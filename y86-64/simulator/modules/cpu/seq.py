# -*- encoding:UTF-8 -*-
from modules.cpu.parts import register, fetch, decode, alu, memory, writeback
from modules.cpu import cpumodel

class SEQ(cpumodel.CPUModel):
    def run(self):
        pc = self.registerFile.readPC()
        self.nowPC = pc
        
        if pc >= len(self.memory):
            self.status |= 4
        
        # --- fetch ---
        fetch_dict = fetch.fetch(self.memory, pc)
        
        self.status = self.status & 7

        # status update
        self.status |= fetch_dict["status"]
        
        # PC pre-update
        if not(self.status & 0x7):
            self.registerFile.writePC(fetch_dict["pct"])
        
        # --- decode --- 
        decode_dict = decode.decode(fetch_dict, self.registerFile)
        
        # --- ALU ---
        alu_dict = alu.ALU(decode_dict)
        
        # CC Update
        if decode_dict["ccupdate"]:
            self.ALUCC = alu_dict["ALUCC"]
        
        updateflag = self.ALUCC & decode_dict["DECC"]
        alu_dict["updateflag"] = updateflag
        
        # --- memory ---
        mem_in_dict = { "valD": decode_dict["valD"], "memode": decode_dict["memode"], "valE": alu_dict["valE"] }

        mem_dict = memory.memory(mem_in_dict, self.memory)
        mem_dict["valD"] = decode_dict["valD"]
        
        # --- write back ---
        wb_in_dict = { "valE": mem_dict["valE"], "valM": mem_dict["valM"], "destE": decode_dict["destE"],
                       "destM": decode_dict["destM"], "updateflag": updateflag }
        
        wb_dict = writeback.writeback(wb_in_dict, self.registerFile)

        return { "fetch": fetch_dict, "decode": decode_dict, "alu": alu_dict, "memory": mem_dict, "wb": wb_dict }

