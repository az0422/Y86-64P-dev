# -*- encoding:UTF-8 -*-
from modules.cpu.parts import register, fetch, decode, alu, memory, writeback
from modules.cpu import cpumodel
import copy

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
        
        self.model = "pipe"
        
        self.recentRegister = 0xF
    
    def getDefaultResult(self):
        return { "fetch": { "opcode": 0x00, "rA": 0xF, "rB": 0xF, "const": 0x00, "pct": 0x00, "jmpc": 0x00, "buff": bytearray(16), "npct": -1 },
                 "decode": { "valA": 0x00, "valB": 0x00, "valD": 0x00, "alumode": 0x0, "memode": 0x0, "DECC": 0x7, "ccupdate": 0x0,
                             "srcA": 0xF, "srcB": 0xF, "srcD": 0xF, "destE": 0xF, "destM": 0xF, "npct": -1, "fwd_alu": "None", "fwd_mem": "None", "fwd_malu": "None" },
                 "alu": { "valE": 0x00, "valD": 0x00, "memode": 0x0, "destE": 0xF, "destM": 0xF, "updateflag": 0x1, "npct": -1, "ALUCC": 7, "valA": 0, "valB": 0,
                          "alumode": 0, "DECC": 7, "destE": 0xF, "destM": 0xF, "memode": 0 },
                 "memory": { "valE": 0x00, "valM": 0x00, "destE": 0xF, "destM": 0xF, "updateflag": 0x1, "memode": 0x0, "npct": -1, "valD": 0 },
                 "wb": { "destE": 0xF, "destM": 0xF, "valE": 0, "valM": 0, "updateflag": 1, "npct": -1 },
                 "fwdu": { "alu": "None", "mem": "None", "malu": "None" }
                }
    
    def run(self):
        if self.stallcount:
            self.stallcount += 1
            fetch_dict = self.getDefaultResult()["fetch"]
            
        else:
            pc = self.registerFile.readPC()
            self.nowPC = pc
            
            if pc >= len(self.memory):
                self.status |= 4
                
            else:
            # --- fetch ---
                fetch_dict = fetch.fetch(self.memory, pc)
                
                self.status = self.status & 7
        
                # status update
                self.status |= fetch_dict["status"]
                
                # PC pre-update
                if not(self.status & 0x7):
                    self.registerFile.writePC(fetch_dict["pct"])
                
                fetch_dict["npct"] = self.nowPC
                
                self.stallcount = fetch_dict["stallcount"]
        
        # --- decode --- 
        decode_dict = decode.decode(fetch_dict, self.registerFile)
        decode_dict["npct"] = fetch_dict["npct"]
        
        # --- ALU ---
        alu_dict = alu.ALU(decode_dict)
        
        # CC Update
        if decode_dict["ccupdate"]:
            self.ALUCC = alu_dict["ALUCC"]
        
        updateflag = self.ALUCC & decode_dict["DECC"]
        alu_dict["updateflag"] = updateflag
        alu_dict["npct"] = decode_dict["npct"]
        
        alu_dict["memode"] = decode_dict["memode"]
        alu_dict["valD"] = decode_dict["valD"]
        alu_dict["destE"] = decode_dict["destE"]
        alu_dict["destM"] = decode_dict["destM"]
        
        # --- memory ---
        mem_in_dict = { "valD": decode_dict["valD"], "memode": decode_dict["memode"], "valE": alu_dict["valE"] }

        mem_dict = memory.memory(mem_in_dict, self.memory)
        mem_dict["valD"] = decode_dict["valD"]
        
        mem_dict["npct"] = alu_dict["npct"]
        mem_dict["destE"] = alu_dict["destE"]
        mem_dict["destM"] = alu_dict["destM"]
        mem_dict["updateflag"] = alu_dict["updateflag"]
        
        # --- write back ---
        wb_in_dict = { "valE": mem_dict["valE"], "valM": mem_dict["valM"], "destE": decode_dict["destE"],
                       "destM": decode_dict["destM"], "updateflag": updateflag }
        
        wb_dict = writeback.writeback(wb_in_dict, self.registerFile)
        
        wb_dict["npct"] = mem_dict["npct"]
        
        return { "fetch": fetch_dict, "decode": decode_dict, "alu": alu_dict, "memory": mem_dict, "wb": wb_dict }
    
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
            