# -*- encoding:UTF-8 -*-
from modules.cpu.parts import register, fetch, decode, alu, memory, writeback
from modules.cpu import cpumodel

class PIPE(cpumodel.CPUModel):
    def __init__(self, program, memsize):
        super().__init__(program, memsize)
        
        self.stallcount = 0
        
        self.FD = { "opcode": 0x00, "rA": 0xF, "rB": 0xF, "const": 0x00, "pct": 0x00, "jmpc": 0x00, "buff": bytearray(16), "npct": -1 }
        self.DA = { "valA": 0x00, "valB": 0x00, "valD": 0x00, "alumode": 0x0, "memode": 0x0, "DECC": 0x7, "ccupdate": 0x0,
                    "srcA": 0xF, "srcB": 0xF, "srcD": 0xF, "destE": 0xF, "destM": 0xF, "npct": -1 }
        self.AM = { "valE": 0x00, "valD": 0x00, "memode": 0x0, "destE": 0xF, "destM": 0xF, "updateflag": 0x1, "npct": -1 }
        self.MW = { "valE": 0x00, "valM": 0x00, "destE": 0xF, "destM": 0xF, "updateflag": 0x1, "memode": 0x0, "npct": -1 }
        
        self.memuse = 0
    
    def run(self):
        # === write back ===
        wb_dict = writeback.writeback(self.MW, self.registerFile)
        wb_dict["npct"] = self.MW["npct"]
        
        # === memory ===
        memory_dict = memory.memory(self.AM, self.memory)
        memory_dict["npct"] = self.AM["npct"]
        
        # pass
        for key in ["destE", "destM", "updateflag", "valD"]:
            memory_dict[key] = self.AM[key]
        
        self.MW = memory_dict
        
        fwdu = { "mem": "None", "malu": "None", "alu": "None" }
        
        self.forwardingUnit(fwdu)
        
        # === ALU ===
        alu_dict = alu.ALU(self.DA)
        alu_dict["npct"] = self.DA["npct"]
        
        # CC Update
        if self.DA["ccupdate"]:
            self.ALUCC = alu_dict["ALUCC"]
        
        updateflag = self.ALUCC & self.DA["DECC"]
        alu_dict["updateflag"] = updateflag
        
        # pass
        for key in ["valD", "memode", "destE", "destM", "DECC"]:
            alu_dict[key] = self.DA[key]
        
        self.AM = alu_dict
        
        # === decode ===
        decode_dict = decode.decode(self.FD, self.registerFile)
        decode_dict["npct"] = self.FD["npct"]
        
        self.DA = decode_dict
        
        self.forwardingUnit(fwdu)
        
        # === fetch ===
        if self.stallcount:
            # stall
            self.stallcount -=1
            pct = self.FD["pct"]
            npct = self.FD["npct"]
            self.FD = { "opcode": 0x00, "rA": 0xF, "rB": 0xF, "const": 0x00, "buff": bytearray(16),
                        "pct": pct, "jmpc": 0x00, "status": 0x8, "stallcount": self.stallcount, "npct": npct }
            self.status |= 8

        else:
            # fetch PC
            pc = self.registerFile.readPC()
            self.nowPC = pc
            
            self.status &= 7
            
            # memory error
            if pc >= len(self.memory):
                self.status |= 4

            fetch_dict = fetch.fetch(self.memory, pc)

            self.status = self.status & 7

            # status update
            self.status |= fetch_dict["status"]
            
            # PC pre-update
            if not(self.status & 0x7):
                self.registerFile.writePC(fetch_dict["pct"])
            
            fetch_dict["npct"] = self.nowPC
            
            # update pipeline register from result
            self.FD = fetch_dict

            # update stall count
            self.stallcount = fetch_dict["stallcount"]
        
        return { "fetch": self.FD, "decode": self.DA, "alu": self.AM, "memory": self.MW, "wb": wb_dict, "fwdu": fwdu }
    
    def forwardingUnit(self, fwdu):
        if self.MW["destM"] != 0xF:
            if self.DA["srcA"] == self.MW["destM"]:
                self.DA["valA"] = self.MW["valM"]
                fwdu["mem"] = "valA"
                
            if self.DA["srcB"] == self.MW["destM"]:
                self.DA["valB"] = self.MW["valM"]
                fwdu["mem"] = "valB"
                
            if self.DA["srcD"] == self.MW["destM"]:
                self.DA["valD"] = self.MW["valM"]
                fwdu["mem"] = "valD"
        
        if self.MW["destE"] != 0xF and self.MW["updateflag"]:
            if self.DA["srcA"] == self.MW["destE"]:
                self.DA["valA"] = self.MW["valE"]
                fwdu["malu"] = "valA"
                
            if self.DA["srcB"] == self.MW["destE"]:
                self.DA["valB"] = self.MW["valE"]
                fwdu["malu"] = "valB"
                
            if self.DA["srcD"] == self.MW["destE"]:
                self.DA["valD"] = self.MW["valE"]
                fwdu["malu"] = "valD"
        
        # ALU
        if self.AM["destE"] != 0xF and self.AM["updateflag"]:
            if self.DA["srcA"] == self.AM["destE"]:
                self.DA["valA"] = self.AM["valE"]
                fwdu["alu"] = "valA"
                
            if self.DA["srcB"] == self.AM["destE"]:
                self.DA["valB"] = self.AM["valE"]
                fwdu["alu"] = "valB"
                
            if self.DA["srcD"] == self.AM["destE"]:
                self.DA["valD"] = self.AM["valE"]
                fwdu["alu"] = "valD"
