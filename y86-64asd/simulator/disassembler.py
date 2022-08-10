# -*- encoding:UTF-8 -*-

# disassembler

import sys
import argparse

from modules import launcher
from modules.assembler import disassembly, Exceptions

class main(launcher.launcher):
    def job(self, args_dict):
        file_in = args_dict["file"]
        file_out = "./a.yps"

        if "--out" in args_dict.keys() or "-o" in args_dict.keys():
            file_out = args_dict["--out"] if "--out" in args_dict.keys() else args_dict["-o"]
        
        bytecode = open(file_in, "br").read()

        disassembler = disassembly.Disassembly(bytecode)
        try:
            asm = disassembler.run()
        except Exceptions.dsmException as dsmExcept:
            dsmExcept.print()
            sys.exit()

        str = ""

        for a in asm:
            str += "\t%s\n" % a

        open(file_out, "w").write(str)

    def help_print(self):
        print("Usage: disassembler.py [FILE] [OPTIONS]...")
        print("Disassembly object FILE to assembly file")
        print("")
        print("example: disassembler.py ./sample.ypo --out ./sample.yps")
        print("")
        print("OPTIONS")
        print(" %-16s %s" % ("-o, --out", "creates an object file with this name. default: a.yps"))
        print(" %-16s %s" % ("-h, --help", "show help"))

main().run()
