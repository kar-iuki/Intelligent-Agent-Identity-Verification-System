import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const dir=path.dirname(fileURLToPath(import.meta.url));
const root=path.dirname(dir);
const p=Presentation.create({slideSize:{width:1280,height:720}});
const C={paper:'#F4F5EF',ink:'#17201B',green:'#274534',deep:'#101513',sage:'#D5F98B',muted:'#536059',line:'#CAD1C9',soft:'#E5EBDF',white:'#FFFFFF',rust:'#9C553A'};
const bg=await fs.readFile(path.join(root,'.verity-cover-build/assets/verity-fingerprint-cover.png'));
const evaluation=JSON.parse(await fs.readFile(path.join(root,'backend/src/data/model-evaluation-3.1.1.json'),'utf8'));
const comparison=JSON.parse(await fs.readFile(path.join(root,'ai-service/ml/experiments/face_review/comparison_models.json'),'utf8'));
const notes=[];
function text(s,t,x,y,w,h,size=24,color=C.ink,bold=false,align='left'){
 const sh=s.shapes.add({geometry:'textbox',name:t.slice(0,70),position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 sh.text=t;sh.text.style={fontSize:size,typeface:'Aptos',color,bold,alignment:align,verticalAlignment:'top',insets:0,autoFit:'none',wrap:'square'};return sh;
}
function line(s,x,y,w,color=C.line,width=1){return s.shapes.add({geometry:'line',position:{left:x,top:y,width:w,height:0},line:{fill:color,width}});}
function rect(s,x,y,w,h,fill=C.green,stroke=fill){return s.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:stroke,width:1}});}
function arrow(s,x1,y,x2,color=C.green,dashed=false){return s.shapes.add({geometry:'connector',kind:'straight',position:{left:Math.min(x1,x2),top:y,width:Math.abs(x2-x1),height:0},line:{fill:color,width:1.7,style:dashed?'dashed':'solid'},...(x2>x1?{tail:{type:'triangle',width:'sm',length:'sm'}}:{head:{type:'triangle',width:'sm',length:'sm'}})});}
function box(s,title,body,x,y,w,h,{dark=false,size=23}={}){const b=rect(s,x,y,w,h,dark?C.green:C.paper,dark?C.green:C.line);text(s,title,x+20,y+18,w-40,34,25,dark?C.paper:C.green,true);text(s,body,x+20,y+60,w-40,h-68,size,dark?C.paper:C.ink);return b;}
function connect(s,a,b,from='right',to='left',dashed=false){return s.shapes.connect(a,b,{fromSide:from,toSide:to,kind:from==='right'&&to==='left'?'straight':'elbow',line:{fill:C.green,width:2,style:dashed?'dashed':'solid'},tail:{type:'triangle',width:'sm',length:'sm'}});}
function table(s,values,x,y,w,h,widths,size=20,{highlight=[]}={}){
 const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,columnWidths:widths,values});
 t.borders.assign({fill:C.line,width:0.7,style:'solid'});
 t.cells.block({row:0,column:0,rowCount:values.length,columnCount:values[0].length}).assign({fill:C.paper,textStyle:{typeface:'Aptos',fontSize:size,color:C.ink},margins:{top:9,bottom:9,left:12,right:12},anchor:'center'});
 t.cells.block({row:0,column:0,rowCount:1,columnCount:values[0].length}).assign({fill:C.green,textStyle:{typeface:'Aptos',fontSize:size,color:C.paper,bold:true}});
 for(let r=0;r<values.length;r++) t.rows[r].height=h/values.length;
 for(const r of highlight)t.cells.block({row:r,column:0,rowCount:1,columnCount:values[0].length}).assign({fill:C.soft,textStyle:{bold:true,color:C.green}});
 return t;
}
function base(title,section,{dark=false,smallTitle=false}={}){const s=p.slides.add();s.background.fill=dark?C.deep:C.paper;const n=p.slides.items.length;const ink=dark?C.paper:C.ink; text(s,section,64,28,1000,25,17,dark?C.sage:C.muted);text(s,title,64,73,1152,102,smallTitle?40:46,ink,false);line(s,64,667,1152,dark?'#48554B':C.line);text(s,'Verity  /  Final project defence',64,681,1040,20,13,dark?'#C4CEC4':C.muted);text(s,String(n).padStart(2,'0'),1160,679,56,22,15,dark?C.sage:C.green,false,'right');return s;}
function source(s,t,dark=false){text(s,t,64,638,1152,23,14,dark?'#C4CEC4':C.muted);}
function note(s,t,ref){const full=t+'\n\nSources: '+ref; s.speakerNotes.text=full;notes.push({slide:p.slides.items.length,text:full});}
function row(s,n,title,body,y,{x=64,w=1152,h=82}={}){text(s,String(n).padStart(2,'0'),x,y,58,40,25,C.green);text(s,title,x+74,y,w-74,34,26,C.ink,true);text(s,body,x+74,y+37,w-74,h-37,22,C.muted);if(y+h<625)line(s,x,y+h,w);}

