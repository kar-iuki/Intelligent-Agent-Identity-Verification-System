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

// 1. Identity, programme and project type.
{
 const s=p.slides.add();s.background.fill=C.deep;s.images.add({blob:bg,contentType:'image/png',alt:'Verity forest-green fingerprint cover artwork',fit:'cover',position:{left:0,top:0,width:1280,height:720}});
 text(s,'Final project defence  /  November 2026',76,54,1000,36,24,C.sage);
 text(s,'VERITY',64,133,760,160,136,C.paper,true);
 text(s,'Intelligent Agent\nIdentity Verification System',76,313,740,116,42,C.paper);
 text(s,'Isaac Kariuki Irungu  ·  151442',76,513,800,34,24,C.paper,true);
 text(s,'Supervisor: Dr. Stephen Obonyo',76,549,900,32,23,C.paper);
 text(s,'BSc Informatics and Computer Science  /  Capstone',76,585,1060,32,22,C.paper);
 text(s,'Strathmore University',76,621,800,31,23,C.paper);
 note(s,'Introduce the completed capstone project and the verification problem for distributed onboarding. The report identifies the student, admission number, supervisor, degree, university and November 2026 date. The fingerprint is the Verity visual identity; the application collects document and facial evidence, not fingerprints. The six-feature SVM was trained for this project. The OCR, face-embedding and anti-spoofing components use existing pretrained models.','Final project report v3.1.1, cover, abstract and §§1.5–1.6; Verity frontend/public/fingerprint-study.webp and theme.css.');
}
// 2. Context.
{
 const s=base('Introduction and background','Context');
 text(s,'Remote agents need\na verifiable identity\nbefore platform access',64,202,630,234,46,C.green);
 text(s,'SalesMesh context',790,199,420,38,25,C.green,true);
 text(s,'Independent agents register and onboard customers across regions, away from direct supervision.',790,249,420,146,27);
 line(s,790,422,420);
 text(s,'Verity’s scope',790,450,420,38,25,C.green,true);
 text(s,'Registration, identity evidence, verification, administrator review and access control.',790,500,420,116,26);
 text(s,'Document evidence, facial comparison and liveness feed one recorded decision.',64,500,620,100,29,C.muted);
 source(s,'Source: final report, Chapter 1');
 note(s,'The project originated in the SalesMesh distributed-sales setting. Independent agents can act on behalf of a platform and interact with customers, so access should depend on identity evidence. The system is a browser-based implementation for agent registration and verification. It does not cover all customer KYC, transaction monitoring or post-onboarding behavioural fraud. Registration guardrails are separate from the SVM. Do not claim that the project measured reductions in time, staff workload or fraud loss.','Final report §§1.1, 1.4 and 1.5; Chapter 6.');
}
// 3. Problem and actual failure modes.
{
 const s=base('Problem statement','Problem');
 text(s,'Weak identity checks can give an unverified agent access to customer onboarding.',64,185,1110,94,34,C.green);
 const data=[['Impersonation','A document, registration details and selfie may describe different people.'],['Presentation attacks','A face image alone cannot establish that the applicant is live.'],['Inconsistent decisions','Manual checks and isolated thresholds do not combine conflicting evidence consistently.'],['Duplicate or repeated attempts','Repeated identities and failed submissions can bypass an unstructured registration process.']];
 data.forEach((r,i)=>{const y=310+i*76;text(s,r[0],64,y,325,58,25,C.ink,true);text(s,r[1],417,y,790,60,23,C.muted);if(i<3)line(s,64,y+61,1152);});
 source(s,'Source: final report, §§1.2 and 2.3');
 note(s,'Frame the problem around the affected parties: platforms, administrators, agents and customers. A valid-looking document is insufficient without consistency and presence checks. The contribution is a coordinated, auditable workflow rather than a claim to detect every forged document or modern spoof. The report identifies these threats through literature and requirements analysis, not a measured local fraud-prevalence study.','Final report §§1.2, 2.3 and 2.6.');
}
// 4. Objectives linked to evidence.
{
 const s=base('General and specific objectives','Objectives');
 text(s,'Develop an integrated identity-verification system that strengthens onboarding security and controls agent access.',64,182,1152,85,31,C.green);
 const rows=[['Investigate registration practice','Literature and workflow analysis informed the requirements.'],['Identify verification risks','Impersonation, spoofing, duplicate identities and capture quality shaped the controls.'],['Examine KYC technologies','Reviewed platforms and academic methods informed the pipeline.'],['Develop the integrated system','Implemented registration, evidence processing, SVM decisions and administrator review.'],['Test and validate effectiveness','Completed synthetic evaluation and selected system tests; operational validation remains partial.']];
 rows.forEach((r,i)=>{const y=290+i*65;text(s,String(i+1).padStart(2,'0'),64,y,50,40,23,C.green);text(s,r[0],128,y,400,54,23,C.ink,true);text(s,r[1],556,y,660,56,22,C.muted);if(i<4)line(s,128,y+56,1088);});
 source(s,'Source: approved objectives in §1.3; achievement assessment in Table 5.17 and Chapter 6');
 note(s,'Approved main objective: To develop an Intelligent Agent Identity Verification System that enhances identity verification, strengthens onboarding security, and controls platform access within distributed agent onboarding environments. The slide preserves all five approved specific objectives, expressed with their completed evidence. The development objective was achieved for the core workflow. The testing objective was partly met, because selected local tests and synthetic experiments do not establish full operational effectiveness. Keep this distinction clear during the defence.','Final report §1.3, Table 5.17 and §§6.2.1–6.2.5.');
}
// 5. Justification.
{
 const s=base('Justification and significance','Contribution',{dark:true});
 text(s,'Identity evidence\nlinked to access',64,201,620,185,55,C.paper);
 text(s,'A traceable decision is useful only when the platform can enforce it and administrators can inspect it.',64,446,570,137,29,'#C4CEC4');
 const items=[['Practical value','Connect document, face and liveness checks to one access-control workflow.'],['Accountability','Retain scores, decision basis and audit context for administrator review.'],['Academic contribution','Provide a reproducible six-score classifier experiment and report its consequential errors.']];
 items.forEach((r,i)=>{const y=200+i*142;text(s,r[0],758,y,458,36,27,C.sage);text(s,r[1],758,y+47,458,85,24,C.paper);if(i<2)line(s,758,y+121,458,'#48554B');});
 source(s,'No measured superiority over commercial platforms or real-world fraud-prevention rate is claimed.',true);
 note(s,'The significance is the integration of verification evidence, recorded outcomes and platform access in the agent-onboarding context. Transparency here means inspectable inputs, model versions, provenance and audit records; an RBF SVM is not inherently a human-readable rule explanation. The project also reports where the model fails. In the revised evaluation, 157 of 1,200 cases labelled Manual Review or Rejected were classified as Verified. This is why the contribution includes measured limits and why human oversight remains necessary.','Final report §§1.4, 2.6, 5.6 and 6.2.6.');
}
// 6. Related work and the specific gap.
{
 const s=base('Literature review and research gaps','Related work');
 table(s,[['Evidence reviewed','What it contributes','Gap relevant to Verity'],['Advance.AI, SEON, Facia,\nJoinble, VerifyID and Jumio','Managed identity and fraud checks','Decision policies in reviewed products\nare proprietary.'],['ArcFace / InsightFace\nDeng et al. (2019)','Discriminative face embeddings','Face similarity does not validate\na document or establish liveness.'],['Liveness research\nChakraborty & Das; Long et al.','Dedicated presentation-attack detection','Generalisation varies with devices,\ncapture conditions and attack types.'],['Onboarding risk frameworks\nSirangi (2024)','Combining evidence for decisions','Behavioural and transaction signals\nmay be unavailable at registration.']],64,193,1152,343,[340,370,442],22);
 text(s,'Project response',64,567,250,35,25,C.green,true);
 text(s,'An inspectable agent-onboarding pipeline with six-score decisions, manual review and audit records.',340,564,876,66,27);
 source(s,'Source: final report, Chapter 2 and Table 2.1');
 note(s,'This is a literature comparison, not a matched trial against commercial products. The report reviewed Advance.AI, SEON, Facia.AI, Joinble, VerifyID and Jumio. It identifies closed decision policies and the integration burden for this project context. ArcFace supports embedding-based matching. Liveness studies address a separate threat and highlight domain shift. The implemented OCR score measures agreement with registration details, not document tamper detection. Verity does not perform AML screening or prove document authenticity. The project response should be described as an integration and evaluation contribution, not an unsupported claim of universal novelty or commercial superiority.','Final report §§2.4–2.7 and Table 2.1; cited studies as listed in the report.');
}
// 7. Editable conceptual framework.
{
 const s=base('Conceptual framework','Evidence to outcome');
 const input=box(s,'Identity evidence','Profile details\nID document\nLive selfie',64,218,240,215);
 const scores=box(s,'Six evidence scores','Face, liveness, OCR\nBlur, brightness, contrast',366,218,324,215);
 const model=box(s,'SVM v3.1.1','Scaled inputs\nLearned decision\nClass probabilities',752,218,244,215,{dark:true});
 connect(s,input,scores);connect(s,scores,model);
 text(s,'Recorded outcome',1032,214,184,60,24,C.green,true);
 text(s,'Verified\n\nManual Review\n\nRejected',1032,288,184,215,23);
 arrow(s,996,326,1024);
 text(s,'Quality checks first: unsuitable images require recapture.',64,450,920,30,21,C.muted);
 text(s,'Access',64,488,240,35,27,C.green,true);
 text(s,'Verified or administrator-approved cases receive access. Review cases need a human decision; rejected cases are denied.',366,484,850,105,27);
 text(s,'Registration guardrails and audit logging operate across the workflow.',64,595,1152,35,23,C.muted);
 source(s,'Source: final report, conceptual framework and §§5.3.3–5.3.4');
 note(s,'Inputs are document and facial evidence plus profile details. OpenCV performs quality checks before downstream processing and supplies raw blur, brightness and contrast. EasyOCR supplies identity-text agreement, ArcFace/InsightFace supplies face similarity and Silent-Face supplies liveness. The model combines all six scores, so similar face scores can produce different outcomes. The backend stores scores, the decision and its provenance, and links the result to access control. Manual Review is an explicit outcome requiring administrator handling. Duplicate identities, disposable email and attempt guardrails act independently of the SVM. Significant operations call the audit logger; source calls alone do not prove that every event persisted.','Final report §2.7, Figure 2.6 and §§5.3.3–5.3.4.');
}
// 8. Methodology and complete data split.
{
 const s=base('Methodology','Development and evaluation');
 text(s,'Applied AI and software engineering',64,188,1152,44,32,C.green);
 text(s,'Agile/Scrum iterations and OOAD linked requirements, design, implementation and testing.',64,241,1152,67,26);
 table(s,[['Draw','Cases','Verified / Review / Rejected','Role'],['Training','7,000','3,000 / 2,400 / 1,600','Fit scaler and classifier'],['Development','1,500','900 / 300 / 300','Examine scenarios and select model'],['Final evaluation','3,000','1,800 / 600 / 600','Evaluate frozen model and baseline']],64,334,1152,225,[238,126,396,392],23);
 text(s,'LFW, NUAA and MIDV-500 informed the score distributions.\nThe 11,500 cases and their outcome labels are synthetic.',64,579,1152,55,22,C.muted);
 source(s,'Source: final report, Chapter 3 and Table 5.6');
 note(s,'The software process used Agile/Scrum and Object-Oriented Analysis and Design. The ML method reused stored measurements from 1,000 LFW face pairs, 1,200 NUAA presentations, and 500 MIDV quality frames with MIDV OCR measurements. These informed distributions, not real three-class KYC labels. Replay-Attack was not used. Version 3.1.1 generated 11,500 cases with independent seeds 120141, 120142 and 120143. Scaling was fitted only on the 7,000 training rows and then reused with clipping for development and test. Final evaluation cases were generated after selection. The original 1,500-case v3.1.0 test set was an additional comparison and is excluded from the 11,500 total. Pretrained image models were used as provided; the project trained the decision classifier.','Final report §§3.1–3.4, §§5.3.6–5.3.7 and Table 5.6.');
}
// 9. Technologies.
{
 const s=base('Tools and technologies','Implementation');
 table(s,[['Layer','Tools','Implemented responsibility'],['Browser','Vue 3, Vite, Vue Router','Agent capture and administrator interfaces'],['Application','Node.js, Express, Socket.IO','Authenticated workflow, decisions and notifications'],['AI API','Python, Flask, Gunicorn','Image-processing and inference endpoints'],['Document evidence','OpenCV and EasyOCR','Quality measurements and identity-text agreement'],['Facial evidence','ArcFace via InsightFace; Silent-Face','Face embeddings and server-side liveness'],['Live capture','MediaPipe Tasks Vision','Random left/right head-turn check in the browser'],['Decision model','LIBSVM 3.10, RBF C-SVC','Six-input classifier v3.1.1'],['Identity and storage','Supabase; SimpleWebAuthn','Auth, PostgreSQL, private images and optional passkeys']],64,184,1152,418,[218,405,529],21);
 source(s,'Pretrained image models were integrated; the six-score SVM was trained for this project.');
 note(s,'The stack separates presentation, application coordination, image processing and persistence. Face matching uses pretrained buffalo_l resources through InsightFace. MiniFASNet resources supply Silent-Face liveness scores. The browser MediaPipe challenge is separate from the server anti-spoofing model and is not camera attestation. Optional WebAuthn stores public-key credentials; it does not give Verity the device biometric template. Hosting is Vercel for the frontend, Render for the backend, Azure Container Apps for AI, and Supabase for authentication, PostgreSQL and Storage. GitHub Actions built the container and published it to GHCR. The report records 4 vCPU and 8 GiB for Azure, not measured minimum requirements, peak memory, training time or costs. Some image-library versions were unpinned.','Final report Tables 5.1–5.2 and §§5.2.1–5.2.3.');
}
// 10. Architecture with interfaces and persistence.
{
 const s=base('System architecture','Implemented components and interfaces');
 const ui=box(s,'Browser / Vercel','Vue interface\nCapture and review',64,204,300,164);
 const api=box(s,'API / Render','Express orchestration\nToken and role checks',474,204,326,164,{dark:true});
 const ai=box(s,'AI / Azure','Flask image services\nSVM inference',910,204,306,164);
 connect(s,ui,api);connect(s,api,ai);text(s,'HTTPS',380,247,80,26,18,C.muted);text(s,'REST + API key',810,243,95,61,17,C.muted);
 const db=box(s,'Supabase','Auth + PostgreSQL + private Storage\nRequests, scores, decisions, access and audit records',344,465,596,136);
 connect(s,api,db,'bottom','top');
 text(s,'Application trust boundary',64,441,245,64,23,C.green,true);
 text(s,'Protected operations run through the backend.',64,520,230,82,22,C.muted);
 text(s,'Recorded AI allocation',987,445,229,37,21,C.green,true);text(s,'4 vCPU\n8 GiB memory',987,490,229,77,29);
 source(s,'Source: final report, Figure 4.4 and §§5.2–5.3');
 note(s,'Trace a captured document and selfie from the browser to the Express API, then to the Flask quality, OCR, face, liveness and SVM endpoints. The backend validates tokens and roles and writes relational evidence and outcome records in Supabase. Supabase authentication also participates in sign-in; the diagram shows the main protected verification flow. Backend-to-AI requests use X-API-Key and HTTPS in the hosted setup. Storage uses a private bucket with signed viewing URLs, though deployed access settings were not comprehensively tested. The report records the v3.1.1 image publication on 19 November 2026 and a matching live/report version display, while the measured hosted run was earlier v3.1.0. Separate saved evaluation from observed deployment. Do not describe 4 vCPU/8 GiB as a benchmarked minimum or invent cost.','Final report Figure 4.4, Tables 5.1–5.2, §§5.2.2–5.3.1 and Appendix 2.');
}
// 11. Editable sequence.
{
 const s=base('System sequence diagram','Verification and administrator review');
 const xs=[150,395,645,895,1144];const labels=['Agent / browser','Express API','Flask AI','Supabase','Administrator'];
 labels.forEach((lab,i)=>{text(s,lab,xs[i]-100,180,200,36,23,C.green,true,'center');s.shapes.add({geometry:'line',position:{left:xs[i],top:223,width:0,height:371},line:{fill:C.line,width:1,style:'dashed'}});});
 const messages=[[0,1,'1  Submit identity evidence'],[1,3,'2  Validate token and profile'],[1,2,'3  Process images + SVM'],[2,1,'4  Six scores and SVM result'],[1,3,'5  Store scores, decision and access'],[1,0,'6  Return outcome'],[1,4,'7  Notify review case'],[4,1,'8  Approve or reject'],[1,3,'9  Update decision, access and audit']];
 messages.forEach(([a,b,label],i)=>{const y=257+i*39;arrow(s,xs[a],y,xs[b],i>=6?C.rust:C.green,i>=6);const lo=Math.min(xs[a],xs[b]);text(s,label,lo+8,y-26,Math.abs(xs[b]-xs[a])-16,26,18,C.ink,false,'center');});
 text(s,'Quality failure requests recapture. Dashed messages apply when administrator review is required.',64,612,1152,34,22,C.muted);
 source(s,'Source: final report, Figure 4.5 and §§5.3.4–5.3.5');
 note(s,'The diagram separates user, application, AI and persistence responsibilities. The application orchestrates the quality, OCR, face and liveness calls, validates the six inputs, and obtains an SVM outcome. Quality failure stops downstream processing and requests another capture. Scores, requests, decisions and access records are separate entities. The administrator path is conditional: a review notification exposes the case, an authorised approval or rejection updates the outcome and access record, and the action is logged. The displayed sequence expresses the implemented design, not proof that all branches ran in a hosted test. The recorded hosted run exercised recapture and verification only. A valid-score threshold fallback is described on the next slide.','Final report Figure 4.5 and §§5.3.3–5.3.5.');
}
// 12. Training, input contract and rule fallback.
{
 const s=base('SVM model development and verification logic','Version 3.1.1',{smallTitle:true});
 text(s,'Learned classifier',64,184,500,40,30,C.green);
 text(s,'LIBSVM C-SVC, RBF kernel\nC = 10, gamma = 1\nTraining-only MinMax scaling\nInverse-frequency class weights',64,239,533,173,26);
 text(s,'Six inputs',64,438,510,35,26,C.green,true);
 text(s,'Face 0–100; liveness and OCR 0–1\nRaw blur; brightness 0–255\nContrast 0–127.5',64,483,540,107,24);
 text(s,'Fallback when valid scores exist\nand SVM inference is unavailable',674,183,542,77,27,C.green);
 table(s,[['Outcome','Application rule'],['Reject','Face < 50 OR live < 0.50 OR OCR < 0.40\nOR (blur < 80 AND face < 65)'],['Verify','After rejection checks: face > 80\nAND live > 0.75 AND OCR > 0.70'],['Review','All remaining valid-score cases']],674,281,542,263,[117,425],20);
 text(s,'The 25–50 face-score band is an evaluation probe, not a hard SVM rule.',64,596,1152,37,24,C.green,true);
 source(s,'Source: final report, §§5.3.5–5.3.7; accessControlService.js');
 note(s,'The v3.1.1 model is a six-input LIBSVM RBF C-SVC trained on 7,000 cases with C=10 and gamma=1. Class weights are 7000/(3 × class count): Verified 0.7778, Review 0.9722 and Rejected 1.4583. LIBSVM probability estimation is fitted during training. No hand-assigned OCR weight or fixed 25–50 review override is used. The face probe band tests learned behaviour: with OCR and liveness fixed at 1.0 across three additional quality profiles, 74/75 cases were referred and one verified. The predecessor verified all 75. Missing, non-finite, wrongly typed or out-of-range inputs fail before prediction or fallback. The application fallback is labelled placeholder_threshold, and its 0/1 outputs are not calibrated probabilities. The 5000-ms source default applies separately to model-status and prediction requests, not the whole workflow. Classifier probabilities reflect the synthetic mixture. No online learning occurs.','Final report Table 5.5, §§5.3.5–5.3.7 and §5.4.3; backend/src/services/accessControlService.js; ai-service/ml/experiments/face_review/scaler.json.');
}
// 13. Native chart and model comparison table.
{
 const s=base('Model evaluation and performance comparison','Held-out synthetic evidence',{smallTitle:true});
 const stats=[['86.07%','Accuracy'],['0.8211','Macro F1'],['69.83%','Manual Review recall']];
 stats.forEach(([v,l],i)=>{const x=64+i*394;text(s,v,x,177,365,68,51,C.green);text(s,l,x,246,365,34,23,C.muted);});
 text(s,'Same cases within each version comparison',64,302,562,31,22,C.green,true);
 const chart=s.charts.add('bar',{position:{left:58,top:337,width:552,height:252},categories:['Original (1,500)','Revised (3,000)'],series:[{name:'v3.1.0',values:[0.767333333333,0.759333333333],fill:'#9AA99B'},{name:'v3.1.1',values:[0.673333333333,0.860666666667],fill:C.green}],barOptions:{direction:'column',grouping:'clustered',gapWidth:90},hasLegend:true,legend:{position:'bottom',overlay:false,textStyle:{typeface:'Aptos',fontSize:17,fill:C.ink}},xAxis:{textStyle:{typeface:'Aptos',fontSize:17,fill:C.ink},line:{fill:C.line,width:1}},yAxis:{min:0,max:1,majorUnit:0.25,numberFormatCode:'0%',textStyle:{typeface:'Aptos',fontSize:15,fill:C.muted},majorGridlines:{fill:C.line,width:0.7},line:{fill:'none',width:0}},dataLabels:{showValue:true,position:'outEnd',numberFormatCode:'0.0%',textStyle:{typeface:'Aptos',fontSize:17,fill:C.ink}},chartFill:C.paper,plotAreaFill:C.paper});
 text(s,'Additional comparison on the revised 3,000 cases',648,302,568,31,21,C.green,true);
 const models=comparison.models;
 const rows=[['Model','Accuracy','Macro F1','Incorrect\napprovals'],['Six-input SVM',(models.full_svm.accuracy*100).toFixed(2)+'%',models.full_svm.macro_f1.toFixed(4),String(models.full_svm.incorrect_verifications)],['Identity-only SVM',(models.identity_only_svm.accuracy*100).toFixed(2)+'%',models.identity_only_svm.macro_f1.toFixed(4),String(models.identity_only_svm.incorrect_verifications)],['Decision Tree',(models.decision_tree.accuracy*100).toFixed(2)+'%',models.decision_tree.macro_f1.toFixed(4),String(models.decision_tree.incorrect_verifications)],['Calibrated tree',(models.calibrated_decision_tree.accuracy*100).toFixed(2)+'%',models.calibrated_decision_tree.macro_f1.toFixed(4),String(models.calibrated_decision_tree.incorrect_verifications)]];
 table(s,rows,648,345,568,232,[226,104,110,128],18,{highlight:[1]});
 text(s,'157 of 1,200 non-Verified cases were incorrectly verified. Real-applicant accuracy remains unestablished.',64,600,1152,37,23,C.rust,true);
 source(s,'Source: report Tables 5.12–5.15; saved v3.1.1 evaluation and supplementary comparator results');
 note(s,'Headline evaluation: 2,582/3,000 correct, accuracy 0.8606667, macro F1 0.8211454 and weighted F1 0.8607976. Actual classes by row and predictions [Verified, Review, Rejected] by column: Verified [1668,116,16]; Review [132,419,49]; Rejected [25,80,495]. Class precision/recall/F1: Verified 0.9140/0.9267/0.9203; Review 0.6813/0.6983/0.6897; Rejected 0.8839/0.8250/0.8534. Incorrect approvals equal 132+25=157 of 1,200 non-Verified labels, 13.08%; among 1,825 predicted verifications they are 8.60%. The denominators differ. On revised cases v3.1.0 accuracy was 75.93%, macro F1 0.6708; v3.1.1 accuracy 86.07%, macro F1 0.8211. On original cases they were 76.73%/0.6794 versus 67.33%/0.6505. Original Verified-to-Review counts increased from 62/900 to 260/900. The right table is supplementary saved evidence beyond the final report’s earlier comparator discussion. It uses the same revised splits. The calibrated tree has nine more correct predictions, but its paired accuracy-difference 95% interval is −0.50 to +1.10 percentage points. Do not claim clear superiority. Predicted review counts: full SVM 615, identity SVM 615, tree 684, calibrated tree 599. Twenty-repeat permutation macro-F1 decreases: face 0.294426, liveness 0.153926, OCR 0.101878, blur 0.005161, contrast 0.003708, brightness 0.000780. These are aggregate sensitivities, not individual-decision percentage weights.','Final report §§5.4.3–5.4.4 and Tables 5.12–5.15; backend/src/data/model-evaluation-3.1.1.json; ai-service/ml/experiments/face_review/comparison_models.json and README.md.');
}
// 14. Keep dated software evidence separate from model accuracy.
{
 const s=base('System testing and results','Evidence and its limits');
 table(s,[['Evidence','Recorded result','What it establishes'],['Local automated tests\n23 October 2026','46 / 46 passed','Selected model contracts, backend,\nretention, passkeys and frontend checks'],['Stored live records\n21 September–3 October','12 requests, 12 score records\n9 decisions: 7 Verified, 2 Rejected','Persistence and linked outcomes;\n3 requests remained pending'],['Hosted workflow\n5 November 2026, v3.1.0','One completed verification\n13.6 seconds on the second submission','Recapture, verification, access grant\nand 12 stored audit events']],64,194,1152,295,[290,358,504],23);
 text(s,'Edge case observed',64,527,304,36,26,C.green,true);
 text(s,'The first card image was too small for OCR. The system requested recapture and stored no decision.',388,524,828,75,26);
 text(s,'These records do not establish a full v3.1.1 hosted regression, load test or real-world accuracy study.',64,604,1152,33,23,C.rust);
 source(s,'Source: final report, Tables 5.8–5.11 and saved test logs');
 note(s,'The 46 tests include 6 SVM contract tests, 2 experiment tests, 4 improvement tests, 2 backend decision tests, 5 retention tests, 9 passkey service tests, 1 passkey route test, 1 database migration test and 16 frontend tests. They passed on 23 October 2026, before v3.1.1. The six SVM tests were rerun after v3.1.0; the full 46 were not rerun. Live exports contained 12 requests across eight agent identifiers, nine linked decisions, five svm_model and four placeholder_threshold bases, and three pending requests. No adjudicated identity labels or historical model-version fields were present. The hosted case on 5 November used v3.1.0. Second-attempt scores were face 64.13, live 0.9998, OCR 1.0, blur 87.79, brightness 156.90, contrast 52.56. The outcome was Verified, probabilities [0.842,0.134,0.024], with access and 12 audit events. The 13.6-second interval is a single observation, not average latency. Manual review, hosted rejection, admin intervention, concurrency, comprehensive security and participant usability were not established. This slide presents recorded evidence; there is no system-demonstration slide.','Final report §§5.4.1–5.4.2, Tables 5.8–5.11; documentation/final_draft_evidence.');
}
// 15. Implemented controls distinguished from outstanding requirements.
{
 const s=base('Security, privacy and data retention','Implemented controls and remaining gaps',{smallTitle:true});
 text(s,'Implemented in source',64,189,535,40,31,C.green);
 text(s,'Bearer-token validation and role checks\nOptional passkeys and challenge validation\nDuplicate-ID and attempt guardrails\nPrivate image storage and signed URLs',64,247,535,178,25);
 text(s,'Verified-image cleanup',64,456,535,36,26,C.green,true);
 text(s,'Three Nairobi business days after the latest successful decision. Cleanup runs at startup and every 15 minutes.',64,507,535,108,24);
 text(s,'Outstanding requirements',674,189,542,40,31,C.rust);
 text(s,'Pre-collection consent and withdrawal\n30-day non-verified-image expiry\n180-day metadata lifecycle\nBackup restoration and retention proof\nProduction origins and accessible CAPTCHA',674,247,542,236,25);
 text(s,'The 30-day and 180-day periods are design requirements, not implemented controls or statutory periods.',674,511,542,107,24,C.muted);
 source(s,'Source: final report, §§5.2.2–5.3.3 and §5.6.3. No compliance certification is claimed.');
 note(s,'Security evidence is bounded. Source implements token and role checks, optional WebAuthn, registration guardrails, server-side AI credentials and signed URLs. Uploads accept JPEG/PNG up to 5 MiB per file. Attempt guardrail defaults are three counted events in a 24-hour window; three strikes lead to rejection, with administrator reset. Retention code considers the latest verified request and expires image evidence after three Monday–Friday business days in Africa/Nairobi, without holiday exclusions. It removes objects and clears file references while retaining records. Five local mocked tests passed; live deletion scheduling was not demonstrated. Amended requirements for 30-day pending/review/rejected/abandoned images and 180-day metadata expiry are incomplete. Applicable consent, notice record, backend enforcement and withdrawal handling were not found. Daily Google Drive backups were reported, but restoration, protections and the seven-day design expiry were not verified. Production-origin separation and the CAPTCHA accessible alternative remain unverified. Legal processing basis, biometric safeguards and overseas-hosting review remain unresolved in the report. No legal-compliance conclusion follows from the architecture or from hosting.','Final report §§5.2.2–5.3.3, §§5.4.1–5.4.2 and §5.6.3; documentRetentionService.js.');
}
// 16. Achievements and measured boundaries.
{
 const s=base('Conclusion, achievements and future improvements','Conclusions',{dark:true,smallTitle:true});
 text(s,'Completed contribution',64,192,550,43,31,C.sage);
 text(s,'A hosted verification workflow\nand a reproducible six-score\nSVM experiment',64,251,560,178,40,C.paper);
 text(s,'The revised model improved agreement with the revised labels, while increasing review on the original scenarios.',64,468,560,122,27,'#C4CEC4');
 const actions=[['Complete safeguards','Consent, retention, recovery and origin controls.'],['Validate real applicants','Independent labels, representative devices and attack cases.'],['Evaluate human review','Measure correction rates, workload and errors in proposed approvals.'],['Improve under controlled evidence','Offline retraining, calibration and reliability tests with versioned rollback.']];
 actions.forEach((r,i)=>{let y=194+i*105;text(s,String(i+1).padStart(2,'0'),720,y,47,37,25,C.sage);text(s,r[0],784,y,432,35,26,C.paper,true);text(s,r[1],784,y+40,432,63,22,'#C4CEC4');});
 source(s,'Current evidence supports controlled evaluation with human oversight, not autonomous operational approval.',true);
 note(s,'Close against the objectives. The project implemented and hosted the core workflow, combined pretrained image components with a trained SVM, preserved decision provenance and provided administrator handling. The synthetic findings are reproducible but do not establish real-applicant accuracy, fairness, attack resistance or operational readiness. The development objective is achieved for the core system; the full amended requirements and testing objective remain partial. The highest priorities are informed collection and retention, isolated recovery testing, origin and human-check controls, independent labelled validation, and measurement of administrator correction. Future model updates should use governed, independently checked labels, an untouched evaluation set and explicit error-cost and review-capacity criteria. Administrator decisions do not automatically become ground truth. Periodic retraining remains offline with versioning and rollback.','Final report Chapter 6, particularly §§6.2–6.4.');
}
// 17. Deliberately contains only the requested closing words.
{
 const s=p.slides.add();s.background.fill=C.deep;s.images.add({blob:bg,contentType:'image/png',alt:'Verity forest-green fingerprint background',fit:'cover',position:{left:0,top:0,width:1280,height:720}});text(s,'Thank You',64,270,950,180,116,C.paper,false);s.speakerNotes.text='';
}
await fs.writeFile(path.join(dir,'speaker-notes.json'),JSON.stringify(notes,null,2));
await (await PresentationFile.exportPptx(p)).save(path.join(dir,'draft.pptx'));
await fs.writeFile(path.join(dir,'slide-layouts.json'),JSON.stringify(await p.inspect({kind:'slide,textbox,table,chart',maxChars:200000}),null,2));
console.log(JSON.stringify({slides:p.slides.items.length,draft:path.join(dir,'draft.pptx')}));
