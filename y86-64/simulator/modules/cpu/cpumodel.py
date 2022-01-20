# -*- encoding:UTF-8 -*-
from modules.cpu.parts import register

class CPUModel():
    def __init__(self, program, memsize):
        self.registerFile = register.registerFile()
        self.memory = bytearray(memsize)
        
        self.memory[0:len(program)] = program

        if memsize < len(program):
            self.memory += bytearray(16)
        
        # a b c x y z
        # a: ZF, b: SF, c: OF -> legacy
        # x: eql, y: grt, z: les -> use
        self.ALUCC = 0x07
        
        # w x y z
        # w: nop x: memory overflow, y: halt, z: err
        self.status = 0x00

        self.nowPC = -1
    
    def run(self):
        pass
    
    def toStringMemory(self):
        str = ""
        for i in self.memory:
            str += "%X" % i
    
    def getRegisters(self):
        return self.registerFile.registers