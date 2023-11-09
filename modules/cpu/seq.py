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

        self.status |= fetch_dict["result"]["status"]
        self.registerFile.writePC(fetch_dict["result"]["nxpc"])

        decode_dict = decode.decode(fetch_dict["result"], self.registerFile)
        alu_dict = alu.ALU(decode_dict["result"])

        if alu_dict["buff"]["ccupdate"]:
            self.ALUCC = alu_dict["result"]["cc"]

        destE_update = alu_dict["buff"]["decc"] & self.ALUCC
        alu_dict["result"]["destE update"] = destE_update

        memory_in_dict = alu_dict["result"].copy()

        for key in alu_dict["pass"].keys():
            memory_in_dict[key] = alu_dict["pass"][key]

        memory_dict = memory.memory(memory_in_dict, self.memory)

        wb_in_dict = memory_dict["result"].copy()

        for key in memory_dict["pass"].keys():
            wb_in_dict[key] = memory_dict["pass"][key]

        wb_dict = writeback.writeback(wb_in_dict, self.registerFile)

        return {"fetch": fetch_dict, "decode": decode_dict, "alu": alu_dict, "memory": memory_dict, "wb": wb_dict}

