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
const prior=JSON.parse(await fs.readFile(path.join(root,'.verity-cs2-build/speaker-notes.json'),'utf8'));
const topics=['','Project identity','Background','Problem','Objectives','Significance','Literature and gap','Conceptual framework','Methodology','Technology','Architecture','Sequence','SVM and fallback','Evaluation','System testing','Security and retention','Conclusions'];
const timings=[];
function detail(numbers){return numbers.map(n=>`${topics[n].toUpperCase()}\n${detailed.find(x=>x.slide===n).text}`).join('\n\n')
 .replace('The slide preserves all five approved specific objectives, expressed with their completed evidence.','The approved specific objectives cover registration practice, verification risks, existing KYC technologies, system development and validation.')
 .replace('The right table is supplementary saved evidence','The additional model comparison is supplementary saved evidence')
 .replace('A valid-score threshold fallback is described on the next slide.','The application fallback is documented in the model-development notes.')
 .replace('This slide presents recorded evidence; there is no system-demonstration slide.','These are historical records, separate from the current demonstration.');}
function timed(s,seconds,script,references,extra=''){
 timings.push({slide:p.slides.items.length,seconds,spokenWords:script.split(/\s+/).length});
 note(s,`DELIVERY TARGET: ${seconds} seconds.\n\nSUGGESTED SPOKEN EXPLANATION\n${script}\n\n${extra ? extra+'\n\n' : ''}REFERENCE DETAIL — use only for follow-up questions, not as a script.\n\n${detail(references)}`,'Final project documentation v3.1.1 and associated saved evaluation/test evidence. Detailed citations appear with each topic below.');
}

