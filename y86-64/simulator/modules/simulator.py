# -*- encoding:UTF-8 -*-

import json
import sys

from modules.assembler import disassembly
from modules.cpu import seq, pipe
from modules.http import server

SIMULATOR_VERSION = "0.1 Alpha-20220121r2"

simServer = server.server()

class simulatorServer():
    def __init__(self, serverport = 5500, serverhost = "localhost"):
        self.simulators = {}
        self.id_sequence = 0

        global simServer
        simServer.setServerSettings(serverport = 5500, serverhost = serverhost, servername = "Y86-64+ Simulator")
        simServer.setApplication(self)
        #simServer.accesslog_flag = False
    
    def run(self):
        simServer.run()
    
    @simServer.addJob("/")
    def action_init(self, request_dict, response_dict):
        # load and make simulator display
        simulator_body = open("./view/main.html", "r", encoding = "UTF-8").read().replace("    ", "").replace("\t", "")
        response_body = simulator_body.replace("%simulator-version%", SIMULATOR_VERSION)
        response_body = response_body.replace("%model-script-seq%", open("./view/seq-model.js", "r", encoding = "UTF-8").read())
        response_body = response_body.replace("%model-script-pipe%", open("./view/pipe-model.js", "r", encoding = "UTF-8").read())
    
        response_dict["body"] = response_body
        
        return response_dict
    
    # create session
    @simServer.addJob("/start")
    def action_selectMode(self, request_dict, response_dict):
        memsize = int(request_dict["POST"]["memsize"])
        model = request_dict["POST"]["model"]
        
        id = self.id_sequence
        self.id_sequence += 1
        
        id = "%02X-%02X-%02X-%02X" % (id >> 24 & 0xFF, id >> 16 & 0xFF, id >> 8 & 0xFF, id & 0xFF)
        
        self.simulators[id] = {
            "memsize": memsize, "model": model, "dsmflag": True, "dsmdict": {}, "sim": None, "snapshot": {}
        }
        
        memory_init_str = ""

        for i in range(memsize):
            if i & 7 == 0:
                memory_init_str += "\n&nbsp;%06X: " % (i)
            
            memory_init_str += "00"
        
        memory_init_str = memory_init_str[1:].replace("\n", "&nbsp;<br>\n")
        
        model_html = open("./view/%s-model.html" % (model)).read()
        model_js = open("./view/%s-model.js" % (model)).read()
        
        model_name = { "seq": "sequential", "pipe": "pipeline" }[model]
        
        response_dict["body"] = json.dumps({ "memory": memory_init_str, "model_html": model_html,
                                             "model_js": model_js, "model_name": model_name,
                                             "sim_id": id })
        response_dict["Content-Type"] = "text/json"
        
        return response_dict
    
    # restart session
    @simServer.addJob("/restart")
    def action_restart(self, request_dict, response_dict):
        id = request_dict["POST"]["sim_id"]
        model = ""
        
        if id not in self.simulators.keys():
            response_dict["result"] = "%s 400 Bad Request" % (request_dict["httpv"])
            response_dict["body"] = "ID(%s) does NOT exist." % id
            
            return response_dict
        
        model = self.simulators[id]["model"]
        model_html = open("./view/%s-model.html" % (model), "r", encoding = "UTF-8").read()
        
        response_dict["body"] = json.dumps({ "model_html": model_html, "model_name": model })
        
        return response_dict
    
    # restore session
    @simServer.addJob("/restore")
    def action_restart(self, request_dict, response_dict):
        id = request_dict["POST"]["sim_id"]
        
        if self.simulators[id]["snapshot"]:
            response_dict["body"] = self.resultDictToJSON(self.simulators[id]["snapshot"], id)
            return response_dict
        else:
            response_dict["result"] = "%s 404 Not Found" % (request_dict["httpv"])
            response_dict["body"] = "snapshot is not found"
            return response_dict
    
    @simServer.addJob("/load")
    def action_load(self, request_dict, response_dict):
        obj_file = request_dict["POST"]["obj_file"]
        id = request_dict["POST"]["sim_id"]

        # try read object file
        try:
            program_byte = open(obj_file, "br").read()
        
        # fail
        except:
            print("ERR: %s cannot be read", (obj_file))

            response_dict["result"] = "%s 400 Bad Request" % (request_dict["httpv"])
            response_dict["body"] = "Object code load error.<br>The object file(%s) could not be loaded" % (obj_file)

            self.simulators[id]["sim"] = None

            return response_dict
        
        self.simulators[id]["dsmdict"] = {}

        # create simulator
        if self.simulators[id]["model"] == "seq":
            self.simulators[id]["sim"] = seq.SEQ(program_byte, self.simulators[id]["memsize"])
        
        elif self.simulators[id]["model"] == "pipe":
            self.simulators[id]["sim"] = pipe.PIPE(program_byte, self.simulators[id]["memsize"])
        
        
        # try make disassembly
        try:
            # make disassembly
            disassembler = disassembly.Disassembly(program_byte)
            (pc_point, bytecode_arr, assembly_list) = disassembler.run(isSimulator = True)

            # make disassembly dictionary
            for i in range(len(pc_point)):
                self.simulators[id]["dsmdict"][pc_point[i]] = ("%-20s&nbsp;&nbsp;%s" % (bytecode_arr[i], assembly_list[i])).replace(" ", "&nbsp;")
            
            # make dictionary to string
            # PC = -1
            assembly_str = self.disassemblyDictToStr([-1, -1, -1, -1, -1], id)
            
            self.simulators[id]["dsmflag"] = True
        
        # error
        except:
            assembly_str = "The assembly code was not provided because an error occurred during disassembly."

            self.simulators[id]["dsmflag"] = False

        # make JSON
        response_body = self.resultDictToJSON({}, id)
        self.simulators[id]["snapshot"] = {}

        response_dict["body"] = response_body
        response_dict["Content-Type"] = "text/json"

        return response_dict
    
    @simServer.addJob("/step")
    def action_step(self, request_dict, response_dict):
        id = request_dict["POST"]["sim_id"]
        
        if self.simulators[id]["sim"] == None:
            response_dict["result"] = "%s 400 Bad Request" % (request_dict["httpv"])
            response_dict["body"] = "Step run error.<br>The simulator is not initialized."
            response_dict["Content-Length"] = str(len(response_dict["body"]))

            return response_dict

        simulator_dict = self.simulators[id]["sim"].run()
        
        # make JSON
        response_body = self.resultDictToJSON(simulator_dict, id)
        self.simulators[id]["snapshot"] = simulator_dict
        
        response_dict["body"] = response_body
        response_dict["Content-Type"] = "text/json"

        return response_dict
    
    @simServer.addJob("/run")
    def action_run(self, request_dict, response_dict):
        id = request_dict["POST"]["sim_id"]
        
        if self.simulators[id]["sim"] == None:
            response_dict["result"] = "%s 400 Bad Request" % (request_dict["httpv"])
            response_dict["body"] = "Run error.<br>The simulator is not initialized. "
            response_dict["Content-Length"] = str(len(response_dict["body"]))

            return response_dict

        response_body = ""

        simulator_dict = self.simulators[id]["sim"].run()

        while not(self.simulators[id]["sim"].status & 7):
            simulator_dict = self.simulators[id]["sim"].run()
        
        if self.simulators[id]["model"] == "pipe":
            for i in range(4):
                simulator_dict = self.simulators[id]["sim"].run()

        response_body = self.resultDictToJSON(simulator_dict, id)
        self.simulators[id]["snapshot"] = simulator_dict

        response_dict["Content-Type"] = "text/json"
        response_dict["body"] = response_body
        
        return response_dict
    
    @simServer.addJob("/shutdown")
    def action_shutdown(self, request_dict, response_dict):
        simServer.shutdownFlag = True

        response_dict["body"] = "Simulator has been terminated."
        return response_dict

    def resultDictToJSON(self, in_dict_orig, id):
        in_dict = {}
        pc_list = [] # fetch, decode, ALU, memory, write back
        mem_info = [] # mem mode, address
        
        if in_dict_orig == {}:
            if self.simulators[id]["model"] == "seq":
                in_dict = { "fetch": { "opcode": 0, "rA": 0xF, "rB": 0xF, "const": 0x00, "buff": bytearray(16), "pct": 0,
                                       "jmpc": 0x00, "status": 0, "stallcount": 0 },
                            "decode": { "valA": 0, "valB": 0, "valD": 0, "destE": 0xF, "destM": 0xF, "srcA": 0xF, "srcB": 0xF , "srcD": 0xF,
                                        "DECC": 7, "alumode": 0, "memode": 0, "ccupdate": 0, "opcode": 0, "rA": 0xF, "rB": 0xF, "const": 0 },
                            "alu": { "valE": 0, "ALUCC": 7, "valA": 0, "valB": 0, "alumode": 0, "updateflag": 1 },
                            "memory": { "valE": 0, "valM": 0, "memerr": 0, "memode": 0, "valD": 0 },
                            "wb": { "destE": 0xF, "destM": 0xF, "valE": 0, "valM": 0, "updateflag": 1 }
                            
                           }
            
            elif self.simulators[id]["model"] == "pipe":
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
        
        if self.simulators[id]["model"] == "pipe":
            pc_list = [ in_dict["fetch"]["npct"], in_dict["decode"]["npct"],
                        in_dict["alu"]["npct"], in_dict["memory"]["npct"],
                        in_dict["wb"]["npct"] ]
        
        elif self.simulators[id]["model"] == "seq":
            pc_list = [self.simulators[id]["sim"].nowPC]
        
        mem_info = [in_dict["memory"]["memode"], in_dict["memory"]["valE"]]
        
        # fetch status
        self.simulators[id]["sim"].nowPC
        status = self.simulators[id]["sim"].status
        CC = self.simulators[id]["sim"].ALUCC
        registers = self.simulators[id]["sim"].getRegisters()
        
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
        in_dict["alu"]["ALUCC"] = "%02X (ZF: %d, SF: %d, OF: %d, eql: %d, grt: %d, les: %d)" % (alucc, alucc >> 5, alucc >> 4 & 1,
                                                                                                alucc >> 3 & 1, alucc >> 2 & 1, alucc >> 1 & 1, alucc & 1)
        in_dict["alu"]["DECC"] = "%X (eql: %d, grt: %d, les: %d)" % (decc, decc >> 2, decc >> 1 & 1, decc & 1)
        in_dict["decode"]["DECC"] = "%X (eql: %d, grt: %d, les: %d)" % (decc, decc >> 2, decc >> 1 & 1, decc & 1)
        
        result = {}
        
        for main_key in in_dict.keys():
            for sub_key in in_dict[main_key].keys():
                if sub_key in ["const", "valA", "valB", "valD", "valE", "valM"]:
                    result["%s_%s" % (main_key, sub_key)] = "%016X" % in_dict[main_key][sub_key]
                else:
                    result["%s_%s" % (main_key, sub_key)] = in_dict[main_key][sub_key]
        
        assembly_str = self.disassemblyDictToStr(pc_list, id)
        memory_str = self.memoryArrToStr(registers[0x4], registers[0x5], mem_info, id)
        
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

    def disassemblyDictToStr(self, pc_list, id):
        if self.simulators[id]["dsmflag"] == False:
            return "The assembly code was not provided because an error occurred during disassembly."

        result_list = []
        keys_list = list(self.simulators[id]["dsmdict"].keys())
        keys_list.sort()

        if self.simulators[id]["model"] == "seq":
            for key in keys_list:
                if (key == pc_list[0]):
                    result_list.append("<div class=\"run_seq\">&nbsp;&nbsp;%06X&nbsp;&nbsp;%s</div>\n" % (key, self.simulators[id]["dsmdict"][key]))
                
                else:
                    result_list.append("<div>&nbsp;&nbsp;%06X&nbsp;&nbsp;%s</div>\n" % (key, self.simulators[id]["dsmdict"][key]))
        
        elif self.simulators[id]["model"] == "pipe":
            i = 0
            
            css_list = ["run_pipe_fetch", "run_pipe_decode", "run_pipe_alu", "run_pipe_memory", "run_pipe_wb"]
            
            for key in keys_list:
                if key in pc_list:
                    css = ""
                    for i in range(5):
                        if key == pc_list[i]:
                            css = css_list[i]
                    
                    result_list.append("<div class=\"%s\">&nbsp;&nbsp;%06X&nbsp;&nbsp;%s</div>\n" % (css, key, self.simulators[id]["dsmdict"][key]))
                
                else:
                    result_list.append("<div>&nbsp;&nbsp;%06X&nbsp;&nbsp;%s</div>\n" % (key, self.simulators[id]["dsmdict"][key]))

        return "".join(result_list)
    
    def memoryArrToStr(self, rsp, rbp, mem_info, id):
        memory_str = ""
        str_list = []

        for i in range(len(self.simulators[id]["sim"].memory) >> 3):
            mem_str = "".join(["%02X" % (self.simulators[id]["sim"].memory[(i << 3) + j]) for j in range(8)])

                
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
            
            str_list.append("<br>")
        
        return "".join(str_list)
