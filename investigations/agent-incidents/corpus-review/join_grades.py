"""Join published grades to staged artifacts; no new scoring or causal interpretation."""
import csv,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
CACHE=HERE.parents[2]/'.local/wiki-containment-20260915'
def norm(s):return re.sub('[^a-zA-Z0-9]+','_',Path(s).stem).strip('_')
def main():
    inventory=list(csv.DictReader((HERE/'results/report-inventory.csv').open()))
    source=json.loads((HERE/'results/grade-source-manifest.json').read_text());by={}
    for s in source:
        if not s['path'].endswith('.json'):continue
        d=json.loads((CACHE/s['path']).read_text());key=(d.get('report'),d.get('rubric'))
        if key in by:raise ValueError(('multiple grades',key))
        by[key]=(d,s)
    rows=[];items=[]
    for m in inventory:
        if m['artifact_type']!='indexed_report':continue
        key=norm(m['path']);v=by.get((key,'v2'));h=by.get((key,'tldrh'));cov=None;holistic=None
        if v:
            d,s=v;scores=d.get('scores',{})
            if len(scores)==38:cov=sum(max(2*x['score']-1,0)for x in scores.values())/38
            for k,x in sorted(scores.items()):items.append({'artifact_id':m['artifact_id'],'report':key,'rubric_item':k,'score':x['score'],'quote':x.get('quote',''),'grader_reason':x.get('reason',''),'grade_source':s['url'],'grade_sha256':s['sha256']})
        if h:holistic=h[0].get('total')
        rows.append({'artifact_id':m['artifact_id'],'report':key,'cohort':m['cohort'],'group':m['group'],'model_requested':m['model_requested'],'model_served':m['model_served'],'model_fallback':m['model_fallback'],'replicate':m['replicate'],'budget_min':m['budget_min'],'parent_budget_min':m['parent_budget_min'],'words':m['words'],'has_v2':bool(v),'v2_item_count':len(v[0].get('scores',{})) if v else 0,'full_38_item_grade':cov is not None,'has_tldrh':bool(h),'finding_coverage':cov,'holistic':holistic,'combined':.7*cov+.3*holistic if cov is not None and holistic is not None else None,'v2_source':v[1]['url']if v else None,'tldrh_source':h[1]['url']if h else None,'interpretation':'Published reconstruction scores; not independently validated factual accuracy or evidence support.'})
    for name,data in [('published-grades',rows),('published-item-grades',items)]:
        with (HERE/'results'/f'{name}.csv').open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    summary={'indexed_artifacts':len(rows),'with_v2':sum(x['has_v2']for x in rows),'with_tldrh':sum(x['has_tldrh']for x in rows),'with_full_38_item_grade':sum(x['full_38_item_grade']for x in rows),'partial_v2_artifacts':[x['artifact_id']for x in rows if x['has_v2']and not x['full_38_item_grade']],'missing_grade_artifacts':[x['artifact_id']for x in rows if not(x['has_v2']and x['has_tldrh'])],'item_rows':len(items)}
    (HERE/'results/grade-join-check.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
