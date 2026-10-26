import csv,json,collections,datetime
from pathlib import Path
base=Path(r'C:\Users\ikari\Downloads')
names=['Supabase Snippet Untitled query.csv','Supabase Snippet Untitled query (1).csv','Supabase Snippet Untitled query (2).csv']
dec,req,scores=[list(csv.DictReader((base/n).open(encoding='utf-8-sig'))) for n in names]
rmap={r['request_id']:r for r in req};smap={r['request_id']:r for r in scores}
def counts(rows,key):return dict(collections.Counter(r[key] for r in rows))
summary={'source_files':names,'request_count':len(req),'unique_agents':len({r['agent_id'] for r in req}),'score_count':len(scores),'decision_count':len(dec),'request_status':counts(req,'status'),'decision_status':counts(dec,'final_decision'),'decision_basis':counts(dec,'decision_basis'),'request_date_range':[min(r['created_at'] for r in req),max(r['created_at'] for r in req)],'decision_date_range':[min(r['decided_at'] for r in dec),max(r['decided_at'] for r in dec)],'requests_without_decisions':sum(r['request_id'] not in {d['request_id'] for d in dec} for r in req),'all_requests_have_scores':all(r['request_id'] in smap for r in req),'orphan_decisions':sum(d['request_id'] not in rmap for d in dec),'status_matches':sum(d['final_decision']==rmap[d['request_id']]['status'] for d in dec if d['request_id'] in rmap),'zero_score_rows':sum(all(float(v)==0 for k,v in s.items() if k not in ['score_id','request_id']) for s in scores),'nonzero_score_rows':sum(any(float(v)!=0 for k,v in s.items() if k not in ['score_id','request_id']) for s in scores),'probability_sums_valid':all(abs(sum(float(d[k]) for k in ['verified_probability','review_probability','rejected_probability'])-1)<1e-5 for d in dec)}
summary['anonymized_decisions']=[{'case':i+1,'final_decision':d['final_decision'],'basis':d['decision_basis'],'scores':[smap[d['request_id']][k] for k in ['face_match_score','liveness_score','ocr_confidence_score','blur_score','brightness_score','contrast_score']]} for i,d in enumerate(dec)]
out=Path(__file__).resolve().parent/'final_draft_evidence/live_summary.json';out.write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
