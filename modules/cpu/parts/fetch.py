# -*- encoding:UTF-8 -*-

def type_a(buff):
    return buff[0], None, None, None, 1

def type_b(buff):
    return buff[0], buff[1] >> 4, buff[1] & 0xF, None, 2

def type_c(buff):
    return buff[0], buff[1] >> 4, buff[1] & 0xF, arr2const(buff[2:10]), 10

def type_d(buff):
    return buff[0], None, None, arr2const(buff[1:9]), 9

IFUNCTION = { 0x00: type_a, 0x10: type_a, 0x20: type_b, 0x30: type_c,
              0x40: type_c, 0x50: type_c, 0x60: type_b, 0x70: type_d,
              0x80: type_d, 0x90: type_a, 0xA0: type_b, 0xB0: type_b }

def fetch(memory, pc):
    buff = memory[pc:pc + 16]
    ifun = buff[0] & 0xF0

    op, rA, rB, const, length = IFUNCTION[ifun](buff)

    return {"result": {"op": op, "rA": rA, "rB": rB, "const": const, "length": length, "nxpc": pc + length, "pc": pc},
            "buff": {"buff": buff, "pc": pc}}

def arr2const(arr):
    const = 0
    
    for i in range(len(arr)):
        const += arr[i] << (i << 3)
    
    return const
