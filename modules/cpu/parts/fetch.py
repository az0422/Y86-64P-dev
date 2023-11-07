# -*- encoding:UTF-8 -*-

def fetch(memory, pct):
    buff = memory[pct:pct + 16]
    
    opcode = buff[0]
    const = 0x00
    rA = 0xF
    rB = 0xF
    
    jmpc = 0

    err = 0
    halt = 0
    nop = 0

    stallcount = 0
    
    # halt
    if opcode == 0x00:
        halt = 1
    
    # nop
    elif opcode == 0x10:
        nop = 1
        pct += 1
    
    # cmov--
    elif opcode in (0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26):
        rA = buff[1] >> 4
        rB = buff[1] & 0xF
        pct += 2
    
    # irmovq, rmmovq, mrmovq
    elif opcode in (0x30, 0x40, 0x50):
        rA = buff[1] >> 4
        rB = buff[1] & 0xF
        const = arr2const(buff[2:10])
        pct += 10
    
    # op
    elif opcode in (0x60, 0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6A):
        rA = buff[1] >> 4
        rB = buff[1] & 0xF
        pct += 2
    
    # j--
    elif opcode in (0x70, 0x71, 0x72, 0x73, 0x74, 0x75, 0x76):
        const = arr2const(buff[1:9])
        jmpc = const
        pct += 9

        stallcount = 4
    
    # call
    elif opcode == 0x80:
        jmpc = pct + 9
        pct = arr2const(buff[1:9])
    
    # ret
    elif opcode == 0x90:
        pct += 1

        stallcount = 4
    
    # push, pop
    elif opcode in (0xA0, 0xB0):
        rA = buff[1] >> 4
        pct += 2
    
    else:
        err = 1
        
    return { "opcode": opcode, "rA": rA, "rB": rB, "const": const, "buff": buff, "pct": pct, "jmpc": jmpc, "status": (nop << 3 | halt << 1 | err), "stallcount": stallcount }

def arr2const(arr):
    const = 0
    
    for i in range(len(arr)):
        const += arr[i] << (i << 3)
    
    return const
