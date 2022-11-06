# -*- encoding:UTF-8 -*-
from modules.cpu.parts import register, fetch, decode, alu, memory, writeback
from modules.cpu import cpumodel
import copy
from _ast import If

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
        # ===== clock up =====
        if self.stallcount:
            self.stallcount -= 1
            fetch_dict = self.getDefaultResult()["fetch"]
            fetch_dict["npct"] = self.nowPC
            self.status |= 8
            
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
        decode_dict = decode.decode(self.FD, self.registerFile)
        decode_dict["npct"] = self.FD["npct"]
        
        # --- ALU ---
        alu_dict = alu.ALU(self.DA)
        
        # CC Update
        if self.DA["ccupdate"]:
            self.ALUCC = alu_dict["ALUCC"]
        
        updateflag = self.ALUCC & self.DA["DECC"]
        alu_dict["updateflag"] = updateflag
        alu_dict["npct"] = self.DA["npct"]
        
        alu_dict["memode"] = self.DA["memode"]
        alu_dict["valD"] = self.DA["valD"]
        alu_dict["destE"] = self.DA["destE"]
        alu_dict["destM"] = self.DA["destM"]
        
        # --- memory ---
        mem_dict = memory.memory(self.AM, self.memory)
        mem_dict["valD"] = self.AM["valD"]
        
        mem_dict["npct"] = self.AM["npct"]
        mem_dict["destE"] = self.AM["destE"]
        mem_dict["destM"] = self.AM["destM"]
        mem_dict["updateflag"] = self.AM["updateflag"]
        
        # --- write back ---
        wb_dict = writeback.writeback(self.MW, self.registerFile)
        
        wb_dict["npct"] = self.MW["npct"]
        
        # ===== clock down =====
        self.FD = fetch_dict
        self.DA = decode_dict
        self.AM = alu_dict
        
        if alu_dict["destE"] != 0xF:
            if self.DA["srcA"] == alu_dict["destE"]:
                self.DA["valA"] = alu_dict["valE"]
            elif self.DA["srcB"] == alu_dict["destE"]:
                self.DA["valB"] = alu_dict["valE"]
            elif self.DA["srcD"] == alu_dict["destE"]:
                self.DA["valD"] = alu_dict["valE"]

        self.MW = mem_dict
        
        if mem_dict["destE"] != 0xF:
            if self.DA["srcA"] == mem_dict["destE"]:
                self.DA["valA"] = mem_dict["valE"]
            elif self.DA["srcB"] == mem_dict["destE"]:
                self.DA["valB"] = mem_dict["valE"]
            elif self.DA["srcD"] == mem_dict["destE"]:
                self.DA["valD"] = mem_dict["valE"]
        if mem_dict["destM"] != 0xF:
            if self.DA["srcA"] == mem_dict["destM"]:
                self.DA["valA"] = mem_dict["valM"]
            elif self.DA["srcB"] == mem_dict["destM"]:
                self.DA["valB"] = mem_dict["valM"]
            elif self.DA["srcD"] == mem_dict["destM"]:
                self.DA["valD"] = mem_dict["valM"]
        
        return { "fetch": self.FD, "decode": self.DA, "alu": self.AM, "memory": self.MW, "wb": wb_dict }
