# -*- encoding:UTF-8 -*-

import sys
import re

from modules.assembler.Exceptions import *
from array import array

# operator dictionary
OPERATOR_DICT = { "halt": 0x00,
                  "nop": 0x10,
                  "rrmovq": 0x20, "cmovle": 0x21, "cmovl": 0x22, "cmove": 0x23, "cmovne": 0x24, "cmovge": 0x25, "cmovg": 0x26,
                  "irmovq": 0x30,
                  "rmmovq": 0x40,
                  "mrmovq": 0x50,
                  "addq": 0x60, "subq": 0x61, "andq": 0x62, "xorq": 0x63, "or": 0x64, "shl": 0x65, "shr": 0x66, "sar": 0x67,"cmp": 0x68, "test": 0x69, "not": 0x6A,
                  "jmp": 0x70, "jle": 0x71, "jl": 0x72, "je": 0x73, "jne": 0x74, "jge": 0x75, "jg": 0x76,
                  "call": 0x80,
                  "ret": 0x90,
                  "pushq": 0xA0,
                  "popq": 0xB0,
                  ".elemrkq": 0x01 }

# instruction length dictionary
INSTRUCTION_LENGTH = { "halt": 1,
                       "nop": 1,
                       "rrmovq": 2, "cmovle": 2, "cmovl": 2, "cmove": 2, "cmovne": 2, "cmovge": 2, "cmovg": 2,
                       "irmovq": 10,
                       "rmmovq": 10,
                       "mrmovq": 10,
                       "addq": 2, "subq": 2, "andq": 2, "xorq": 2, "or": 2, "shl": 2, "shr": 2, "sar": 2, "cmp": 2, "test": 2, "not": 2,
                       "jmp": 9, "jle": 9, "jl": 9, "je": 9, "jne": 9, "jge": 9, "jg": 9,
                       "call": 9,
                       "ret": 1,
                       "pushq": 2,
                       "popq": 2,
                       ".elemrkq": 8,
                       ".quad": 8 }

# register dictionary
REGISTER_DICT = { "%rax": 0x00, "%rcx": 0x01, "%rdx": 0x02, "%rbx": 0x03, "%rsp": 0x04, "%rbp": 0x05, "%rsi": 0x06, "%rdi": 0x07,
                  "%r8": 0x08, "%r9": 0x09, "%r10": 0x0A, "%r11": 0x0B, "%r12": 0x0C, "%r13": 0x0D, "%r14": 0x0E, "%null": 0x0F }

