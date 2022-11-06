# -*- encoding:UTF-8 -*-

import json
import uuid
import threading
import time
import copy
import os

from modules.assembler import assembly, disassembly, Exceptions
from modules.cpu import seq, pipe
import flask

SIMULATOR_VERSION = "0.3 Alpha-2-20221106r1"

def run(serverport = 5500, serverhost = "localhost"):
    server = flask.Flask("Y86-64+ server")
    examples = os.listdir("./examples")
    examples.sort()
    
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
            
        elif simulator["model"] == "pipe":
            i = 0;
            css_list = ["run_pipe_fetch", "run_pipe_decode", "run_pipe_alu", "run_pipe_memory", "run_pipe_wb"]
            
            for key in keys_list:
                if key in pc_list:
                    css = ""
                    for i in range(5):
                        if key == pc_list[i]:
                            css = css_list[i]
                    
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
    
    def resultDictToJSON(result_orig, simulator_orig):
        result_dict = copy.deepcopy(result_orig)
        simulator = copy.deepcopy(simulator_orig)
        
        for model in result_dict.keys():
            for k in result_dict[model].keys():
                if k in ("valA", "valB", "valE", "const", "valD", "valM"):
                    result_dict[model][k] = "%016X" % result_dict[model][k]
        
        pc_list = []
        if simulator["model"] == "pipe":
            pc_list = [result_dict["fetch"]["npct"], result_dict["decode"]["npct"],
                       result_dict["alu"]["npct"], result_dict["memory"]["npct"],
                       result_dict["wb"]["npct"]]
        
        elif simulator["model"] == "seq":
            pc_list = [simulator["sim"].nowPC]
        
        mem_info = [result_dict["memory"]["memode"], result_orig["memory"]["valE"]]
        
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
        
        for b in result_dict["fetch"]["buff"]:
            fetch_buff.append(" %02X" % (b))
        
        result_dict["fetch"]["buff"] = "".join(fetch_buff)
        
        alucc = result_dict["alu"]["ALUCC"]
        decc = result_dict["decode"]["DECC"]
        
        result_dict["alu"]["ALUCC"] = "%02X (ZF: %d, SF: %d, OF: %d, eql: %d, grt: %d, les: %d)" % (alucc, alucc >> 5, alucc >> 4 & 1,
                                                                                               alucc >> 3 & 1, alucc >> 2 & 1, alucc >> 1 & 1, alucc & 1)
        result_dict["alu"]["DECC"] = "%X (eql: %d, grt: %d, les: %d)" % (decc, decc >> 2, decc >> 1 & 1, decc & 1)
        result_dict["decode"]["DECC"] = "%X (eql: %d, grt: %d, les: %d)" % (decc, decc >> 2, decc >> 1 & 1, decc & 1)
        
        assembly_str = disassemblyDictToStr(pc_list, simulator)
        memory_str = memoryArrToStr(registers[0x4], registers[0x5], mem_info, simulator)
        
        registerRaw = []
        registerInt = []
        
        for i in range(len(registers)):
            registerRaw.append("%016X" % (registers[i]))
            registerInt.append(registers[i] if registers[i] >> 63 != 1 else ((~registers[i] + 1) & 0xFFFFFFFFFFFFFFFF) * -1)
        
        result_dict["object"] = assembly_str
        result_dict["memory_data"] = memory_str
        result_dict["status"] = status_str
        result_dict["flags"] = flags_str
        result_dict["CC"] = cc_str
        
        result_dict["registerRaw"] = registerRaw
        result_dict["registerInt"] = registerInt
        
        return json.dumps(result_dict)
    
    @server.route("/")
    def action_init():
        simulator_body = open("./view/main.html", "r", encoding = "UTF-8").read().replace("    ", "").replace("\t", "")
        response_body = simulator_body.replace("%simulator-version%", SIMULATOR_VERSION)
        response_body = response_body.replace("%model-script-seq%", open("./view/seq-model.js", "r", encoding = "UTF-8").read())
        response_body = response_body.replace("%model-script-pipe%", open("./view/pipe-model.js", "r", encoding = "UTF-8").read())
        
        examples_list = []
        
        for i, example in enumerate(examples):
            examples_list.append("<li onclick=\"loadExampleCode(" + str(i) + ")\"> %s </li>" % example)
        
        response_body = response_body.replace("%example-list%", "\n".join(examples_list))
        
        return response_body, 200
    
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
                               "sim_id": id }), 200
    
    @server.route("/restart", methods=["GET", "POST"])
    def action_restart():
        id = flask.request.form["sim_id"]

        if id not in simulators.keys():
            return "ID(%s) does NOT exist." % id, 400
        
        model = simulators[id]["model"]
        model_html = open("./view/%s-model.html" % (model), "r", encoding = "UTF-8").read()
        
        return flask.jsonify({ "model_html": model_html, "model_name": model }), 200
    
    @server.route("/restore", methods=["GET", "POST"])
    def action_restore():
        id = flask.request.form["sim_id"]
        
        if simulators[id]["snapshot"]:
            response = resultDictToJSON(simulators[id]["snapshot"], simulators[id])
            simulators[id]["life"] = 35
            
            return flask.Response(response, mimetype="application/json"), 200
        
        else:
            return "snapshot was not found", 404
            
    @server.route("/alive", methods=["GET", "POST"])
    def action_alive():
        id = flask.request.form["sim_id"]
        
        if id in simulators.keys():
            simulators[id]["life"] = 35
        else:
            return "Simulator session was destroyed.", 400
        
        return "AOK", 200
    
    def action_load(program_byte, id):
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
        return response_body
        
        #return flask.Response(response_body, "text/application")
    
    @server.route("/step", methods=["GET", "POST"])
    def action_step():
        id = flask.request.form["sim_id"]
        
        if simulators[id]["sim"] == None:
            return "Step run error.<br>The simulator is not initialized.", 400

        simulator_dict = simulators[id]["sim"].run()
        
        # make JSON
        response_body = resultDictToJSON(simulator_dict, simulators[id])
        simulators[id]["snapshot"] = copy.deepcopy(simulator_dict)
        
        return flask.Response(response_body, "application/json"), 200
    
    @server.route("/run", methods=["GET", "POST"])
    def action_run():
        id = flask.request.form["sim_id"]
        
        if simulators[id]["sim"] == None:
            return "Run error.<br>The simulator is not initialized. ", 400

        simulator_dict = simulators[id]["sim"].run()

        while not(simulators[id]["sim"].status & 7):
            simulator_dict = simulators[id]["sim"].run()
        
        if simulators[id]["model"] == "pipe":
            for i in range(4):
                simulator_dict = simulators[id]["sim"].run()

        response_body = resultDictToJSON(simulator_dict, simulators[id])
        simulators[id]["snapshot"] = simulator_dict
        
        return flask.Response(response_body, "application/json"), 200
    
    @server.route("/assembly", methods = ["POST", "GET"])
    def action_assembly():
        data = flask.request.data.decode("UTF-8")
        id, asm = data.split("&", maxsplit=1)
        id = id.split("=")[1]
        asm_list = asm.split("=", maxsplit=1)[1].split("\n")
        
        try:
            assemblyCode = assembly.Assembly(asm_list).run("0")
            return flask.Response(action_load(assemblyCode, id), "application/json"), 200
        except Exceptions.asmException as e:
            return e.toString(), 400
        return ""
            
    @server.route("/example", methods = ["GET", "POST"])
    def action_example():
        example_num = int(flask.request.form["num"])
        example = open("./examples/" + examples[example_num], "r").read()
        return flask.Response(example, "text/plain"), 200
    
    @server.route("/shutdown", methods=["GET", "POST"])
    def action_shutdown():
        id = flask.request.form["sim_id"]
        
        if id not in simulators.keys():
            return "Run error.<br>The simulator is not initialized. ", 400
        
        del simulators[id]
        
        return "This session was terminated.", 200
        
    server.run(port = serverport, host = serverhost)