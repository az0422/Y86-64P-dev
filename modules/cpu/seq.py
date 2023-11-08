# -*- encoding:UTF-8 -*-
from modules.cpu.parts import register, fetch, decode, alu, memory, writeback
from modules.cpu import cpumodel

class SEQ(cpumodel.CPUModel):
    def __init__(self, program, memsize):
        super().__init__(program, memsize)
        
        self.model = "seq"
    
    def getDefaultResult(self):
        return {}
    
    def run(self):
        pc = self.registerFile.readPC()

        fetch_dict = fetch.fetch(self.memory, pc)

        self.status |= fetch_dict["status"]

        decode_dict = decode.decode(fetch_dict["result"], self.registerFile)
        alu_dict = alu.ALU(decode_dict["result"])

        if alu_dict["buff"]["ccupdate"]:
            self.ALUCC = alu_dict["result"]["cc"]

        destE_update = alu_dict["buff"]["decc"] & self.ALUCC
        alu_dict["result"]["destE update"] = destE_update

        print(alu_dict)

