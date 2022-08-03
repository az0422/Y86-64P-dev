# -*- encoding:UTF-8 -*-

import json
import uuid
import threading
import time
import copy
import os

from modules.assembler import disassembly
from modules.cpu import seq, pipe
import flask

SIMULATOR_VERSION = "0.1 Alpha-20220204r1"

def run(serverport = 5500, serverhost = "localhost"):
    server = flask.Flask("Y86-64+ server")
    
    simulators = {}
    
    def disassemblyDictToStr(pc_list, simulator):
        if simulator["dsmflag"] == False:
            return "Disassemble was failure."
        
        result_list = []
        keys_list = list(simulator["dsmdict"].keys())
        keys_list.sort()
        
        if simulator["model"] == "seq":
            for key in keys_list:
                if (key == pc_list[0]):
                    result_list.append("<div class=\"run_seq\">&nbsp;&nbsp;%06X&nbsp;&nbsp;%s</div>\n" % (key, simulator["dsmdict"][key]))
                    
                else:
                    result_list.append("<div>&nbsp;&nbsp;%06X&nbsp;&nbsp;%s</div>\n" % (key, simulator["dsmdict"][key]))
            
        elif simulator["mode"] == "pipe":
            i = 0;
            css_list = ["run_pipe_fetch", "run_pipe_decode", "run_pipe_alu", "run_pipe_memory", "run_pipe_wb"]
            
            for key in keys_list:
                if key in pc_list:
                    css = ""
                    
                    for i in range(5):
                        if key == pc_list[i]:
                            css == css_list[i]
                    
                    result_list.append("<div class=\"%s\">&nbsp;&nbsp;%06X&nbsp;&nbsp;%s</div>\n" % (css, key, simulator["dsmdict"][key]))
                    
                else:
                    result_list.append("<div>&nbsp;&nbsp;%06X&nbsp;&nbsp;%s</div>\n" % (key, simulator["dsmdict"][key]))
        
        return "".join(result_list)
        
    def memoryArrToStr(rsp, rbp, mem_info, simulator):
        str_list = []

        for i in range(len(simulator["sim"].memory) >> 3):
            mem_str = "".join(["%02X" % (simulator["sim"].memory[(i << 3) + j]) for j in range(8)])

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
    
    def resultDictToJSON(result, simulator):
        result_dict = copy.deepcopy(result)
        
        pc_list = []
        if simulator["model"] == "pipe":
            pc_list = [result["fetch"]["npct"], result["decode"]["npct"],
                       result["alu"]["npct"], result["memory"]["npct"],
                       result["wb"]["npct"]]
        
        elif simulator["model"] == "seq":
            pc_list = [simulator["sim"].nowPC]
        
        mem_info = [result["memory"]["memode"], result["memory"]["valE"]]
        
        status = simulator["sim"].status
        CC = simulator["sim"].ALUCC
        registers = simulator["sim"].getRegisters()
        
        flag_str = ("N", "Y")
        status_str = "%d (NOP: %s, MEM ERR: %s, HALT: %s, INS ERR: %s, AOK: %s)" % (
                     status, flag_str[status >> 3], flag_str[status >> 2 & 1], 
                     flag_str[status >> 1 & 1], flag_str[status & 1],
                     ("Y", "N")[int(bool(status))])
        
        flags = CC >> 3
        cc = CC & 7
        
        flags_str = "%X (ZF: %d, SF: %d, OF: %d)" % (flags, flags >> 2, flags >> 1 & 1, flags & 1)
        cc_str = "%X (eql: %d, grt: %d, les: %d)" % (cc, cc >> 2, cc >> 1 & 1, cc & 1)
        
        fetch_buff = [] 
        
        for b in result["fetch"]["buff"]:
            fetch_buff.append(" %02X" % (b))
        
        result["fetch"]["buff"] = "".join(fetch_buff)
        
        alucc = result["alu"]["ALUCC"]
        decc = result["decode"]["DECC"]
        
        result["alu"]["ALUCC"] = "%02X (ZF: %d, SF: %d, OF: %d, eql: %d, grt: %d, les: %d)" % (alucc, alucc >> 5, alucc >> 4 & 1,
                                                                                               alucc >> 3 & 1, alucc >> 2 & 1, alucc >> 1 & 1, alucc & 1)
        result["alu"]["DECC"] = "%X (eql: %d, grt: %d, les: %d)" % (decc, decc >> 2, decc >> 1 & 1, decc & 1)
        result["decode"]["DECC"] = "%X (eql: %d, grt: %d, les: %d)" % (decc, decc >> 2, decc >> 1 & 1, decc & 1)
        
        assembly_str = disassemblyDictToStr(pc_list, simulator)
        memory_str = memoryArrToStr(registers[0x4], registers[0x5], mem_info, simulator)
        
        registerRaw = []
        registerInt = []
        
        for i in range(len(registers)):
            registerRaw.append("%016X" % (registers[i]))
            registerInt.append(registers[i] if registers[i] >> 63 != 1 else ((~registers[i] + 1) & 0xFFFFFFFFFFFFFFFF) * -1)
        
        result["object"] = assembly_str
        result["memory"] = memory_str
        result["status"] = status_str
        result["flags"] = flags_str
        result["CC"] = cc_str
        
        result["registerRaw"] = registerRaw
        result["registerInt"] = registerInt
        
        return json.dumps(result)
    
    @server.route("/")
    def action_init():
        simulator_body = open("./view/main.html", "r", encoding = "UTF-8").read().replace("    ", "").replace("\t", "")
        response_body = simulator_body.replace("%simulator-version%", SIMULATOR_VERSION)
        response_body = response_body.replace("%model-script-seq%", open("./view/seq-model.js", "r", encoding = "UTF-8").read())
        response_body = response_body.replace("%model-script-pipe%", open("./view/pipe-model.js", "r", encoding = "UTF-8").read())
        
        return response_body
    
    @server.route("/start", methods=["GET", "POST"])
    def action_selectMode():
        memsize = int(flask.request.form["memsize"])
        model = flask.request.form["model"]
        
        id = str(uuid.uuid4())
        
        simulators[id] = {
            "memsize": memsize, "model": model, "life": 35, "dsmflag": True, "dsmdict": {}, "sim": None, "snapshot": {}
        }
        
        memory_init = []

        for i in range(memsize):
            if i & 7 == 0:
                memory_init.append("\n&nbsp;%06X: " % (i))
            
            memory_init.append("00")
        
        memory_init = "".join(memory_init)[1:].replace("\n", "<br>")
        
        model_html = open("./view/%s-model.html" % (model)).read()
        model_js = open("./view/%s-model.js" % (model)).read()
        
        model_name = { "seq": "sequential", "pipe": "pipeline" }[model]
        
        return flask.jsonify({ "memory": memory_init, "model_html": model_html,
                               "model_js": model_js, "model_name": model_name,
                               "sim_id": id })
    
    @server.route("/restart", methods=["GET", "POST"])
    def action_restart():
        id = flask.request.form["sim_id"]

        if id not in simulators.keys():
            return flask.make_response("ID(%s) does NOT exist." % id, 400)
        
        model = simulators[id]["model"]
        model_html = open("./view/%s-model.html" % (model), "r", encoding = "UTF-8").read()
        
        return flask.jsonify({ "model_html": model_html, "model_name": model })
    
    @server.route("/restore", methods=["GET", "POST"])
    def action_restore():
        id = flask.request.form["sim_id"]
        
        if simulators[id]["snapshot"]:
            response = resultDictToJSON(simulators[id]["snapshot"], simulators[id])
            simulators[id]["life"] = 35
            
            return flask.Response(response, mimetype="application/json")
        
        else:
            return flask.make_response("snapshot was not found", 404)
            
    @server.route("/alive", methods=["GET", "POST"])
    def action_alive():
        id = flask.request.form["sim_id"]
        
        if id in simulators.keys():
            self.simulators[id]["life"] = 35
        else:
            return flask.make_response("Simulator session was destroyed.", 400)
        
        return "AOK"
    
    @server.route("/load", methods=["GET", "POST"])
    def action_load():
        obj_file = flask.request.form["obj_file"]
        id = flask.request.form["sim_id"]

        if os.path.isfile(obj_file):
            program_byte = open(obj_file, "br").read()
            
        else:
            print("ERR: %s cannot be read", (obj_file))
            
            simulators[id]["sim"] = None
            
            return flask.make_response("Object code load error.<br>The object file(%s) could not be loaded" % (obj_file), 400)
        
        simulators[id]["dsmdict"] = {}

        # create simulator
        if simulators[id]["model"] == "seq":
            simulators[id]["sim"] = seq.SEQ(program_byte, simulators[id]["memsize"])
        
        elif simulators[id]["model"] == "pipe":
            simulators[id]["sim"] = pipe.PIPE(program_byte, simulators[id]["memsize"])
        
        # try make disassembly
        try:
            # make disassembly
            disassembler = disassembly.Disassembly(program_byte)
            (pc_point, bytecode_arr, assembly_list) = disassembler.run(isSimulator = True)

            # make disassembly dictionary
            for i in range(len(pc_point)):
                simulators[id]["dsmdict"][pc_point[i]] = ("%-20s&nbsp;&nbsp;%s" % (bytecode_arr[i], assembly_list[i])).replace(" ", "&nbsp;")
            
            
            simulators[id]["dsmflag"] = True
        
        # error
        except:
            simulators[id]["dsmflag"] = False
            
        # make JSON
        response_body = resultDictToJSON(simulators[id]["sim"].getDefaultResult(), simulators[id])
        simulators[id]["snapshot"] = {}

        return flask.Response(response_body, "text/application")
    
    @server.route("/step", methods=["GET", "POST"])
    def action_step():
        id = flask.request.form["sim_id"]
        
        if simulators[id]["sim"] == None:
            return flask.make_response("Step run error.<br>The simulator is not initialized.", 400)

        simulator_dict = simulators[id]["sim"].run()
        
        # make JSON
        response_body = resultDictToJSON(simulator_dict, simulators[id])
        simulators[id]["snapshot"] = simulator_dict
        
        return flask.Response(response_body, "application/json")
    
    @server.route("/run", methods=["GET", "POST"])
    def action_run(self, request_dict, response_dict):
        id = flask.request.form["sim_id"]
        
        if simulators[id]["sim"] == None:
            return flask.make_response("Run error.<br>The simulator is not initialized. ", 400)

        simulator_dict = self.simulators[id]["sim"].run()

        while not(simulators[id]["sim"].status & 7):
            simulator_dict = simulators[id]["sim"].run()
        
        if simulators[id]["model"] == "pipe":
            for i in range(4):
                simulator_dict = simulators[id]["sim"].run()

        response_body = resultDictToJSON(simulator_dict, simulators[id])
        simulators[id]["snapshot"] = simulator_dict

        response_dict["Content-Type"] = "text/json"
        response_dict["body"] = response_body
        
        return response_dict
    
    server.run(port = serverport, host = serverhost)


