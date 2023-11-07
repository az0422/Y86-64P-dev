# -*- encoding:UTF-8 -*-

#
# in_dict:
# - valA: long
# - valB: long
# - alumode: int
#
def ALU(buff):
    alu = buff["alumode"]

    valA = buff["valA"]
    valB = buff["valB"]
    valE = 0x00
    
    les = 0
    eql = 0
    grt = 0

    def addq():
        return valB + valA
    
    def subq():
        return valB - valA
    
    def andq():
        return valB & valA
    
    def xorq():
        return valB ^ valA
    
    def orq():
        return valB | valA
    
    def shl():
        if valA > 64:
            return 0
        else:
            return valB << valA
    
    def shr():
        if valA > 64:
            return 0
        else:
            return valB >> valA
    
    def sar():
        if valA > 64:
            return 0
        else:
            valE = valB >> valA
            msb = valB >> 63
            
            if msb == 1:
                mask = -1 << (64 - valA)
                return valE | mask
            
            return valE
    
    valE = (addq, subq, andq, xorq, orq, shl, shr, sar)[alu]()

    # limit 64bit
    valE = valE & 0xFFFFFFFFFFFFFFFF
    
    # get MSB from operand
    valASF = valA >> 63 & 0x1
    valBSF = valB >> 63 & 0x1
    
    # set flags
    ZF = int(valE == 0x00)
    SF = valE >> 63
    OF = (~valASF & ~valBSF & SF) | (valASF & valBSF & ~SF) if alu == 0 else 0
    
    # set CC flag
    eql = ZF
    les = SF ^ OF
    grt = ~ZF & ~(SF ^ OF) & 0x1 
    
    return { "result": {"valE": valE, "cc": ZF << 5 | SF << 4 | OF << 3 | eql << 2 | les << 1 | grt},
             "pass": {"valD": buff["valD"], "destE": buff["destE"], "destM": buff["destM"], "memode": buff["memode"]}, 
             "buff": buff}
