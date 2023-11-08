# -*- encoding:UTF-8 -*-

#
# in_dict
# - valE: long
# - valD: long
# - memode: int
#

def memory(buff, memory):
    memode = buff["memode"]
    
    valE = buff["valE"]
    
    valM = 0x00
    valD = buff["valD"]
    memerr = 0
    
    # pass
    if memode == 0:
        pass

    else:
        try:
            # read
            if memode == 1:
                arrdata = memory[valE : valE + 8]
                valM = arr2const(arrdata)
            
            # write
            elif memode == 2:
                memory[valE: valE + 8] = const2arr(valD)
            
            # pop
            elif memode == 3:
                arrdata = memory[valE - 8: valE]
                valM = arr2const(arrdata)
            
            # push
            elif memode == 4:
                memory[valE : valE + 8] = const2arr(valD)
            
        except IndexError:
            memerr = 1
    
    return { "result": {"status": memerr, "valE": valE, "valM": valM},
             "pass": {"destE": buff["destE"], "destM": buff["destM"], "destE update": buff["destE update"]},
             "buff": buff.copy() }
    
def arr2const(arr):
    const = 0
    
    for i in range(len(arr)):
        const += arr[i] << (i << 3)
    
    return const

def const2arr(const):
    arr = bytearray(8)
    
    for i in range(8):
        arr[i] = const & 0xFF
        const >>= 8
    
    return arr
