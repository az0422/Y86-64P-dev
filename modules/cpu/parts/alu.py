# -*- encoding:UTF-8 -*-

#
# in_dict:
# - valA: long
# - valB: long
# - alumode: int
#
def ALU(in_dict):
    alumode = in_dict["alumode"]
    
    result = {}
    
    valA = in_dict["valA"]
    valB = in_dict["valB"]
    valE = 0x00
    
    les = 0
    eql = 0
    grt = 0
    
    # addq
    if alumode == 0:
        valE = valB + valA
    
    # subq
    elif alumode == 1:
        valE = valB - valA
    
    # andq
    elif alumode == 2:
        valE = valB & valA
    
    # xorq
    elif alumode == 3:
        valE = valB ^ valA
    
    # or
    elif alumode == 4:
        valE = valB | valA
    
    # shl
    elif alumode == 5:
        if valA > 64:
            valE = 0
        else:
            valE = valB << valA
    
    # shr
    elif alumode == 6:
        if valA > 64:
            valE = 0
        else:
            valE = valB >> valA
    
    # sar
    elif alumode == 7:
        if valA > 64:
            valE = -1
        else:
            valE = valB >> valA
            msb = valB >> 63
            
            if msb == 1:
                mask = -1 << (64 - valA)
                valE = valE | mask
    
    # limit 64bit
    valE = valE & 0xFFFFFFFFFFFFFFFF
    
    # get MSB from operand
    valASF = valA >> 63 & 0x1
    valBSF = valB >> 63 & 0x1
    
    # set flags
    ZF = int(valE == 0x00)
    SF = valE >> 63
    OF = (~valASF & ~valBSF & SF) | (valASF & valBSF & ~SF) if alumode == 0 else 0
    
    # set CC flag
    eql = ZF
    les = SF ^ OF
    grt = ~ZF & ~(SF ^ OF) & 0x1 
    
    return { "valE": valE, "ALUCC": (ZF << 5) | (SF << 4) | (OF << 3) | (eql << 2) | (grt << 1) | les, "valA": valA, "valB": valB, "alumode": alumode }
