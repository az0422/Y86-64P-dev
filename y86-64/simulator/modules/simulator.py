# -*- encoding:UTF-8 -*-

from modules.assembler import disassembly
from modules.cpu import seq, pipe
from modules.http import server

import json
import sys

SIMULATOR_VERSION = "0.1 Alpha-20211028r0"

class sServer(server.server):
    def accesslog_print(self, addr_str, header_dict):
        pass

simServer = sServer()

class simulatorServer():
    def __init__(self, model, memsize, obj_file, serverport = 5500, serverhost = "localhost"):
        self.model = model
        self.memsize = memsize
        self.obj_file = obj_file
        self.simulator = None
        self.disassemblySuccess = True
        self.disassembly_dict = {}

        global simServer
        simServer.setServerSettings(serverport = 5500, serverhost = serverhost, servername = "Y86-64+ Simulator")
        simServer.setApplication(self)
    
    def run(self):
        simServer.run()
    
    @simServer.addJob("/")
    def action_init(self, request_dict, response_dict):
        # destroy simulator
        self.simulator = None

        # load and make simulator display
        simulator_body = open("./view/main.html", "r", encoding = "UTF-8").read().replace("    ", "").replace("\t", "")
        simulator_model = open("./view/%s-model.html" % (self.model), "r", encoding = "UTF-8").read().replace("    ", "").replace("\t", "")
        simulator_script = open("./view/%s-model.js" % (self.model), "r", encoding = "UTF-8").read().replace("    ", "").replace("\t", "")

        memory_init_str = ""

        for i in range(self.memsize):
            if i & 7 == 0:
                memory_init_str += "\n&nbsp;%06X: " % (i)
            
            memory_init_str += "00"
        
        memory_init_str = memory_init_str[1:].replace("\n", "&nbsp;<br>\n")

        response_body = simulator_body.replace("%cpu-model%", simulator_model)
        response_body = response_body.replace("%model-script%", simulator_script)
        response_body = response_body.replace("%file-path%", self.obj_file)
        response_body = response_body.replace("%simulator-version%", SIMULATOR_VERSION)
        response_body = response_body.replace("%model-name%", self.model)
        response_body = response_body.replace("%memory%", memory_init_str)
    
        response_dict["body"] = response_body
        
        return response_dict

    @simServer.addJob("/load")
    def action_load(self, request_dict, response_dict):
        obj_file = request_dict["body"]["obj_file"]

        # try read object file
        try:
            program_byte = open(obj_file, "br").read()
        
        # fail
        except:
            print("ERR: %s cannot be read", (obj_file))

            response_dict["result"] = "%s 400 Bad Request" % (request_dict["header"]["request"][2])
            response_dict["body"] = "Object code load error.<br>The object file(%s) could not be loaded" % (obj_file)

            self.simulator = None

            return response_dict
        
        self.disassembly_dict = {}

        # create simulator
        if self.model == "seq":
            self.simulator = seq.SEQ(program_byte, self.memsize)
        
        elif self.model == "pipe":
            self.simulator = pipe.PIPE(program_byte, self.memsize)
        
        
        # try make disassembly
        try:
            # make disassembly
            disassembler = disassembly.Disassembly(program_byte)
            (pc_point, bytecode_arr, assembly_list) = disassembler.run(isSimulator = True)

            # make disassembly dictionary
            for i in range(len(pc_point)):
                self.disassembly_dict[pc_point[i]] = ("%-20s&nbsp;&nbsp;%s" % (bytecode_arr[i], assembly_list[i])).replace(" ", "&nbsp;")
            
            # make dictionary to string
            # PC = -1
            assembly_str = self.disassemblyDictToStr([-1, -1, -1, -1, -1])

            self.disassemblySuccess = True
        
        # error
        except:
            assembly_str = "The assembly code was not provided because an error occurred during disassembly."

            self.disassemblySuccess = False

        # make memory to string
        memory_str = self.memoryArrToStr(0, 0, [0, 0])

        # make JSON
        response_body = self.resultDictToJSON({})

        response_dict["body"] = response_body
        response_dict["Content-Type"] = "text/json"

        return response_dict
    
    @simServer.addJob("/step")
    # run step
    def action_step(self, request_dict, response_dict):
        if self.simulator == None:
            response_dict["result"] = "%s 400 Bad Request" % (request_dict["header"]["request"][2])
            response_dict["body"] = "Step run error.<br>The simulator is not initialized."
            response_dict["Content-Length"] = str(len(response_dict["body"]))

            return response_dict

        simulator_dict = self.simulator.run()
        
        # make JSON
        response_body = self.resultDictToJSON(simulator_dict)
        
        response_dict["body"] = response_body
        response_dict["Content-Type"] = "text/json"

        return response_dict
    
    @simServer.addJob("/run")
    def action_run(self, request_dict, response_dict):
        if self.simulator == None:
            response_dict["result"] = "%s 400 Bad Request" % (request_dict["header"]["request"][2])
            response_dict["body"] = "Run error.<br>The simulator is not initialized. "
            response_dict["Content-Length"] = str(len(response_dict["body"]))

            return response_dict

        response_body = ""

        simulator_dict = self.simulator.run()

        while not(self.simulator.status & 7):
            simulator_dict = self.simulator.run()
        
        if self.model == "pipe":
            for i in range(4):
                simulator_dict = self.simulator.run()

        response_body = self.resultDictToJSON(simulator_dict)

        response_dict["Content-Type"] = "text/json"
        response_dict["body"] = response_body
        
        return response_dict
    
    @simServer.addJob("/shutdown")
    def action_shutdown(self, request_dict, response_dict):
        simServer.shutdownFlag = True

        response_dict["body"] = "Simulator has been terminated."
        return response_dict

    def resultDictToJSON(self, in_dict_orig):
        in_dict = {}
        pc_list = [] # fetch, decode, ALU, memory, write back
        mem_info = [] # mem mode, address
        
        if in_dict_orig == {}:
            if self.model == "seq":
                in_dict = { "fetch": { "opcode": 0, "rA": 0xF, "rB": 0xF, "const": 0x00, "buff": bytearray(16), "pct": 0,
                                       "jmpc": 0x00, "status": 0, "stallcount": 0 },
                            "decode": { "valA": 0, "valB": 0, "valD": 0, "destE": 0xF, "destM": 0xF, "srcA": 0xF, "srcB": 0xF , "srcD": 0xF,
                                        "DECC": 7, "alumode": 0, "memode": 0, "ccupdate": 0, "opcode": 0, "rA": 0xF, "rB": 0xF, "const": 0 },
                            "alu": { "valE": 0, "ALUCC": 7, "valA": 0, "valB": 0, "alumode": 0, "updateflag": 1 },
                            "memory": { "valE": 0, "valM": 0, "memerr": 0, "memode": 0, "valD": 0 },
                            "wb": { "destE": 0xF, "destM": 0xF, "valE": 0, "valM": 0, "updateflag": 1 }
                            
                           }
            
            elif self.model == "pipe":
                in_dict = { "fetch": { "opcode": 0x00, "rA": 0xF, "rB": 0xF, "const": 0x00, "pct": 0x00,
                                      "jmpc": 0x00, "buff": bytearray(16), "npct": -1 },
                            "decode": { "valA": 0x00, "valB": 0x00, "valD": 0x00, "alumode": 0x0,
                                        "memode": 0x0, "DECC": 0x7, "ccupdate": 0x0,
                                        "srcA": 0xF, "srcB": 0xF, "srcD": 0xF, "destE": 0xF, "destM": 0xF, "npct": -1, 
                                        "fwd_alu": "None", "fwd_mem": "None", "fwd_malu": "None" },
                            "alu": { "valE": 0x00, "valD": 0x00, "memode": 0x0, "destE": 0xF, "destM": 0xF,
                                     "updateflag": 0x1, "npct": -1, "ALUCC": 7, "valA": 0, "valB": 0,
                                     "alumode": 0, "DECC": 7,
                                     "destE": 0xF, "destM": 0xF, "memode": 0 },
                            "memory": { "valE": 0x00, "valM": 0x00, "destE": 0xF, "destM": 0xF, "updateflag": 0x1,
                                        "memode": 0x0, "npct": -1, "valD": 0 },
                            "wb": { "destE": 0xF, "destM": 0xF, "valE": 0, "valM": 0, "updateflag": 1, "npct": -1 },
                            "fwdu": { "alu": "None", "mem": "None", "malu": "None" }
                          }
        
        else:
            for mnkey in in_dict_orig.keys():
                in_dict[mnkey] = { }
                
                for mkey in in_dict_orig[mnkey].keys():
                    in_dict[mnkey][mkey] = in_dict_orig[mnkey][mkey]
        
        if self.model == "pipe":
            pc_list = [ in_dict["fetch"]["npct"], in_dict["decode"]["npct"], in_dict["alu"]["npct"], in_dict["memory"]["npct"], in_dict["wb"]["npct"] ]
        
        elif self.model == "seq":
            pc_list = [self.simulator.nowPC]
        
        mem_info = [in_dict["memory"]["memode"], in_dict["memory"]["valE"]]
        
        # fetch status
        self.simulator.nowPC
        status = self.simulator.status
        CC = self.simulator.ALUCC
        registers = self.simulator.getRegisters()
        
        # status
        # w: memory overflow, x: nop, y: halt, z: err
        status_str = "%d (NOP: %s, MEM ERR: %s, HALT: %s, INS ERR: %s, AOK: %s)" % (status,
                     ["N", "Y"][status >> 3], ["N", "Y"][status >> 2 & 1], ["N", "Y"][status >> 1 & 1],
                     ["N", "Y"][status & 1], ["Y", "N"][int(bool(status))])

        # flags and ALU CC
        flags = CC >> 3
        cc = CC & 7

        flags_str = "%X (ZF: %d, SF: %d, OF: %d)" % (flags, flags >> 2, flags >> 1 & 1, flags & 1)
        cc_str = "%X (eql: %d, grt: %d, les: %d)" % (cc, cc >> 2, cc >> 1 & 1, cc & 1)
        
        fetch_buff = "%02X" % (in_dict["fetch"]["buff"][0])

        for b in in_dict["fetch"]["buff"][1:]:
            fetch_buff += " %02X" % (b)
        
        alucc = in_dict["alu"]["ALUCC"]
        decc = in_dict["decode"]["DECC"]
        in_dict["fetch"]["buff"] = fetch_buff
        in_dict["alu"]["ALUCC"] = "%02X (ZF: %d, SF: %d, OF: %d, eql: %d, grt: %d, les: %d)" % (alucc, alucc >> 5, alucc >> 4 & 1, alucc >> 3 & 1, alucc >> 2 & 1, alucc >> 1 & 1, alucc & 1)
        in_dict["alu"]["DECC"] = "%X (eql: %d, grt: %d, les: %d)" % (decc, decc >> 2, decc >> 1 & 1, decc & 1)
        in_dict["decode"]["DECC"] = "%X (eql: %d, grt: %d, les: %d)" % (decc, decc >> 2, decc >> 1 & 1, decc & 1)
        
        result = {}
        
        for main_key in in_dict.keys():
            for sub_key in in_dict[main_key].keys():
                if sub_key in ["const", "valA", "valB", "valD", "valE", "valM"]:
                    result["%s_%s" % (main_key, sub_key)] = "%016X" % in_dict[main_key][sub_key]
                else:
                    result["%s_%s" % (main_key, sub_key)] = in_dict[main_key][sub_key]
        
        assembly_str = self.disassemblyDictToStr(pc_list)
        memory_str = self.memoryArrToStr(registers[0x4], registers[0x5], mem_info)
        
        result["object"] = assembly_str
        result["memory"] = memory_str
        result["status"] = status_str
        result["flags"] = flags_str
        result["CC"] = cc_str
        
        # get register data
        result["registerRaw"] = []
        result["registerInt"] = []

        for i in range(len(registers)):
            result["registerRaw"].append("%016X" % (registers[i]))
            result["registerInt"].append(registers[i] if registers[i] >> 63 != 1 else ((~registers[i] + 1) & 0xFFFFFFFFFFFFFFFF) * -1)
        
        # make JSON return
        response_body = json.dumps(result)

        return response_body

    def disassemblyDictToStr(self, pc_list):
        if self.disassemblySuccess == False:
            return "The assembly code was not provided because an error occurred during disassembly."

        result = ""
        keys_list = list(self.disassembly_dict.keys())
        keys_list.sort()

        if self.model == "seq":
            for key in keys_list:
                if (key == pc_list[0]):
                    result += "<div class=\"run_seq\">&nbsp;&nbsp;%06X&nbsp;&nbsp;%s</div>\n" % (key, self.disassembly_dict[key])
                
                else:
                    result += "<div>&nbsp;&nbsp;%06X&nbsp;&nbsp;%s</div>\n" % (key, self.disassembly_dict[key])
        
        elif self.model == "pipe":
            i = 0
            
            css_list = ["run_pipe_fetch", "run_pipe_decode", "run_pipe_alu", "run_pipe_memory", "run_pipe_wb"]
            
            for key in keys_list:
                if key in pc_list:
                    css = ""
                    for i in range(5):
                        if key == pc_list[i]:
                            css = css_list[i]
                    
                    result += "<div class=\"%s\">&nbsp;&nbsp;%06X&nbsp;&nbsp;%s</div>\n" % (css, key, self.disassembly_dict[key])
                
                else:
                    result += "<div>&nbsp;&nbsp;%06X&nbsp;&nbsp;%s</div>\n" % (key, self.disassembly_dict[key])

        return result
    
    def memoryArrToStr(self, rsp, rbp, mem_info):
        memory_str = ""
        str_list = []

        for i in range(len(self.simulator.memory) >> 3):
            mem_str = ""
            
            for j in range(8):
                mem_str += "%02X" % (self.simulator.memory[(i << 3) + j])
                
            str_list.append("")
            str_list[-1] = "&nbsp;%06X: %s&nbsp;" % (i << 3, mem_str)
            
            # read
            if mem_info[0] == 1 and mem_info[1] >> 3 == i:
                str_list[-1] = "<span class=\"read_point\"> %s R&nbsp;</span>" % (str_list[-1])
            
            # write
            elif mem_info[0] == 2 and mem_info[1] >> 3 == i:
                str_list[-1] = "<span class=\"write_point\"> %s W&nbsp;</span>" % (str_list[-1])
            
            # stack point
            if rsp >> 3 == i:
                str_list[-1] = "<span class=\"rsp_point\">%s RSP&nbsp;</span>" % (str_list[-1])

            # stack base point
            if rbp >> 3 == i:
                str_list[-1] = "<span class=\"rbp_point\"> %s RBP&nbsp;</span>" % (str_list[-1])
                
        for str in str_list:
            memory_str += str + "<br>"
        
        return memory_str
