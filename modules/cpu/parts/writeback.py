# -*- encoding:UTF-8 -*-

def writeback(in_dict, register):
    # flag
    updateflag = in_dict["updateflag"]
    
    # destinations
    destE = in_dict["destE"]
    destM = in_dict["destM"]
    
    # results
    valE = in_dict["valE"]
    valM = in_dict["valM"]
    
    # write 
    if updateflag:
        register.write(destE, destM, valE, valM)
    
    else:
        register.write(0xF, destM, valE, valM)
    
    return { "destE": destE, "destM": destM, "valE": valE, "valM": valM, "updateflag": updateflag }
