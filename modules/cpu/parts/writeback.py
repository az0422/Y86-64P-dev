# -*- encoding:UTF-8 -*-

def writeback(buff, register):
    # flag
    updateflag = buff["updateflag"]
    
    # destinations
    destE = buff["destE"]
    destM = buff["destM"]
    
    # results
    valE = buff["valE"]
    valM = buff["valM"]
    
    # write 
    if updateflag:
        register.write(destE, destM, valE, valM)
    
    else:
        register.write(0xF, destM, valE, valM)
    
    return { "result": {},
        "buff": buff.copy() }
