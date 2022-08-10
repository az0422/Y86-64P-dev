# -*- encoding:UTF-8 -*-

class registerFile():
    def __init__(self):
        # registers
        # 0: rax, 1: rcx, 2: rdx, 3: rbx
        # 4: rsp, 5: rbp, 6: rsi, 7: rdi
        # 8: r8, 9: r9, A: r10, B: r11
        # C: r12, D: r13, E: r14, F: null
        # 10: PC
        self.registers = [0x00] * 17
    
    # read
    # input: address(5bit) * 2
    # output: value(64bit) * 2
    def read(self, rA, rB):
        return [self.registers[rA], self.registers[rB]]
    
    # write
    # input: address(5bit) * 2
    #        data(64bit) * 2
    def write(self, rA, rB, dataA, dataB):
        self.registers[rA] = dataA
        self.registers[rB] = dataB
        self.registers[0xF] = 0x00
    
    # PC read
    # output(64bit) * 1
    def readPC(self):
        return self.registers[0x10]
    
    # PC update
    # input(64bit) * 1
    def writePC(self, pct):
        self.registers[0x10] = pct
