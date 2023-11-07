# -*- encoding:UTF-8 -*-

# xyz; x: equal, y: great, z: less
DECC = [0x7, 0x5, 0x1, 0x4, 0x3, 0x6, 0x2]

ALUMODE = [0, 1, 2, 3, 4, 5, 6, 7, 1, 2, 3]

#
# in_dict:
# - opcode: int
# - rA: int
# - rB: int
# - const: long
# - jmpc: long
#

def decode(buff, resigter):
    opcode = buff["op"]
    rA = buff["rA"]
    rB = buff["rB"]
    const = buff["const"]


def decode(in_dict, register):
    opcode = in_dict["opcode"]
    rA = in_dict["rA"]
    rB = in_dict["rB"]
    const = in_dict["const"]
    jmpc = in_dict["jmpc"]
    
    destE = 0xF
    destM = 0xF
    
    valA = 0x00
    valB = 0x00
    valD = 0x00

    srcA = 0xF
    srcB = 0xF
    srcD = 0xF
    
    # 0: add, 1: sub, 2: and, 3: xor, 4: or, 5: shl, 6: shr, 7: sar
    alumode = 0
    
    # 0: pass, 1: read, 2: write, 3: pop, 4: push
    memorymode = 0
    
    decc = 0x7
    
    ccupdate = 0
    
    # halt, nop
    if opcode in (0x00, 0x10):
        pass
    
    # cmov-
    elif opcode in (0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26):
        valA, valB = register.read(rA, 0xF)
        destE = rB
        srcA = rA

        decc = DECC[opcode & 0xF]
        
    # irmovq
    elif opcode == 0x30:
        valA = const
        destE = rB
    
    # rmmovq
    elif opcode == 0x40:
        valD, valB = register.read(rA, rB)
        valA = const
        srcA = 0xF
        srcB = rB
        srcD = rA

        memorymode = 2
    
    # mrmovq
    elif opcode == 0x50:
        valA, valB = register.read(0xF, rB)
        valA = const
        destM = rA
        srcA = 0xF
        srcB = rB

        memorymode = 1
    
    # op
    elif opcode in (0x60, 0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67):
        valA, valB = register.read(rA, rB)
        destE = rB
        srcA = rA
        srcB = rB

        alumode = ALUMODE[opcode & 0xF]
        ccupdate = 1

    # cmp, test
    elif opcode in (0x68, 0x69):
        valA, valB = register.read(rA, rB)
        destE = 0xF
        srcA = rA
        srcB = rB

        alumode = ALUMODE[opcode & 0xF]
        ccupdate = 1
    
    # not
    elif opcode == 0x6A:
        valA, valB = register.read(rA, 0xF)
        valB = 0xFFFFFFFFFFFFFFFF
        destE = rB
        srcA = rA
        
        alumode = ALUMODE[opcode & 0xF]
        ccupdate = 1

    # j--
    elif opcode in (0x70, 0x71, 0x72, 0x73, 0x74, 0x75, 0x76):
        valA = const
        destE = 0x10
        decc = DECC[opcode & 0xF]

        srcA = 0xF
    
    # call
    elif opcode == 0x80:
        valA, valB = register.read(0xF, 0x4)
        valA = 0x8
        valD = jmpc
        destE = 0x4
        srcB = 0x4
        srcD = 0xF

        alumode = 1
        memorymode = 4
    
    # ret
    elif opcode == 0x90:
        valA, valB = register.read(0xF, 0x4)
        valA = 0x8
        destE = 0x4
        destM = 0x10
        srcB = 0x4

        memorymode = 3
    
    # push
    elif opcode == 0xA0:
        valB, valD = register.read(0x4, rA)
        valA = 0x8
        destE = 0x4
        srcB = 0x4
        srcD = rA

        alumode = 1
        memorymode = 4
    
    # pop
    elif opcode == 0xB0:
        valA, valB = register.read(0xF, 0x4)
        valA = 0x8
        destE = 0x4
        destM = rA
        srcB = 0x4
        
        memorymode = 3
    
    return { "valA": valA, "valB": valB, "valD": valD, "destE": destE, "destM": destM, "srcA": srcA, "srcB": srcB , "srcD": srcD,
             "DECC": decc, "alumode": alumode, "memode": memorymode, "ccupdate": ccupdate, "opcode": opcode, "rA": rA, "rB": rB, "const": const }
