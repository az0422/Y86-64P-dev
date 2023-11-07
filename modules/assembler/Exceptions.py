# -*- encoding:UTF-8 -*-

class asmException(Exception):
    def __init__(self, msg, name, line, code):
        super().__init__(msg)
        self.line = line
        self.code = code
        self.name = name
        self.msg = msg
    
    def printError(self):
        print("%s line at %d" % (self.code, self.line))
        print("%s: %s" % (self.name, self.msg))
    
    def toString(self):
        return "%s line at %d\n%s: %s" % (self.code, self.line, self.name, self.msg)

class dsmException(Exception):
    def __init__(self, msg, name, addr, buffs):
        super().__init__(msg)
        self.addr = addr
        self.buffs = buffs
        self.name = name
        self.msg = msg
    
    def printError(self):
        print("buffer: %s, address: %X" % (self.buffs, self.addr))
        print("%s: %s" % (self.name, self.msg))
    
    def toString(self):
        return "buffer: %s, address: %X\n%s: %s" % (self.buffs, self.addr, self.name, self.msg)

class AsmSyntaxError(asmException):
	def __init__(self, line, code):
		super().__init__("invalid syntax", "AsmSyntaxError", line, code)

class AsmUnknownOperator(asmException):
    def __init__(self, line, code):
        super().__init__("unknown operator", "AsmUnknownOperator", line, code)

class AsmConstantError(asmException):
    def __init__(self, line, code):
        super().__init__("invalid constant", "AsmConstantError", line, code)

class AsmUnknownLabel(asmException):
    def __init__(self, line, code):
        super().__init__("unknown label", "AsmUnknownLabel", line, code)

class AsmUnknownRegister(asmException):
    def __init__(self, line, code):
        super().__init__("unknown register(s)", "AsmUnknownRegister", line, code)

class DsmUnknownOpcode(dsmException):
    def __init__(self, addr, buffs):
        super().__init__("unknown opcode", "DsmUnknownOpcode", addr, buffs)