class Assembly():
    def __init__(self, asm_list):
        self.asm_list = asm_list
    
    def trim(self, asm_str):
        result = []
        
        # remove unnecessary space
        asm_str = asm_str.strip()
        
        if asm_str != "":
            # split comment and label
            line = asm_str.replace("#", "\n#", 1)
            linearr = line.split("\n")
            
            for strt in linearr:
                strt = strt.strip()
                
                if strt.startswith("#") or strt == "":
                    continue
                
                strt = strt.replace(":", ":\n")
                
                strtarr = strt.split("\n")
                
                for str in strtarr:
                    str = str.strip()
                    
                    if str == "":
                        continue
                    
                    # exchange white spaces to a space
                    strarr = str.split(maxsplit = 1)
    
                    if len(strarr) == 2:
                        str = "%s %s" % (strarr[0], strarr[1].replace(" ", "").replace("\t", ""))
                    
                    result.append(str)
        
        return result
    
    # calculate label address
    def calcLabel(self):
        pc = 0
        result = {}
        line = 1
        
        for asm_str in self.asm_list:
            asm_trim = self.trim(asm_str)
            
            for record in asm_trim:
                # if label
                if record.endswith(":"):
                    result[record[:-1]] = pc
                    continue
                
                recordsplit = record.split(" ")
                
                # 8byte align 
                if recordsplit[0] == ".align":
                    pc += (8 - (pc & 7))
                
                # dummy space
                elif recordsplit[0] == ".dummy":
                    pc += eval(recordsplit[1])
                
                elif recordsplit[0] == ".pos":
                    pc = eval(recordsplit[1])
                
                # instruction
                else:
                    if recordsplit[0] not in INSTRUCTION_LENGTH.keys():
                        raise AsmUnknownOperator(line, asm_str)

                    pc += INSTRUCTION_LENGTH[recordsplit[0]]
                
                line += 1
            
        return result
    
    # parser
    def parsing(self, asm_str):
        result = []
        
        trimdata = self.trim(asm_str)
         
        for record in trimdata:
            # default
            parse = { "operator": "nop", "rA": "%null", "rB": "%null", "const": "0" }
            parsetemp = {}
            
            if record.endswith(":"):
                continue
            
            recordsplit = record.split(maxsplit = 1)
            
            # seperate operator and operand
            operator = recordsplit[0]
            operand = recordsplit[1] if len(recordsplit) == 2 else ""
            
            parse["operator"] = operator
            
            # parse
            if operator in ("halt", "nop", "ret"):
                pass
            
            elif operator in ("rrmovq", "cmovle", "cmovl", "cmove", "cmovne", "cmovge", "cmovg", "addq", "subq", "andq", "xorq", "or", "shl", "shr", "sar", "cmp", "test", "not"):
                parsetemp = re.search("(?P<rA>%[0-9a-z]+),(?P<rB>%[0-9a-z]+)", operand).groupdict()
            
            elif operator in ("pushq", "popq"):
                parsetemp = re.search("(?P<rA>%[0-9a-z]+)", operand).groupdict()
            
            elif operator in ("irmovq"):
                # ((\\-|\\.)?[0-9a-zA-Z\\_\\-\\.]+)
                parsetemp = re.search("\\$?(?P<const>((\\-|\\.)?[0-9a-zA-Z\\_\\-\\.]+)),(?P<rB>%[0-9a-z]+)", operand).groupdict()
            
            elif operator in ("rmmovq"):
                parsetemp = re.search("(?P<rA>%[0-9a-z]+),(?P<const>((\\-|\\.)?[0-9a-zA-Z\\_\\-\\.]*))\\((?P<rB>%[0-9a-z]+)\\)", operand).groupdict()
            
            elif operator in ("mrmovq"):
                parsetemp = re.search("(?P<const>((\\-|\\.)?[0-9a-zA-Z\\_\\-\\.]*))\\((?P<rB>%[0-9a-z]+)\\),(?P<rA>%[0-9a-z]+)", operand).groupdict()
            
            elif operator in ("jmp", "jle", "je", "jne", "jge", "jg", "call"):
                parsetemp = re.search("\\$?(?P<const>((\\-|\\.)?[0-9a-zA-Z\\_\\-\\.]+))", operand).groupdict()
            
            elif operator in (".quad", ".elemrkq", ".dummy", ".align", ".pos"):
                parsetemp = re.search("(?P<const>((\\-|\\.)?[0-9a-zA-Z\\_\\-\\.]+))", operand).groupdict()
            
            # 값 가져오기 
            for key in parsetemp.keys():
                parse[key] = parsetemp[key]
            
            result.append(parse)
        
        return result
    
    # 상수 값을 리틀 엔디안 배열로 변환 
    def constAssembly(self, const, size = 8):
        result = bytearray()
        
        for i in range(size):
            result.append(const & 0xFF)
            const >>= 8
        
        return result
    
    def run(self, warn_level):
        # 1패스: 레이블 위치 계산 
        labeladdr = self.calcLabel()

        line = 1
        result = bytearray()
        
        # 2패스: 어셈블리 코드 변환 
        for asm in self.asm_list:
            try:
                # 분석 값 가져오기
                parsedata = self.parsing(asm)
            except AttributeError:
                raise AsmSyntaxError(line, asm)
            
            # 바이너리 코드로 변환
            for parecord in parsedata:
                # 값 인출 
                operator = parecord["operator"]
                rA = parecord["rA"]
                rB = parecord["rB"]
                const = parecord["const"] if parecord["const"] != "" else "0"
                
                try:
                    # 부호가 있고 10진수이거나 16진수인 값일 경우
                    if re.match("\\-?[0-9]+|(0x[0-9a-fA-F]+)$", const):
                        const = eval(const)
                    
                    else:
                        const = labeladdr[const]
                        
                except SyntaxError:
                    raise AsmConstantError(line, asm)
                
                except KeyError:
                    raise AsmUnknownLabel(line, asm)
                
                # 레지스터 이름 검사 
                if rA not in REGISTER_DICT.keys() or rB not in REGISTER_DICT.keys():
                    raise AsmUnknownRegister(line, asm)
                
                # 어셈블리 명령어
                if operator in OPERATOR_DICT.keys():
                    # opcode 삽입
                    result.append(OPERATOR_DICT[operator])
                    
                    # 피연산자 삽입 
                    # opcode
                    if operator in ("halt", "nop", "ret"):
                        pass
                    
                    # opcode rA,rB
                    elif operator in ("rrmovq", "cmovle", "cmovl", "cmove", "cmovne", "cmovge", "cmovg", "addq", "subq",
                                      "andq", "xorq", "or", "shl", "shr", "sar", "cmp", "test", "pushq", "popq", "not"):
                        result.append(REGISTER_DICT[rA] << 4 | REGISTER_DICT[rB])
                    
                    # opcode rA,rB constant
                    elif operator in ("irmovq", "rmmovq", "mrmovq"):
                        constbarr = self.constAssembly(const)
                        
                        result.append(REGISTER_DICT[rA] << 4 | REGISTER_DICT[rB])
                        result += constbarr
                    
                    # opcode constant
                    elif operator in ("jmp", "jle", "jl", "je", "jne", "jge", "jg", "call"):
                        constbarr = self.constAssembly(const)
                        result += constbarr
                    
                    elif operator == ".elemrkq":
                        constbarr = self.constAssembly(const, size = 7)
                        result += constbarr
                    
                # 지시자
                elif operator == ".quad":
                    constbarr = self.constAssembly(const)
                    result += constbarr
                
                elif operator == ".align":
                    arr = bytearray(8 - len(result) & 7)
                    
                    if len(arr) != 0:
                        arr[0] = 0x03
                        result += arr
                
                elif operator == ".dummy":
                    arr = bytearray(const)
                    arr[0] = 0x02
                    arr[-1] = 0x02
                    result += arr
                
                elif operator == ".pos":
                    if const < len(result):
                        raise AsmSyntaxError(line, asm)
                    
                    elif const > 0:
                        if warn_level == "1":
                            print("WARN: .pos CONST was deprecated where line %d of .pos %d.\nUse .dummy CONST instead when make dummy space. It will be disassembled to .dummy." % (line, const))
                        arr = bytearray(const - len(result))
                        arr[0] = 0x02
                        arr[-1] = 0x02
                        result += arr
                        
                    elif const == 0:
                        pass
            
            line += 1
        
        return result
    