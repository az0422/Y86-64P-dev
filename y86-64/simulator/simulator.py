# -*- encoding:UTF-8 -*-

# 시뮬레이터 실행기
#
# 시뮬레이터는 기본적으로 HTTP 프로토콜을 이용한 1:1 클라이언트 - 서버 모델을 사용한다

import sys

from modules import launcher, config, simulator

class main(launcher.launcher):
    def args_set(self):
        return False
    
    def job(self, args_dict):
        configdata = config.config("config/settings.conf").read()
        memsize = 512
        serverport = 5500
        serverhost = ""

        # fetch from configuration
        memsize = configdata["General"]["memsize"] if "memsize" in configdata["General"].keys() else 512
        serverport = int(configdata["Server"]["port"]) if "port" in configdata["Server"].keys() else 5500
        serverhost = configdata["Server"]["host"] if "host" in configdata["Server"].keys() else ""
        
        suffix = memsize[-1].lower()
        obj_file = ""
        model = "seq"
        
        # kB
        if suffix == "k":
            memsize = int(memsize[:-1]) * 1024

        # MB
        elif suffix == "m":
            memsize = int(memsize[:-1]) * 1024 * 1024

        # GB
        elif suffix == "g":
            memsize = int(memsize[:-1]) * 1024 * 1024 * 1024

        # convert to integer
        else:
            try:
                memsize = int(memsize)
            except:
                print("ERR: value error of memory size(memsize) in config file")
                sys.exit()

        # open file
        if "file" in args_dict.keys():
            obj_file = args_dict["file"]
        
        # select model
        if "--model" in args_dict.keys() or "-m" in args_dict.keys():
            model = args_dict["--model"] if "--model" in args_dict.keys() else args_dict["-m"]
            
            if model not in ("seq", "pipe"):
                self.help_print()
                sys.exit()
        
        # apply memsize
        memsize = memsize - (memsize & 7) + 8

        # greater than 512
        if memsize < 512:
            memsize = 512

        # make server and run
        sim = simulator.simulatorServer(model, memsize, obj_file, serverport = serverport, serverhost = serverhost)
        sim.run()
        
        sys.exit()


    def help_print(self):
        print("Usage: simulator [FILE]... [OPTIONS]...")
        print("Simulator read FILE and simulating on web browser")
        print("")
        print("example: simulator.py ./example.ybin --model seq")
        print("")
        print("FILE (optional)")
        print("Y86-64 object file. Simulator pre-enters on simulator page in object file name field.")
        print("")
        print("")
        print("OPTIONS")
        print(" %-16s %s" % ("-m, --model", "chooes cpu model. seq is sequential mode, pipe is pipeline model, default is seq"))
        print(" %-16s %s" % ("-h, --help", "show help"))

main().run()