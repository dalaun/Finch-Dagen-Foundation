#!/usr/bin/env python3
# Usage: python3 tests/rehearsal/blind-path/make_bpmn.py rehearsal/11-blind-goal-adversarial-path.bpmn
# Generates the BPMN 2.0 lane diagram for rehearsal/11 (with diagram layout).
import sys
from xml.sax.saxutils import escape as e
LANES=[("L_D","Dalaun"),("L_B","Builder"),("L_A","Adversary checker"),("L_K","Keystone checker"),("L_G","Grader (holds the key)"),("L_C","Counsel")]
LH=150; X0=180
# id, type, lane, col, name
N=[("start","startEvent","L_D",0,"Goal and keystone claim set"),
   ("d_heldout","task","L_D",1,"Held-out cases written outside the builder; hashes committed"),
   ("b_read","task","L_B",1,"Read goal, facts, adversary library, practice set"),
   ("b_step","task","L_B",2,"Propose next step with every fact stated"),
   ("a_check","task","L_A",3,"Score every pattern: closest, fact difference, contrary authority, no whole match (BG1-BG5)"),
   ("a_gw","exclusiveGateway","L_A",4,"Step clears the adversary?"),
   ("k_check","task","L_K",5,"Same claim held; supports, blocks, silent or unresolved; agrees with facts (BG6)"),
   ("k_gw","exclusiveGateway","L_K",6,"Link blocks?"),
   ("b_src","task","L_B",7,"Name the step's key source, or mark ASSUMPTION (BG7)"),
   ("b_gw","exclusiveGateway","L_B",8,"Path complete?"),
   ("g_commit","task","L_G",9,"Key matches its commitment (GR1); held-out budget left (GR3)"),
   ("g_grade","task","L_G",10,"Right answer and every step traceable? (GR4)"),
   ("g_out","task","L_G",11,"Return pass or fail only (GR2)"),
   ("b_gw2","exclusiveGateway","L_B",12,"Pass?"),
   ("c_packet","task","L_C",13,"Receive packet: every material fact, the path, the questions (CR2, private)"),
   ("c_advise","task","L_C",14,"Advise; sign off or not (CR1, CR3)"),
   ("d_act","task","L_D",15,"Act only after the advice; reliance record kept (CR4)"),
   ("end","endEvent","L_D",16,"Step taken on the up and up")]
F=[("start","d_heldout",""),("d_heldout","b_read",""),("b_read","b_step",""),("b_step","a_check",""),("a_check","a_gw",""),
   ("a_gw","b_step","No: revise the step"),("a_gw","k_check","Yes"),("k_check","k_gw",""),("k_gw","b_step","Yes: revise"),
   ("k_gw","b_src","No"),("b_src","b_gw",""),("b_gw","b_step","No: next step"),("b_gw","g_commit","Yes: submit path"),
   ("g_commit","g_grade",""),("g_grade","g_out",""),("g_out","b_gw2","one bit"),("b_gw2","b_step","Fail: try a new route"),
   ("b_gw2","c_packet","Pass: hand to counsel"),("c_packet","c_advise",""),("c_advise","d_act",""),("d_act","end","")]
D=[("do_practice","Practice set K1-K33, SK1-SK16 (public)","L_B",0,"b_read","in"),
   ("do_key","Held-out key (secret, verifier environment)","L_G",8,"g_commit","in"),
   ("do_commit","Commitments: salted hashes (public)","L_D",2,"d_heldout","out"),
   ("do_lib","Adversary library: sets A (97-24, sham, 7701(o)) and B (4941, 4943, 4945)","L_A",2,"a_check","in"),
   ("do_log","Held-out use log","L_G",12,"g_commit","out"),
   ("do_rel","Reliance record and packet (private folder)","L_C",15,"c_packet","out")]
lane_y={l:i*LH for i,(l,_) in enumerate(LANES)}
def size(t): return (36,36) if t.endswith("Event") else ((50,50) if "Gateway" in t else (130,80))
def box(n):
    i,t,l,c,_=n; w,h=size(t); x=X0+c*165+ (130-w)//2; y=lane_y[l]+(LH-h)//2; return x,y,w,h
B={n[0]:box(n) for n in N}
W=X0+17*165+60
o=['<?xml version="1.0" encoding="UTF-8"?>',
 '<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" id="Defs_blind_path" targetNamespace="http://example.org/trust-domain/rehearsal/blind-path">',
 '  <!-- Blind-goal adversarial path (rehearsal/11-blind-goal-adversarial-path.md). SYNTHETIC. Design and education, not legal or tax advice. Generated; edit the generator, not by hand. -->',
 '  <bpmn:collaboration id="Collab"><bpmn:participant id="P" name="Blind-goal adversarial path" processRef="Proc"/></bpmn:collaboration>',
 '  <bpmn:process id="Proc" isExecutable="false">','    <bpmn:laneSet id="Lanes">']
