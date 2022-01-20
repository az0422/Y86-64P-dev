# -*- encoding:UTF-8 -*-

# assembler

import sys

from modules import launcher
from modules.assembler import assembly, Exceptions

class main(launcher.launcher):
    def job(self, args_dict):
        file_in = args_dict["file"]
        file_out = "./a.ypo"
        warn_level = "0"
        
        if "--out" in args_dict.keys() or "-o" in args_dict.keys():
            file_out = args_dict["--out"] if "--out" in args_dict.keys() else args_dict["-o"]
        
        if "--warn" in args_dict.keys() or "-w" in args_dict.keys():
            warn_level = args_dict["--warn"] if "--out" in args_dict.keys() else args_dict["-w"]
        
        asm_list = open(file_in, "r", encoding="UTF-8").read().split("\n")

        assembler = assembly.Assembly(asm_list)
        try:
            bytecode = assembler.run(warn_level)
        except Exceptions.asmException as asmExcept:
            asmExcept.print()
            sys.exit()

        open(file_out, "bw").write(bytecode)

    def help_print(self):
        print("Usage: assembler.py [FILE] [OPTIONS]...")
        print("Assembly FILE to object file")
        print("")
        print("example: assembler.py ./sample.yps --out ./sample.ypo")
        print("")
        print("OPTIONS")
        print(" %-16s %s" % ("-o, --out", "creates an object file with this name. default: a.ypo"))
        print(" %-16s %s" % ("-w, --warn", "warning level to print. default: 0, value: 0, 1"))
        print(" %-16s %s" % ("-h, --help", "show help"))

main().run()
