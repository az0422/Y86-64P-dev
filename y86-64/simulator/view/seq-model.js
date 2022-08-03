
// fetch
fetch_data = response_obj["fetch"]

document.getElementById("fetch-buffer").innerHTML = fetch_data["buff"];
document.getElementById("fetch-pc").innerHTML = (fetch_data["pct"] != -1 ? fetch_data["pct"] : 0).toString(16).toUpperCase();
document.getElementById("fetch-opcode").innerHTML = fetch_data["opcode"].toString(16).toUpperCase().padStart(2, "0");
document.getElementById("fetch-rA").innerHTML = fetch_data["rA"].toString(16).toUpperCase() + " (" + REGISTERS[fetch_data["rA"]] + ")";
document.getElementById("fetch-rB").innerHTML = fetch_data["rB"].toString(16).toUpperCase() + " (" + REGISTERS[fetch_data["rB"]] + ")";
document.getElementById("fetch-constant").innerHTML = fetch_data["const"];

// decode
decode_data = response_obj["decode"]

document.getElementById("decode-valA").innerHTML = decode_data["valA"];
document.getElementById("decode-valB").innerHTML = decode_data["valB"];
document.getElementById("decode-valD").innerHTML = decode_data["valD"];
document.getElementById("decode-srcA").innerHTML = decode_data["srcA"].toString(16).toUpperCase() + " (" + REGISTERS[decode_data["srcA"]] + ")";
document.getElementById("decode-srcB").innerHTML = decode_data["srcB"].toString(16).toUpperCase() + " (" + REGISTERS[decode_data["srcB"]] + ")";
document.getElementById("decode-srcD").innerHTML = decode_data["srcD"].toString(16).toUpperCase() + " (" + REGISTERS[decode_data["srcD"]] + ")";
document.getElementById("decode-destE").innerHTML = decode_data["destE"].toString(16).toUpperCase() + " (" + REGISTERS[decode_data["destE"]] + ")";
document.getElementById("decode-destM").innerHTML = decode_data["destM"].toString(16).toUpperCase() + " (" + REGISTERS[decode_data["destM"]] + ")";
document.getElementById("decode-decode-CC").innerHTML = decode_data["DECC"];
document.getElementById("decode-memory-mode").innerHTML = MEMODE[decode_data["memode"]];
document.getElementById("decode-ALU-mode").innerHTML = ALUMODE[decode_data["alumode"]];
document.getElementById("decode-alu-ccupdate").innerHTML = decode_data["ccupdate"] ? "Y" : "N";

// ALU
alu_data = response_obj["alu"]

document.getElementById("alu-valA").innerHTML = alu_data["valA"];
document.getElementById("alu-valB").innerHTML = alu_data["valB"];
document.getElementById("alu-mode").innerHTML = ALUMODE[alu_data["alumode"]];
document.getElementById("alu-valE").innerHTML = alu_data["valE"];
document.getElementById("alu-ALUCC").innerHTML = alu_data["ALUCC"];
document.getElementById("alu-ccupdate").innerHTML = alu_data["ccupdate"] ? "Y" : "N";
document.getElementById("alu-DECC").innerHTML = alu_data["DECC"];
document.getElementById("alu-destE-update").innerHTML = alu_data["updateflag"] ? "Y" : "N";

// memory
document.getElementById("memory-mode").innerHTML = MEMODE[response_obj.memory_memode];
document.getElementById("memory-valE").innerHTML = response_obj.memory_valE;
document.getElementById("memory-valM").innerHTML = response_obj.memory_valM;
document.getElementById("memory-valD").innerHTML = response_obj.memory_valD;

// write back
document.getElementById("write-back-destE").innerHTML = response_obj.wb_destE.toString(16).toUpperCase() + " (" + REGISTERS[response_obj.wb_destE] + ")";
document.getElementById("write-back-destM").innerHTML = response_obj.wb_destM.toString(16).toUpperCase() + " (" + REGISTERS[response_obj.wb_destM] + ")";
document.getElementById("write-back-valE").innerHTML = response_obj.wb_valE;
document.getElementById("write-back-valM").innerHTML = response_obj.wb_valM;
document.getElementById("write-back-update").innerHTML = response_obj.wb_updateflag ? "Y" : "N";