for l,name in LANES:
    o.append(f'      <bpmn:lane id="{l}" name="{e(name)}">')
    o+= [f'        <bpmn:flowNodeRef>{n[0]}</bpmn:flowNodeRef>' for n in N if n[2]==l]
    o.append('      </bpmn:lane>')
o.append('    </bpmn:laneSet>')
inc={n[0]:[] for n in N}; out={n[0]:[] for n in N}
for k,(a,b,_) in enumerate(F): out[a].append(f"f{k}"); inc[b].append(f"f{k}")
for i,t,l,c,name in N:
    kids="".join(f"<bpmn:incoming>{x}</bpmn:incoming>" for x in inc[i])+"".join(f"<bpmn:outgoing>{x}</bpmn:outgoing>" for x in out[i])
    assoc=""
    if t=="task":
        for d in D:
            if d[4]==i:
                assoc+= (f'<bpmn:dataInputAssociation id="da_{d[0]}"><bpmn:sourceRef>{d[0]}</bpmn:sourceRef></bpmn:dataInputAssociation>' if d[5]=="in"
                         else f'<bpmn:dataOutputAssociation id="da_{d[0]}"><bpmn:targetRef>{d[0]}</bpmn:targetRef></bpmn:dataOutputAssociation>')
    o.append(f'    <bpmn:{t} id="{i}" name="{e(name)}">{kids}{assoc}</bpmn:{t}>')
for k,(a,b,name) in enumerate(F):
    o.append(f'    <bpmn:sequenceFlow id="f{k}" sourceRef="{a}" targetRef="{b}"'+(f' name="{e(name)}"' if name else "")+'/>')
for d in D:
    o.append(f'    <bpmn:dataStoreReference id="{d[0]}" name="{e(d[1])}"/>')
o.append('  </bpmn:process>')
o.append('  <bpmndi:BPMNDiagram id="Dia"><bpmndi:BPMNPlane id="Plane" bpmnElement="Collab">')
o.append(f'    <bpmndi:BPMNShape id="P_di" bpmnElement="P" isHorizontal="true"><dc:Bounds x="120" y="0" width="{W-120}" height="{LH*len(LANES)}"/></bpmndi:BPMNShape>')
for l,_ in LANES:
    o.append(f'    <bpmndi:BPMNShape id="{l}_di" bpmnElement="{l}" isHorizontal="true"><dc:Bounds x="150" y="{lane_y[l]}" width="{W-150}" height="{LH}"/></bpmndi:BPMNShape>')
for i,(x,y,w,h) in B.items():
    o.append(f'    <bpmndi:BPMNShape id="{i}_di" bpmnElement="{i}"><dc:Bounds x="{x}" y="{y}" width="{w}" height="{h}"/></bpmndi:BPMNShape>')
DS={}
for d in D:
    x=X0+d[3]*165+40; y=lane_y[d[2]]+LH-48; DS[d[0]]=(x,y,50,40)
    o.append(f'    <bpmndi:BPMNShape id="{d[0]}_di" bpmnElement="{d[0]}"><dc:Bounds x="{x}" y="{y}" width="50" height="40"/></bpmndi:BPMNShape>')
def c(b): x,y,w,h=b; return x+w//2,y+h//2
for k,(a,b,_) in enumerate(F):
    (x1,y1),(x2,y2)=c(B[a]),c(B[b])
    pts=[(x1,y1),(x2,y2)] if y1==y2 or x1==x2 else [(x1,y1),(x1,y2),(x2,y2)]
    o.append(f'    <bpmndi:BPMNEdge id="f{k}_di" bpmnElement="f{k}">'+"".join(f'<di:waypoint x="{px}" y="{py}"/>' for px,py in pts)+'</bpmndi:BPMNEdge>')
for d in D:
    (x1,y1),(x2,y2)=c(DS[d[0]]),c(B[d[4]])
    o.append(f'    <bpmndi:BPMNEdge id="da_{d[0]}_di" bpmnElement="da_{d[0]}"><di:waypoint x="{x1}" y="{y1}"/><di:waypoint x="{x2}" y="{y2}"/></bpmndi:BPMNEdge>')
o+= ['  </bpmndi:BPMNPlane></bpmndi:BPMNDiagram>','</bpmn:definitions>']
open(sys.argv[1],'w').write("\n".join(o)+"\n")
