
// fetch
document.getElementById("fetch-buffer").innerHTML = response_obj.fetch_buff;
document.getElementById("fetch-pc").innerHTML = (response_obj.fetch_pct != -1 ? response_obj.fetch_pct : 0).toString(16).toUpperCase();
document.getElementById("fetch-opcode").innerHTML = response_obj.fetch_opcode.toString(16).toUpperCase().padStart(2, "0");
document.getElementById("fetch-rA").innerHTML = response_obj.fetch_rA.toString(16).toUpperCase() + " (" + REGISTERS[response_obj.fetch_rA] + ")";
document.getElementById("fetch-rB").innerHTML = response_obj.fetch_rB.toString(16).toUpperCase() + " (" + REGISTERS[response_obj.fetch_rB] + ")";
document.getElementById("fetch-constant").innerHTML = response_obj.fetch_const;

// decode
document.getElementById("decode-valA").innerHTML = response_obj.decode_valA;
document.getElementById("decode-valB").innerHTML = response_obj.decode_valB;
document.getElementById("decode-valD").innerHTML = response_obj.decode_valD;
document.getElementById("decode-srcA").innerHTML = response_obj.decode_srcA.toString(16).toUpperCase() + " (" + REGISTERS[response_obj.decode_srcA] + ")";
document.getElementById("decode-srcB").innerHTML = response_obj.decode_srcB.toString(16).toUpperCase() + " (" + REGISTERS[response_obj.decode_srcB] + ")";
document.getElementById("decode-srcD").innerHTML = response_obj.decode_srcD.toString(16).toUpperCase() + " (" + REGISTERS[response_obj.decode_srcD] + ")";
document.getElementById("decode-destE").innerHTML = response_obj.decode_destE.toString(16).toUpperCase() + " (" + REGISTERS[response_obj.decode_destE] + ")";
document.getElementById("decode-destM").innerHTML = response_obj.decode_destM.toString(16).toUpperCase() + " (" + REGISTERS[response_obj.decode_destM] + ")";
document.getElementById("decode-decode-CC").innerHTML = response_obj.decode_DECC;
document.getElementById("decode-memory-mode").innerHTML = MEMODE[response_obj.decode_memode];
document.getElementById("decode-ALU-mode").innerHTML = ALUMODE[response_obj.decode_alumode];
document.getElementById("decode-alu-ccupdate").innerHTML = response_obj.decode_ccupdate ? "Y" : "N";

// forwarding unit
//document.getElementById("decode-fwd-alu").innerHTML = response_obj.fwdu_alu;
//document.getElementById("decode-fwd-mem").innerHTML = response_obj.fwdu_mem;
//document.getElementById("decode-fwd-malu").innerHTML = response_obj.fwdu_malu;

// ALU
document.getElementById("alu-valA").innerHTML = response_obj.alu_valA;
document.getElementById("alu-valB").innerHTML = response_obj.alu_valB;
document.getElementById("alu-mode").innerHTML = ALUMODE[response_obj.alu_alumode];
document.getElementById("alu-valE").innerHTML = response_obj.alu_valE;
document.getElementById("alu-ALUCC").innerHTML = response_obj.alu_ALUCC;
document.getElementById("alu-ccupdate").innerHTML = response_obj.alu_ccupdate ? "Y" : "N";
document.getElementById("alu-DECC").innerHTML = response_obj.alu_DECC;
document.getElementById("alu-destE-update").innerHTML = response_obj.alu_updateflag ? "Y" : "N";
document.getElementById("alu-valD").innerHTML = response_obj.alu_valD;
document.getElementById("alu-memode").innerHTML = MEMODE[response_obj.alu_memode];
document.getElementById("alu-destE").innerHTML = response_obj.alu_destE.toString(16).toUpperCase() + " (" + REGISTERS[response_obj.alu_destE] + ")";
document.getElementById("alu-destM").innerHTML = response_obj.alu_destM.toString(16).toUpperCase() + " (" + REGISTERS[response_obj.alu_destM] + ")";

// memory
document.getElementById("memory-mode").innerHTML = MEMODE[response_obj.memory_memode];
document.getElementById("memory-valE").innerHTML = response_obj.memory_valE;
document.getElementById("memory-valM").innerHTML = response_obj.memory_valM;
document.getElementById("memory-valD").innerHTML = response_obj.memory_valD;
document.getElementById("memory-destE").innerHTML = response_obj.alu_destE.toString(16).toUpperCase() + " (" + REGISTERS[response_obj.memory_destE] + ")";
document.getElementById("memory-destM").innerHTML = response_obj.alu_destE.toString(16).toUpperCase() + " (" + REGISTERS[response_obj.memory_destM] + ")";
document.getElementById("memory-destE-update").innerHTML = response_obj.memory_updateflag ? "Y" : "N";

// write back
document.getElementById("write-back-destE").innerHTML = response_obj.wb_destE.toString(16).toUpperCase() + " (" + REGISTERS[response_obj.wb_destE] + ")";
document.getElementById("write-back-destM").innerHTML = response_obj.wb_destM.toString(16).toUpperCase() + " (" + REGISTERS[response_obj.wb_destM] + ")";
document.getElementById("write-back-valE").innerHTML = response_obj.wb_valE;
document.getElementById("write-back-valM").innerHTML = response_obj.wb_valM;
document.getElementById("write-back-update").innerHTML = response_obj.wb_updateflag ? "Y" : "N";