// 1. Established cover and complete student identification.
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
 timed(s,10,'I am Isaac Kariuki Irungu, ICS 4D. Verity is my completed capstone project for agent identity verification and controlled platform access.',[1],
 'RUN OF SHOW\nTarget about 5 minutes of slide explanation and 8 minutes of demonstration, around 13 minutes overall. This leaves roughly 2 minutes within the guide’s 15-minute presentation slot for transitions or delays. Follow any different allocation given by the panel.\nSlides 1–7: around 3 minutes 45 seconds.\nSlide 8: 15-second setup, then an 8-minute demonstration.\nSlides 9–11: around 55 seconds.\nOnly read the short spoken explanation in each note. The longer reference section retains technical detail for questions.\n\nThe user confirmed ICS 4D. The fingerprint is brand artwork, not a biometric collected by Verity.');
}
// 2. Context, problem and significance remain one focused slide.
{
 const s=base('Problem statement and justification','Why Verity was developed');
 text(s,'Remote agents need\nverified identities\nbefore platform access.',64,199,620,182,47,C.green);
 text(s,'SalesMesh uses independent agents beyond direct supervision. Manual document checks cannot consistently establish who is present or prevent impersonation and duplicate registration.',64,430,580,170,27);
 const items=[['Document consistency','Do the ID details match the registration?'],['Presence and identity','Is the person live and the face a match?'],['Enforced access','Does the recorded decision control entry?']];
 items.forEach((a,i)=>{const y=196+i*111;text(s,a[0],748,y,468,36,27,C.green,true);text(s,a[1],748,y+43,468,61,24,C.muted);if(i<2)line(s,748,y+96,468);});
 text(s,'Evidence from the report',748,547,468,31,23,C.green,true);
 text(s,'The hosted test required recapture of an unreadable card before making a decision.',748,586,468,55,22);
 source(s,'Sources: final report §§1.2–1.4 and hosted workflow, 5 November 2026 (v3.1.0)');
 timed(s,35,'The project began with SalesMesh, where independent agents onboard customers beyond direct supervision. A document alone does not establish that the person presenting it is its owner or is live. Verity connects identity evidence to an enforceable access decision. The recorded hosted test illustrates why evidence quality matters: an unreadable card triggered recapture before the system made a decision.',[2,3,5]);
}
// 3. Preserve the exact approved objective and exact research question.
{
 const s=base('Objective and research question','What the project set out to establish',{dark:true});
 text(s,'Approved general objective',64,189,1152,36,25,C.sage,true);
 text(s,'To develop an Intelligent Agent Identity Verification System that enhances identity verification, strengthens onboarding security, and controls platform access within distributed agent onboarding environments.',64,243,1120,152,34,C.paper);
 line(s,64,425,1152,'#48554B');
 text(s,'Research question · evaluation focus',64,462,1152,36,25,C.sage,true);
 text(s,'How effective is the developed Intelligent Agent Identity Verification System when tested and validated, and how accurate is its decision model?',64,516,1120,113,33,C.paper);
 source(s,'Source: final report, General Objective and Research Question 5',true);
 timed(s,30,'The approved objective was to strengthen identity verification and onboarding security while controlling platform access. The specific objectives covered existing practice, risks, KYC technologies, implementation and validation. For this defence, I focus on the report’s evaluation question: how effective is the implemented workflow, and how accurate is its decision model? I address these using separate system tests and model experiments.',[4],
 'The report lists five research questions. This slide quotes Question 5 exactly as the evaluation focus, rather than inventing a newly approved main question. The development objective was achieved for the core workflow. Full operational validation and amended requirements remain partial.');
}
// 4. Literature and conceptual framework share a single visual argument.
{
 const s=base('Related work and the project response','Literature review and conceptual framework');
 table(s,[['Reviewed work','Contribution','Gap relevant to Verity'],['ArcFace and KYC face studies\nDeng et al.; Abraham & Paul','Face embeddings and\nportrait-to-selfie comparison','Face matching needs separate\ndocument and presence checks.'],['Liveness research\nChakraborty & Das; Long et al.','Presentation-attack\ndetection','Capture conditions and unseen\nattacks affect generalisation.'],['Managed KYC platforms\nAdvance.AI, SEON, Jumio and others','Integrated identity\nand fraud services','Reviewed decision policies\nare proprietary.']],64,185,1152,286,[375,325,452],22);
 text(s,'Verity’s conceptual framework',64,505,1152,34,25,C.green,true);
 const labels=['Identity evidence','Six evidence scores','SVM decision','Controlled access'];
 const bs=labels.map((t,i)=>{const x=64+i*304;const b=rect(s,x,554,240,64,i===2?C.green:C.soft,i===2?C.green:C.line);text(s,t,x+12,573,216,30,22,i===2?C.paper:C.green,true,'center');return b;});
 for(let i=0;i<3;i++)connect(s,bs[i],bs[i+1]);
 source(s,'Source: final report, Chapter 2 and Figure 2.6. This is a literature comparison, not a commercial benchmark.');
 timed(s,25,'The literature separates face matching from liveness and document consistency. Commercial services combine these checks, but their reviewed decision policies are proprietary. Verity’s contribution is an inspectable integration for agent onboarding: identity evidence becomes six scores, a recorded decision and controlled access, with administrator review for uncertain cases.',[6,7]);
}
// 5. Deployed architecture plus the actual technology choices.
{
 const s=base('System architecture and technologies','Implemented components');
 text(s,'Image processing and inference',64,181,1152,32,25,C.green,true);
 text(s,'OpenCV quality checks, EasyOCR text agreement, ArcFace face matching\nSilent-Face liveness, MediaPipe capture challenge and LIBSVM decisions',64,224,1152,61,24);
 const ui=box(s,'Vue / Vercel','Profile details\nID + live selfie',64,321,190,174,{size:22});
 const api=box(s,'Express API','Token + role checks\nAI orchestration\nStore decisions',297,321,219,174,{dark:true,size:21});
 const ai=box(s,'Flask / Azure','Quality gate and image checks\nSix scores and scaling\nRBF SVM v3.1.1',559,321,367,174,{size:22});
 const outcome=box(s,'Outcome','Verified: access\nReview: administrator\nRejected: denied',969,321,247,174,{size:21});
 connect(s,ui,api);connect(s,api,ai);connect(s,ai,outcome);
 const db=rect(s,297,558,629,62,C.soft,C.line);text(s,'Supabase: Auth, PostgreSQL and private image storage',311,576,601,32,22,C.green);connect(s,api,db,'bottom','top');
 text(s,'Pretrained image models\nSVM trained for Verity',969,552,247,70,23,C.muted);
 source(s,'Frontend: Vercel. Backend: Render. AI: Azure, recorded allocation 4 vCPU / 8 GiB. Storage and Auth: Supabase.');
 timed(s,35,'The browser sends identity evidence to Express, which checks authentication and coordinates the Flask AI service. Quality checks precede OCR, face matching and liveness. The classifier combines their scores, and the backend records the decision and access state in Supabase. I integrated pretrained image models and trained the decision SVM. The architecture separates image processing from application access control.',[9,10],
 'Release evidence: the report records v3.1.1 publication to GHCR on 19 November 2026 and matching saved/live version labels. The measured hosted run was v3.1.0. The recorded Azure allocation is not a measured minimum, training-time result or cost estimate.');
}
// 6. A separate model-development slide makes the methodology explainable.
{
 const s=base('Methodology and SVM decision logic','Development and model v3.1.1');
 text(s,'Applied AI and software engineering',64,188,555,40,29,C.green);
 text(s,'Agile/Scrum iterations with OOAD',64,244,555,40,25);
 text(s,'Independent synthetic draws',64,306,555,35,25,C.green,true);
 table(s,[['Draw','Cases','Role'],['Training','7,000','Fit scaler and SVM'],['Development','1,500','Select model'],['Final evaluation','3,000','Compare frozen models']],64,355,555,214,[195,105,255],21);
 text(s,'Six input measurements',691,188,525,40,29,C.green);
 text(s,'Face match, liveness, OCR agreement\nBlur, brightness and contrast',691,244,525,75,25);
 line(s,691,339,525);
 text(s,'Training-only MinMax scaling\nLIBSVM RBF: C = 10, gamma = 1\nInverse-frequency class weights',691,367,525,112,24);
 text(s,'When SVM inference is unavailable',691,511,525,35,25,C.green,true);
 text(s,'Valid scores use the threshold fallback.\nInvalid inputs fail before prediction.',691,556,525,66,23);
 source(s,'Source distributions: LFW, NUAA and MIDV-500. Generated outcome labels and scenario mixtures remain assumptions.');
 timed(s,45,'Development used Agile iterations and object-oriented analysis and design. For the model, stored measurements from LFW, NUAA and MIDV informed synthetic score distributions. Independent draws supplied seven thousand training cases, fifteen hundred development cases and three thousand final evaluation cases. Scaling used training data only. Version 3.1.1 is an RBF SVM with class weighting. Its learned decision is separate from the application’s threshold fallback when inference is unavailable.',[8,12],
 'FALLBACK REFERENCE\nReject if face < 50, liveness < 0.50, OCR < 0.40, or blur < 80 together with face < 65. Otherwise verify only if face > 80, liveness > 0.75 and OCR > 0.70. Remaining valid-score cases go to Manual Review. The basis is placeholder_threshold. Missing, malformed, non-finite or out-of-range inputs fail before fallback.\n\nThe 25–50 face-score region is an evaluation probe, not a hard runtime override. Training estimates LIBSVM class probabilities, and no online learning occurs.');
}
// 7. Native chart and table retain both the gain and the changed-scenario tradeoff.
{
 const s=base('Model evaluation and comparisons','Held-out synthetic evidence');
 const stats=[[(evaluation.accuracy*100).toFixed(2)+'%','Accuracy'],[evaluation.macro_f1.toFixed(4),'Macro F1'],[(evaluation.per_class.review.recall*100).toFixed(2)+'%','Manual Review recall']];
 stats.forEach(([v,l],i)=>{const x=64+i*394;text(s,v,x,177,365,68,51,C.green);text(s,l,x,246,365,34,23,C.muted);});
 text(s,'Same cases within each version comparison',64,302,562,31,22,C.green,true);
 s.charts.add('bar',{position:{left:58,top:337,width:552,height:252},categories:['Original (1,500)','Revised (3,000)'],series:[{name:'v3.1.0',values:[0.767333333333,0.759333333333],fill:'#9AA99B'},{name:'v3.1.1',values:[0.673333333333,0.860666666667],fill:C.green}],barOptions:{direction:'column',grouping:'clustered',gapWidth:90},hasLegend:true,legend:{position:'bottom',overlay:false,textStyle:{typeface:'Aptos',fontSize:17,fill:C.ink}},xAxis:{textStyle:{typeface:'Aptos',fontSize:17,fill:C.ink},line:{fill:C.line,width:1}},yAxis:{min:0,max:1,majorUnit:0.25,numberFormatCode:'0%',textStyle:{typeface:'Aptos',fontSize:15,fill:C.muted},majorGridlines:{fill:C.line,width:0.7},line:{fill:'none',width:0}},dataLabels:{showValue:true,position:'outEnd',numberFormatCode:'0.0%',textStyle:{typeface:'Aptos',fontSize:17,fill:C.ink}},chartFill:C.paper,plotAreaFill:C.paper});
 text(s,'Additional comparison on the revised 3,000 cases',648,302,568,31,21,C.green,true);
 const m=comparison.models;const keys=[['Six-input SVM','full_svm'],['Identity-only SVM','identity_only_svm'],['Decision Tree','decision_tree'],['Calibrated tree','calibrated_decision_tree']];
 table(s,[['Model','Accuracy','Macro F1','Incorrect\napprovals'],...keys.map(([label,k])=>[label,(m[k].accuracy*100).toFixed(2)+'%',m[k].macro_f1.toFixed(4),String(m[k].incorrect_verifications)])],648,345,568,232,[226,104,110,128],18,{highlight:[1]});
 text(s,'157 of 1,200 non-Verified labels were incorrectly verified. Real-applicant accuracy remains unestablished.',64,600,1152,37,23,C.rust,true);
 source(s,'Sources: final report Tables 5.12–5.15, saved v3.1.1 evaluation and supplementary comparator results');
 timed(s,45,'Version 3.1.1 reached 86.07 percent accuracy and a macro F1 of 0.8211 on the revised synthetic evaluation. Against the same cases, it improved on version 3.1.0, but performance fell on the original scenarios, showing the effect of changed labels. The other classifiers were close. The critical error is that 157 of 1,200 non-Verified labels received verification. These results support further controlled evaluation rather than a real-applicant accuracy claim.',[13],
 'PRESENTATION PRIORITY\nPoint to the headline result, the opposite direction on the original scenarios, and the incorrect approvals. Do not read each comparator row. The table is available for follow-up. The calibrated tree has nine additional correct predictions, with a paired 95% accuracy-difference interval from −0.50 to +1.10 percentage points. No clear superiority claim follows.');
}
// 8. Sequence and dated system evidence support one short demo setup.
{
 const s=base('System sequence and demonstration','Verification workflow and recorded tests');
 const xs=[140,380,620,860,1100], labels=['Agent','Express API','Flask AI','Records','Administrator'];
 labels.forEach((lab,i)=>{text(s,lab,xs[i]-108,190,216,36,24,C.green,true,'center');s.shapes.add({geometry:'line',position:{left:xs[i],top:236,width:0,height:250},line:{fill:C.line,width:1,style:'dashed'}});});
 const seq=[[0,1,'1  Submit evidence'],[1,2,'2  Process and classify'],[2,1,'3  Scores and outcome'],[1,3,'4  Persist decision and access'],[1,0,'5  Show access state'],[4,1,'6  Review decision, when required']];
 seq.forEach(([a,b,t],i)=>{const y=267+i*41;arrow(s,xs[a],y,xs[b],i===5?C.rust:C.green,i===5);text(s,t,Math.min(xs[a],xs[b])+8,y-26,Math.abs(xs[a]-xs[b])-16,26,18,C.ink,false,'center');});
 line(s,64,505,1152);
 const facts=[['46 / 46 tests','23 Oct 2026, earlier build'],['Recapture and access','Hosted, 5 Nov 2026, v3.1.0'],['12 audit events','One recorded hosted case']];
 facts.forEach(([v,l],i)=>{const x=64+i*394;text(s,v,x,536,365,45,31,C.green);text(s,l,x,591,365,33,21,C.muted);});
 source(s,'Source: report Figure 4.5 and Tables 5.8–5.11. These records do not establish a full v3.1.1 hosted regression.');
 const demo=prior.find(x=>x.slide===5).text.split('REHEARSAL AND SETUP')[1].split('MODEL AND TEST DETAIL')[0];
 timed(s,15,'I will now demonstrate one verification workflow, a recapture case and the resulting agent and administrator views. The figures below are dated evidence from the report, separate from today’s demonstration.',[11,14],
 'DEMONSTRATION BUDGET: 8 minutes.\n0:00–0:45: introduce the signed-in agent and test case.\n0:45–2:30: capture the ID and selfie, including the browser challenge.\n2:30–3:45: show a prepared capture-quality error and recovery, or clearly labelled recorded evidence.\n3:45–5:15: submit and inspect actual scores, decision basis, model version and access.\n5:15–6:45: inspect the same request and audit trail in the administrator browser.\n6:45–8:00: explain the outcome, acknowledge the evidence limit and return to slide 9.\n\nDo not repeat the model table in the demo. If a delay consumes the buffer, move to labelled backup evidence instead of waiting indefinitely.\n\nREHEARSAL AND SETUP'+demo);
}
// 9. Report implementation and outstanding privacy requirements accurately.
{
 const s=base('Security, privacy and data retention','Implemented controls and remaining gaps',{smallTitle:true});
 text(s,'Implemented in source',64,189,535,40,31,C.green);
 text(s,'Bearer-token validation and role checks\nOptional passkeys and challenge validation\nDuplicate-ID and attempt guardrails\nPrivate image storage and signed URLs',64,247,535,178,25);
 text(s,'Verified-image cleanup',64,456,535,36,26,C.green,true);
 text(s,'Three Nairobi business days after the latest successful decision. Cleanup runs at startup and every 15 minutes.',64,507,535,108,24);
 text(s,'Outstanding requirements',674,189,542,40,31,C.rust);
 text(s,'Pre-collection consent and withdrawal\n30-day non-verified-image expiry\n180-day metadata lifecycle\nBackup restoration and retention proof\nProduction origins and accessible CAPTCHA',674,247,542,236,25);
 text(s,'The 30-day and 180-day periods remain design requirements. The report does not establish their implementation.',674,511,542,107,24,C.muted);
 source(s,'Source: final report §§5.2.2–5.3.3 and §5.6.3. These project retention periods are not statutory periods.');
 timed(s,25,'The source implements role checks, optional passkeys, private images and registration guardrails. Verified images have a three-business-day cleanup policy. The report also records unfinished work: consent handling, expiry for other images and metadata, and recovery verification. I therefore distinguish implemented controls from the remaining requirements and do not claim compliance certification.',[15]);
}
// 10. Close the objectives and give the next work a clear priority.
{
 const s=base('Achievements and next steps','Conclusion',{dark:true});
 text(s,'Completed contribution',64,192,550,43,31,C.sage);
 text(s,'A hosted verification workflow\nand a reproducible six-score\nSVM experiment',64,251,560,178,40,C.paper);
 text(s,'Core development is complete. Broader operational validation and the amended safeguards remain partial.',64,468,560,122,27,'#C4CEC4');
 const actions=[['Complete safeguards','Consent, retention, recovery and origin controls.'],['Validate real applicants','Independent labels, representative devices and attack cases.'],['Evaluate human review','Measure correction rates, workload and approval errors.'],['Improve with controlled tests','Offline retraining, calibration and versioned rollback.']];
 actions.forEach((r,i)=>{const y=194+i*105;text(s,String(i+1).padStart(2,'0'),720,y,47,37,25,C.sage);text(s,r[0],784,y,432,35,26,C.paper,true);text(s,r[1],784,y+40,432,63,22,'#C4CEC4');});
 source(s,'Source: final report, Chapter 6. Current evidence supports controlled evaluation with human oversight.',true);
 timed(s,25,'Verity delivers the core verification and access workflow and a reproducible model experiment. The development objective is achieved, while operational validation remains partial. The next priorities are completing the safeguards, evaluating independently labelled applicants and measuring administrator correction. Further model updates should remain controlled, versioned and supported by untouched evaluation data.',[16]);
}
// 11. Only the requested closing words.
{
 const s=p.slides.add();s.background.fill=C.deep;
 s.images.add({blob:bg,contentType:'image/png',alt:'Verity dark-green fingerprint background',fit:'cover',position:{left:0,top:0,width:1280,height:720}});
 text(s,'Thank You',64,270,950,180,116,C.paper);
 s.speakerNotes.text='Thank you. Target: 5 seconds.';
 timings.push({slide:11,seconds:5,spokenWords:2});
}
await fs.writeFile(path.join(dir,'speaker-notes.json'),JSON.stringify(notes,null,2));
await fs.writeFile(path.join(dir,'timing-plan.json'),JSON.stringify({slides:timings,slideSeconds:timings.reduce((a,x)=>a+x.seconds,0),demoSeconds:480,totalSeconds:timings.reduce((a,x)=>a+x.seconds,0)+480},null,2));
await (await PresentationFile.exportPptx(p)).save(path.join(dir,'draft.pptx'));
console.log(JSON.stringify({slides:p.slides.items.length,draft:path.join(dir,'draft.pptx')}));

