# -*- encoding:UTF-8 -*-

# xyz; x: equal, y: great, z: less
DECC = [0x7, 0x5, 0x1, 0x4, 0x3, 0x6, 0x2]

ALUMODE = [0, 1, 2, 3, 4, 5, 6, 7, 1, 2, 3]

def decode(buff, register):
    opcode = buff["op"]
    rA = buff["rA"]
    rB = buff["rB"]
    const = buff["const"]

    valA = 0x00
    valB = 0x00
    valD = 0x00

    srcA = 0xF
    srcB = 0xF
    srcD = 0xF

    destE = 0xF
    destM = 0x00

    alu = 0
    memode = 0

    decc = 0x7
    ccupdate = 0

    # form: valA, valB, valD, srcA, srcB, srcD, destE, destM, 
    #       alumode, memode, decc, ccupdate
    def op_none():
        return (
            valA, valB, valD, srcA, srcB, srcD, destE, destM,
            alu, memode, decc, ccupdate
        )
    
    def op_move():
        valA, valB = register.read(rA, 0xF)

        srcA = rB

        destE = rA
        decc = DECC[opcode & 0xF]

        return (
            valA, valB, valD, srcA, srcB, srcD, destE, destM,
            alu, memode, decc, ccupdate
        )
    
    def op_irmove():
        valA = const

        destE = rB

        decc = DECC[opcode & 0xF]

        return (
            valA, valB, valD, srcA, srcB, srcD, destE, destM,
            alu, memode, decc, ccupdate
        )
    
    def op_rmmove():
        valA = const

        destE = rB

        decc = DECC[opcode & 0xF]
        memode = 2

        return (
            valA, valB, valD, srcA, srcB, srcD, destE, destM,
            alu, memode, decc, ccupdate
        )
    
    def op_mrmove():
        valA, valB = register.read(0xF, buff[rB])
        valA = const
        destM = rA
        srcA = 0xF
        srcB = rB

        memode = 1

        return (
            valA, valB, valD, srcA, srcB, srcD, destE, destM,
            alu, memode, decc, ccupdate
        )
    
    def op_op_a():
        valA, valB = register.read(rA, rB)
        destE = rB
        srcA = rA
        srcB = rB

        alu = ALUMODE[opcode & 0xF]
        ccupdate = 1

        return (
            valA, valB, valD, srcA, srcB, srcD, destE, destM,
            alu, memode, decc, ccupdate
        )
    
    def op_op_b():
        valA, valB = register.read(rA, rB)
        destE = 0xF
        srcA = rA
        srcB = rB

        alu = ALUMODE[opcode & 0xF]
        ccupdate = 1

        return (
            valA, valB, valD, srcA, srcB, srcD, destE, destM,
            alu, memode, decc, ccupdate
        )
    
    def op_op_c():
        valA, valB = register.read(rA, 0xF)
        valB = 0xFFFFFFFFFFFFFFFF
        destE = rB
        srcA = rA
        
        alu = ALUMODE[opcode & 0xF]
        ccupdate = 1

        return (
            valA, valB, valD, srcA, srcB, srcD, destE, destM,
            alu, memode, decc, ccupdate
        )
    
    def op_jump():
        valA = const
        destE = 0x10
        decc = DECC[opcode & 0xF]

        srcA = 0xF
        
        return (
            valA, valB, valD, srcA, srcB, srcD, destE, destM,
            alu, memode, decc, ccupdate
        )
        
    def op_call():
        valA, valB = register.read(0xF, 0x4)
        valA = 0x8
        valD = const
        destE = 0x4
        srcB = 0x4
        srcD = 0xF

        alu = 1
        memode = 4

        return (
            valA, valB, valD, srcA, srcB, srcD, destE, destM,
            alu, memode, decc, ccupdate
        )
    
    def op_ret():
        valA, valB = register.read(0xF, 0x4)
        valA = 0x8
        destE = 0x4
        destM = 0x10
        srcB = 0x4

        memode = 3

        return (
            valA, valB, valD, srcA, srcB, srcD, destE, destM,
            alu, memode, decc, ccupdate
        )
    
    def op_push():
        valB, valD = register.read(0x4, rA)
        valA = 0x8
        destE = 0x4
        srcB = 0x4
        srcD = rA

        alu = 1
        memode = 4

        return (
            valA, valB, valD, srcA, srcB, srcD, destE, destM,
            alu, memode, decc, ccupdate
        )
    
    def op_pop():
        valA, valB = register.read(0xF, 0x4)
        valA = 0x8
        destE = 0x4
        destM = rA
        srcB = 0x4
        
        memode = 3

        return (
            valA, valB, valD, srcA, srcB, srcD, destE, destM,
            alu, memode, decc, ccupdate
        )
    
    OP_FUNCTIONS = (op_none, op_move, op_irmove, op_rmmove, op_mrmove, op_op_a, op_op_b, op_op_c, op_jump, op_call, op_ret, op_push, op_pop)
    OP_FUNCTIONS_INDEX = (0, 0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12)
    OP_FUNCTION_CALC_SET = (0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2)

    op_index = OP_FUNCTIONS_INDEX[opcode >> 4] if opcode >> 4 != 0x6 else OP_FUNCTIONS_INDEX[6] + OP_FUNCTION_CALC_SET[opcode & 0x7]

    valA, valB, valD, srcA, srcB, srcD, destE, destM, alu, memode, decc, ccupdate = OP_FUNCTIONS[op_index]()

    return {"result": {"valA": valA, "valB": valB, "valD": valD, "srcA": srcA, "srcB": srcB, "srcD": srcD,
                       "destE": destE, "destM": destM, "alumode": alu, "memode": memode, "decc": decc, "ccupdate": ccupdate,
                       "pc": buff["nxpc"]},
            "buff": buff.copy()}