const detailed=JSON.parse(await fs.readFile(path.join(root,'.verity-defence-build/speaker-notes.json'),'utf8'));
function detail(...numbers){return numbers.map(n=>`DEFENCE REFERENCE ${n}\n${detailed.find(x=>x.slide===n).text}`).join('\n\n')
 .replace('The slide preserves all five approved specific objectives, expressed with their completed evidence.','The five approved specific objectives cover registration practice, verification risks, existing KYC technologies, system development and validation.')
 .replace('The right table is supplementary saved evidence','The additional model comparison is supplementary saved evidence')
 .replace('A valid-score threshold fallback is described on the next slide.','The valid-score threshold fallback is documented below.')
 .replace('This slide presents recorded evidence; there is no system-demonstration slide.','These are recorded test results, separate from the live demonstration.');}

// 1. CS2 cover: all required identifiers, with the user-confirmed class.
{
 const s=p.slides.add();s.background.fill=C.deep;
 s.images.add({blob:bg,contentType:'image/png',alt:'Verity dark-green fingerprint artwork',fit:'cover',position:{left:0,top:0,width:1280,height:720}});
 text(s,'Final project defence  /  November 2026',76,54,1000,36,24,C.sage);
 text(s,'VERITY',64,133,760,160,136,C.paper,true);
 text(s,'Intelligent Agent\nIdentity Verification System',76,313,790,116,42,C.paper);
 text(s,'Isaac Kariuki Irungu  ·  151442  ·  ICS 4D',76,505,1000,36,24,C.paper,true);
 text(s,'Supervisor: Dr. Stephen Obonyo',76,547,1000,33,23,C.paper);
 text(s,'Capstone  /  BSc Informatics and Computer Science',76,588,1100,33,22,C.paper);
 text(s,'Strathmore University',76,629,850,32,23,C.paper);
 note(s,'PRESENTATION ROUTE\nThe CS2 guide recommends approximately three minutes of introductory slides and twelve minutes for demonstration and evidence, subject to the panel’s allocation. Introduce the project in about fifteen seconds, then cover the problem, objective and architecture. Slide 5 is the cue to switch to the application. Keep slide 6 for the closing.\n\nThe user confirmed ICS 4D. The project type is Capstone. The fingerprint is brand artwork; the system does not collect fingerprints.\n\n'+detail(1),'CS Project II Final Defense Slide Guide, supplied DOCX; final report v3.1.1 cover; user-provided class.');
}
// 2. Specific affected parties, failure of the current approach and report evidence.
{
 const s=base('Problem statement and justification','Why Verity was developed');
 text(s,'Remote agents need\nverified identities\nbefore platform access.',64,199,620,182,47,C.green);
 text(s,'SalesMesh uses independent agents beyond direct supervision. Manual document checks cannot consistently establish who is present or prevent impersonation and duplicate registration.',64,430,580,170,27);
 const items=[['Document consistency','Do the ID details match the registration?'],['Presence and identity','Is the person live and the face a match?'],['Enforced access','Does the recorded decision control entry?']];
 items.forEach((a,i)=>{const y=196+i*111;text(s,a[0],748,y,468,36,27,C.green,true);text(s,a[1],748,y+43,468,61,24,C.muted);if(i<2)line(s,748,y+96,468);});
 text(s,'Evidence from the report',748,547,468,31,23,C.green,true);
 text(s,'An unreadable card capture stopped before a decision; recapture was required.',748,586,468,55,22);
 source(s,'Sources: final report §§1.2–1.4; hosted workflow, 5 November 2026 (v3.1.0)');
 note(s,'DELIVERY — about 45 seconds.\nIdentify the affected platform, remote agents and customers. Manual document inspection alone cannot consistently connect registration data, a matching person and a live capture to an enforced access decision. Explain that the project integrates these separate questions. The report’s hosted case gives a concrete reason for a capture-quality gate: the first card image was too small for OCR, the system requested recapture and stored no decision. On the second submission the workflow completed. This is one observed case, not a measured prevalence estimate or fraud-reduction rate.\n\nRELATED WORK AND JUSTIFICATION\n'+detail(2,3,5,6),'Final report Chapters 1–2 and Table 5.11.');
}
// 3. Exact approved objective and an exact report research question.
{
 const s=base('Objective and research question','What the project set out to establish',{dark:true});
 text(s,'Approved general objective',64,189,1152,36,25,C.sage,true);
 text(s,'To develop an Intelligent Agent Identity Verification System that enhances identity verification, strengthens onboarding security, and controls platform access within distributed agent onboarding environments.',64,243,1120,152,34,C.paper);
 line(s,64,425,1152,'#48554B');
 text(s,'Research question · evaluation focus',64,462,1152,36,25,C.sage,true);
 text(s,'How effective is the developed Intelligent Agent Identity Verification System when tested and validated, and how accurate is its decision model?',64,516,1120,113,33,C.paper);
 source(s,'Source: final report, General Objective and Research Question 5',true);
 note(s,'DELIVERY — about 35 seconds.\nState the approved objective without changing its meaning. The report contains five research questions rather than a single designated main question. This presentation selects the exact fifth question as the evaluation focus because the completed-system demonstration and held-out model results address it directly. Do not describe this selection as a newly approved research question.\n\nThe demonstration links identity capture to a recorded decision and access state. The synthetic experiment addresses decision-model accuracy; it does not establish operational effectiveness for real applicants. The core development objective was achieved, while full testing and amended requirements remain partial.\n\nSPECIFIC OBJECTIVES AND ACHIEVEMENTS\n'+detail(4,16),'Final report General Objective, Research Questions, Table 5.17 and Chapter 6.');
}
// 4. Native shapes and connectors: training evidence, deployed path and persistence.
{
 const s=base('System architecture','Trace one verification request');
 text(s,'Offline model development',64,181,1152,32,25,C.green,true);
 text(s,'LFW, NUAA and MIDV-500 measurements → synthetic scores\n7,000 training / 1,500 development / 3,000 evaluation cases',64,224,1152,61,24);
 const ui=box(s,'Vue / Vercel','Profile details\nID + live selfie',64,321,190,174,{size:22});
 const api=box(s,'Express API','Token + role checks\nAI orchestration\nStore decisions',297,321,219,174,{dark:true,size:21});
 const ai=box(s,'Flask / Azure','Quality → OCR, face, liveness\nSix scores → scaling\nRBF SVM v3.1.1',559,321,367,174,{size:22});
 const outcome=box(s,'Outcome','Verified → access\nReview → admin\nRejected → denied',969,321,247,174,{size:21});
 connect(s,ui,api);connect(s,api,ai);connect(s,ai,outcome);
 const db=rect(s,297,558,629,62,C.soft,C.line);
 text(s,'Supabase · Auth, PostgreSQL and private image storage',311,576,601,32,22,C.green);
 connect(s,api,db,'bottom','top');
 text(s,'Pretrained image models;\nproject-trained SVM.',969,552,247,70,23,C.muted);
 source(s,'Deployment: Vercel + Render + Azure + Supabase. Recorded AI allocation: 4 vCPU / 8 GiB.');
 note(s,'DELIVERY — about 70–85 seconds.\nTrace an ID and live selfie from Vue through Express to the Flask quality gate. Suitable captures proceed to OCR, facial matching and liveness. Six measurements are scaled with the training-fitted scaler and passed to the RBF SVM. Express persists scores, decision basis and access state in Supabase. Verified cases receive access; Review requires an administrator; rejected cases are denied. Requests between backend and AI use an API key. Explain the quality gate as one concrete design choice: unsuitable evidence must be recaptured before downstream processing.\n\nTRAINED VERSUS PRETRAINED\nThe project trained the six-score classifier. It used EasyOCR, ArcFace through InsightFace buffalo_l and Silent-Face MiniFASNet resources as provided. MediaPipe supplies a separate random left/right head-turn check in the browser. Raw features are face similarity, liveness, OCR identity-text agreement, blur, brightness and contrast. Fingerprints are not an input.\n\nDEPLOYMENT AND RESOURCES\nFrontend: Vercel; application API: Render; AI: Azure Container Apps; identity/database/storage: Supabase. The report records 4 vCPU and 8 GiB for AI, not a measured minimum, cost or peak-memory benchmark. GitHub Actions published the v3.1.1 container to GHCR on 19 November 2026. The report shows matching saved/live version labels; the fully measured hosted run was earlier v3.1.0.\n\nFULL TECHNICAL REFERENCE\n'+detail(7,8,9,10,11,12,15),'Final report Chapters 3–5, Figure 4.4 and Appendix 2; v3.1.1 scaler and model evidence.');
}
// 5. Demonstration cue plus compact, actual evaluation and edge-case evidence.
{
 const s=base('From identity evidence to platform access','Demonstration of the developed solution',{smallTitle:true});
 const steps=[['01','Capture identity','Profile, ID and live selfie'],['02','Process evidence','Quality gate and six scores'],['03','Record the decision','Outcome, basis and audit'],['04','Inspect access','Agent and admin views']];
 steps.forEach(([n,a,b],i)=>{const x=64+i*296;text(s,n,x,192,50,33,22,C.green);text(s,a,x,237,272,34,25,C.green,true);text(s,b,x,282,272,55,21,C.muted);});
 line(s,64,354,1152);
 text(s,'Accuracy · 3,000 held-out synthetic cases',64,378,610,34,24,C.green,true);
 s.charts.add('bar',{position:{left:55,top:419,width:575,height:203},categories:['v3.1.0','v3.1.1'],series:[{name:'Accuracy',values:[0.759333333333,0.860666666667],fill:C.green}],barOptions:{direction:'column',grouping:'clustered',gapWidth:75},hasLegend:false,xAxis:{textStyle:{typeface:'Aptos',fontSize:19,fill:C.ink},line:{fill:C.line,width:1}},yAxis:{min:0,max:1,majorUnit:0.25,numberFormatCode:'0%',textStyle:{typeface:'Aptos',fontSize:16,fill:C.muted},majorGridlines:{fill:C.line,width:0.7},line:{fill:'none',width:0}},dataLabels:{showValue:true,position:'outEnd',numberFormatCode:'0.00%',textStyle:{typeface:'Aptos',fontSize:20,fill:C.green}},chartFill:C.paper,plotAreaFill:C.paper});
 text(s,'Observed recovery',704,378,512,35,25,C.green,true);
 text(s,'Small card image → recapture before a decision. Hosted case: 5 Nov 2026, v3.1.0.',704,421,512,79,24);
 text(s,'Important limitation',704,519,512,35,25,C.rust,true);
 text(s,'157 / 1,200 non-Verified labels were incorrectly verified. Real-applicant accuracy remains unestablished.',704,562,512,74,23);
 source(s,'Sources: final report Tables 5.11–5.15; saved v3.1.1 evaluation. Current model macro F1: 0.8211.');
 note(s,'DEMONSTRATION — switch to Verity immediately; use the panel’s allocation (the guide suggests about twelve minutes).\n\nREHEARSAL AND SETUP\nUse a tested build, a consenting test participant and the project’s approved sample evidence. Sign in before presenting. Keep an agent browser and a separate administrator browser ready, with passwords kept in a password manager. Verify the current deployment before the defence. If unavailable, use a tested local build or clearly label report evidence as recorded backup. This presentation does not claim a fresh deployment test was performed while authoring the slides.\n\nSCENARIO: AGENT COMPLETES IDENTITY VERIFICATION\n1. Open the agent workflow and explain the profile details being compared with the ID.\n2. Capture or upload the document and complete live selfie capture, including the browser head-turn challenge. Show one safe capture-quality failure or recorded recapture example, then recover with suitable evidence. Do not promise that every deliberately poor input will trigger the same error.\n3. Submit. Show the recorded scores, decision basis and model version. Explain OCR agreement, face match and liveness as separate evidence.\n4. Show the resulting agent access state. If the actual result is Review or Rejected, explain it honestly rather than trying to force an approval.\n5. In the administrator browser, inspect the same request, linked scores, evidence and audit trail. Demonstrate an administrator decision only in a prepared, authorised test case. The report’s hosted evidence did not exercise the manual-review or rejection branches, so distinguish implemented paths from previously observed results.\n6. Open the model evaluation view and compare the two versions on the same revised 3,000 synthetic cases. Explain 86.07% accuracy, macro F1 0.8211 and the consequential false-approval count. The 157 errors have 1,200 non-Verified labels as their denominator.\n7. State one operational limitation and the next validation step: independently labelled real applicants and representative capture/attack conditions.\n\nBACKUP EVIDENCE\nThe recorded 5 November 2026 v3.1.0 case requested recapture for a card too small for OCR, then verified the second submission, granted access and retained twelve audit events. The 13.6-second interval is one observation, not a latency benchmark. Local 46/46 tests are dated 23 October 2026 and must not be described as a full v3.1.1 regression.\n\nMODEL AND TEST DETAIL\n'+detail(13,14),'CS2 defence guide; final report §§5.4–5.6; saved model-evaluation-3.1.1.json and supplementary comparison_models.json.');
}
// 6. Requested closing retained after the five-slide CS2 structure.
{
 const s=p.slides.add();s.background.fill=C.deep;
 s.images.add({blob:bg,contentType:'image/png',alt:'Verity dark-green fingerprint background',fit:'cover',position:{left:0,top:0,width:1280,height:720}});
 text(s,'Thank You',64,270,950,180,116,C.paper);
 s.speakerNotes.text='';
}
await fs.writeFile(path.join(dir,'speaker-notes.json'),JSON.stringify(notes,null,2));
await (await PresentationFile.exportPptx(p)).save(path.join(dir,'draft.pptx'));
await fs.writeFile(path.join(dir,'slide-layouts.json'),JSON.stringify(await p.inspect({kind:'slide,textbox,table,chart',maxChars:100000}),null,2));
console.log(JSON.stringify({slides:p.slides.items.length,draft:path.join(dir,'draft.pptx')}));