'''
    
    @simServer.addJob("/shutdown")
    def action_shutdown(self, request_dict, response_dict):
        simServer.shutdownFlag = True
        self.aliveChecker.shutdown()

        response_dict["body"] = "Simulator has been terminated."
        return response_dict
    
    @simServer.addJob("/manager")
    def action_manager(self, request_dict, response_dict):
        view_html = open("./view/manager.html", "r").read()
        
        response_dict["body"] = view_html
        return response_dict
    
    @simServer.addJob("/mgrdata")
    def action_mgrdata(self, request_dict, response_dict):
        result_list = []
        
        lock.acquire()
        id_list = self.simulators.keys()
        lock.release()
        
        for id in id_list:
            try:
                memsize = self.simulators[id]["memsize"]
                model = self.simulators[id]["model"]
                life = self.simulators[id]["life"]
                
                if memsize >> 40:
                    memsize = str(memsize >> 40) + "TB"
                elif memsize >> 30:
                    memsize = str(memsize >> 30) + "GB"
                elif memsize >> 20:
                    memsize = str(memsize >> 20) + "MB"
                elif memsize >> 10:
                    memsize = str(memsize >> 10) + "KB"
                else:
                    memsize = str(memsize) + "B"
                
                result_list.append({ "uuid": id, "memsize": memsize, "model": { "seq": "Sequential", "pipe": "Pipeline" }[model], "life": str(life) })
            except:
                print("INFO: ID " + id + " was already closed")
        
        response_dict["body"] = json.dumps({ "data": result_list })
        
        return response_dict
    
    @simServer.addJob("/kill")
    def action_kill(self, request_dict, response_dict):
        id = request_dict["POST"]["sim_id"]
        
        lock.acquire()
        del self.simulators[id]
        lock.release()
        
        return response_dict

# killer
class checkAliveThread(threading.Thread):
    def __init__(self, simulators):
        super().__init__()
        self.simulators = simulators
        self.shutdown_flag = False
    
    def run(self):
        while True:
            lock.acquire()
            id_list = list(self.simulators.keys())
            lock.release()
            
            for id in id_list:
                try:
                    if self.simulators[id]["life"] <= 0:
                        del self.simulators[id]
                    else:
                        self.simulators[id]["life"] -= 1
                except:
                    print("INFO: ID " + id + " was already closed")
                
            for i in range(12):
                time.sleep(5)
                
                if self.shutdown_flag:
                    return
    
    def shutdown(self):
        self.shutdown_flag = True
   '''     