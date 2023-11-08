# -*- encoding:UTF-8 -*-

VALIDATE_OP = (2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
               8, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
               0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1,
               0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
               0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
               0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1,
               0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1,
               0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
               0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
               0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
               0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,)

def arr2const(arr):
    const = 0
    
    for i in range(len(arr)):
        const += arr[i] << (i << 3)
    
    return const

def type_a(buff):
    return buff[0], 0xF, 0xF, 0x00, 1

def type_b(buff):
    return buff[0], buff[1] >> 4, buff[1] & 0xF, 0x00, 2

def type_c(buff):
    return buff[0], buff[1] >> 4, buff[1] & 0xF, arr2const(buff[2:10]), 10

def type_d(buff):
    return buff[0], 0xF, 0xF, arr2const(buff[1:9]), 9

IFUNCTION = (
    type_a, type_a, type_b, type_c,
    type_c, type_c, type_b, type_d,
    type_d, type_a, type_b, type_b
)

def fetch(memory, pc):
    buff = memory[pc:pc + 16]
    ifun = buff[0] >> 4
    op = buff[0]

    status = VALIDATE_OP[op]

    if not status & 0x9: op, rA, rB, const, length = IFUNCTION[ifun](buff)
    else: rA, rB, const, length = 0xF, 0xF, 0x00, 0

    nxpc = pc + length

    if ifun == 0x7:
        nxpc = const
        pc = pc + length

    elif ifun == 0x8:
        nxpc = const
        const = pc + length

    return {"result": {"op": op, "rA": rA, "rB": rB, "const": const, "length": length, "nxpc": nxpc, "pc": pc, "status": status},
            "buff": {"buff": buff, "pc": pc}}
