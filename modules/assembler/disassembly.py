# -*- encoding:UTF-8 -*-


import sys
from modules.assembler.Exceptions import *

# opcode에 해당하는 어셈블리 연산자를 저장한 딕셔너리 
OPERATOR_DICT = { 0x00: "halt",
                  0x10: "nop", 
                  0x20: "rrmovq", 0x21: "cmovle", 0x22: "cmovl", 0x23: "cmove",
                  0x24: "cmovne", 0x25: "cmovge", 0x26: "cmovg",
                  0x30: "irmovq",
                  0x40: "rmmovq",
                  0x50: "mrmovq",
                  0x60: "addq", 0x61: "subq", 0x62: "andq", 0x63: "xorq", 0x64: "or",0x65: "shl",
                  0x66: "shr", 0x67: "sar", 0x68: "cmp", 0x69: "test", 0x6A: "not",
                  0x70: "jmp", 0x71: "jle", 0x72: "jl", 0x73: "je", 0x74: "jne",
                  0x75: "jge", 0x76: "jg",
                  0x80: "call",
                  0x90: "ret",
                  0xA0: "pushq",
                  0xB0: "popq" }

# 레지스터 번호에 해당하는 레지스터 이름을 저장한 딕셔너리 
REGISTER_DICT = { 0x0: "%rax", 0x1: "%rcx", 0x2: "%rdx", 0x3: "%rbx",
                  0x4: "%rsp", 0x5: "%rbp", 0x6: "%rsi", 0x7: "%rdi",
                  0x8: "%r8", 0x9: "%r9", 0xA: "%r10", 0xB: "%r11",
                  0xC: "%r12", 0xD: "%r13", 0xE: "%r14", 0xF: "%null" }

IFUN_LENGTH = (1, 1, 2, 10, 10, 10, 2, 9, 9, 1, 2, 2)

class Disassembly():
    def __init__(self, bytecode):
        self.bytecode = bytecode
    
    # opcode에 따라서 값을 분석함 
    def decode(self, buff):
        opcode = buff[0]
        length = IFUN_LENGTH[opcode >> 4]
        rA = 0xF
        rB = 0xF
        const = 0x00
        drtv = False
        
        # 분석
        # 일반 명령어 
        if length == 1:
            pass
        
        elif length == 2:
            rA = buff[1] >> 4
            rB = buff[1] & 0xF
        
        elif length == 9:
            const = self.arr2const(buff[1 : 9])
        
        elif length == 10:
            rA = buff[1] >> 4
            rB = buff[1] & 0xF
            const = self.arr2const(buff[2 : 10])
        
        # 지시자
        if opcode == 0x01:
            length = 8
            drtv = True
            const = self.arr2const(buff[1 : 8])
        
        elif opcode in (0x02, 0x03):
            drtv = True
        
        return { "opcode": opcode, "length": length,
                 "rA": rA, "rB": rB, "const": const, "drtv": drtv }
    
	# 리틀 엔디안으로 표현된 정수를 정수로 변환
    def arr2const(self, arr):
        const = 0
    
        for i in range(len(arr)):
            const += arr[i] << (i << 3)
        
        return const
    
	# 현재 버퍼의 값을 문자열로 변환 
    def erreport(self, buff):
        str = ""
        
        for b in buff:
            str += "%X" % (b)
        
        return str
    
    # 실행 
    def run(self, isSimulator = False):
        pc = 0
        result = []
        pc_point = []
        bytecode_arr = []
        
        # 역 어셈블링 진행
        while pc < len(self.bytecode):
            try:
                # 16바이트 단위로 버퍼에 먼저 저장한 후 처리 
                buff = self.bytecode[pc : pc + 16]
                
                dechash = self.decode(buff)
                
                opcode = dechash["opcode"]
                length = dechash["length"]
                rA = dechash["rA"]
                rB = dechash["rB"]
                const = dechash["const"]

                pc_point.append(pc)
                bytecode_arr.append(buff[0 : length])
                
                pc += length
                
                # 지시자
                if dechash["drtv"]:
                    # .elemrkq
                    if opcode == 0x01:
                        result.append(".elemrkq 0x%X" % (const))
                        
                        # 데이터만큼 64비트 정수 취급
                        for i in range(const):
                            pc_point.append(pc)
                            bytecode_arr.append(self.bytecode[pc : pc + 8])

                            value = self.arr2const(self.bytecode[pc : pc + 8])
                            result.append(".quad 0x%X" % (value))
                            pc += 8
                    
                    # .dummy
                    elif opcode == 0x02:
                        dummylength = 1
                        
                        # 다음 번 02가 나올 때까지 반복
                        while self.bytecode[pc] != 0x02:
                            dummylength += 1
                            pc += 1
                        
                        # 다음 번 위치로 갱신
                        pc += 1
                        
                        result.append(".dummy 0x%X" % (dummylength + 1))
                        
                    # .align
                    elif opcode == 0x03:
                        result.append(".align 8")
                        pc += (8 - pc & 7)
                
                # 일반 명령어 
                else:
                    # 1바이트
                    if length == 1:
                        result.append(OPERATOR_DICT[opcode])
                    
                    # 2바이트
                    elif length == 2:
                        if opcode in (0xA0, 0xB0):
                            result.append("%s %s" % (OPERATOR_DICT[opcode], REGISTER_DICT[rA]))
                        else:
                            result.append("%s %s,%s" % (OPERATOR_DICT[opcode], REGISTER_DICT[rA], REGISTER_DICT[rB]))
                    
                    # 9바이트 
                    elif length == 9:
                        result.append("%s $0x%X" % (OPERATOR_DICT[opcode], const))
                    
                    # 10바이트 
                    elif length == 10:
                        if opcode >> 4 == 3:
                            result.append("%s $0x%X,%s" % (OPERATOR_DICT[opcode], const, REGISTER_DICT[rB]))
                            
                        elif opcode >> 4 == 4:
                            result.append("%s %s,0x%X(%s)" % (OPERATOR_DICT[opcode], REGISTER_DICT[rA], const, REGISTER_DICT[rB]))
                            
                        elif opcode >> 4 == 5:
                            result.append("%s 0x%X(%s),%s" % (OPERATOR_DICT[opcode], const, REGISTER_DICT[rB], REGISTER_DICT[rA]))
                        
            except KeyError:
                raise DsmUnknownOpcode(pc - length, self.erreport(buff))

            except IndexError:
                raise DsmUnknownOpcode(pc, self.erreport(buff))
        
        # 시뮬레이터 용 역 어셈블링 결과 출력
        # 구성은 <명령어 주소> <기계어 코드> <어셈블리어 코드>
        if isSimulator:
            bytecode_str_arr = []
            for barr in bytecode_arr:
                str = ""
                for b in barr:
                    str += "%02X" % (b)
                
                bytecode_str_arr.append(str)

            return (pc_point, bytecode_str_arr, result)

        # 프로그램에서의 결과 출력
        return result
    
