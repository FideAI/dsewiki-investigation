"""Inventory staged reports and provenance without representing acquisition as reading."""
import argparse,csv,hashlib,json,re
from collections import Counter,defaultdict
from pathlib import Path

def dumpcsv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def run(cache,out):
    out.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((cache/'corpus-manifest.json').read_text())
    artifacts={a['path']:a for a in manifest['artifacts']}
    prior_path=Path(__file__).resolve().parent.parent/'claim-audit/results/report-register.csv'
    old=list(csv.DictReader(prior_path.open())) if prior_path.exists() else []
    prior={x['sha256']:x['report_id'] for x in old}
    expanded={d['artifact_id']:d for p in (Path(__file__).resolve().parent/'reviews').glob('C*.json') for d in [json.loads(p.read_text())]}
    rows=[];issues=[];duplicates=defaultdict(list);index_totals={}
    for index_path in sorted(cache.glob('benchmark/graded_inputs/*/_index.jsonl')):
        cohort=index_path.parent.name
        items=[json.loads(x) for x in index_path.read_text().splitlines() if x.strip()]
        index_totals[cohort]=len(items)
        by=defaultdict(list)
        for i in items:by[i['graded_input']].append(i)
        for name,records in by.items():
            if len(records)>1:issues.append({'cohort':cohort,'file':name,'issue':'duplicate_index_entries','count':len(records)})
            if not(index_path.parent/name).exists():issues.append({'cohort':cohort,'file':name,'issue':'index_target_missing','count':1})
        for path in sorted(index_path.parent.rglob('*.md')):
            rel=str(path.relative_to(cache));raw=path.read_bytes();sha=hashlib.sha256(raw).hexdigest();assert sha==artifacts[rel]['sha256']
            rejected='rejected' in path.relative_to(index_path.parent).parts
            meta=by.get(path.name,[]) if not rejected else [];m=meta[0] if len(meta)==1 else {}
            if not meta and not rejected:issues.append({'cohort':cohort,'file':path.name,'issue':'unindexed_staged_file','count':1})
            duplicates[sha].append(rel)
            artifact_id=str(path.relative_to(cache/'benchmark/graded_inputs')).removesuffix('.md')
            review=expanded.get(artifact_id,{})
            reviewed=review.get('full_text_read')is True and review.get('sha256')==sha
            group=('main' if cohort.startswith('round4_') else 'followup_min5' if cohort.startswith('fu5k_min5_') else 'provider_swap' if cohort.startswith('pswap_') else 'earlier_provider_ablation' if cohort.startswith('ablation_') else 'exploratory_followup' if cohort=='fu5k' else 'synthesis')
            rows.append({'artifact_id':str(path.relative_to(cache/'benchmark/graded_inputs')).removesuffix('.md'),'cohort':cohort,'group':group,'artifact_type':'rejected_attempt' if rejected else 'indexed_report' if len(meta)==1 else 'unindexed_file','path':rel,'sha256':sha,'source_url':artifacts[rel]['url'],'bytes':len(raw),'words':len(raw.decode().split()),'index_entries':len(meta),'agent':m.get('agent'),'model_requested':m.get('model'),'model_served':m.get('model_served'),'model_fallback':json.dumps(m.get('model_fallback')),'replicate':m.get('replicate'),'budget_min':m.get('budget_min'),'parent_budget_min':m.get('parent_budget_min'),'data_variant':m.get('data_variant'),'partial':m.get('partial'),'terminal_refusal':m.get('terminal_refusal'),'parent_run_id':m.get('parent_run_id'),'prompt_id':m.get('prompt_id'),'prior_review_id':prior.get(sha,''),'full_text_read':reviewed or sha in prior,'adjudication_scope':'eight_defined_questions' if reviewed else 'four_defined_questions' if sha in prior else 'pending','expanded_conclusion_review':'completed_assistant_assessment' if reviewed else 'pending','review_id':review.get('review_id',''), 'independent_human_review':'pending'})
    groups=[]
    for group in sorted({r['group'] for r in rows}):
        rr=[r for r in rows if r['group']==group]
        groups.append({'group':group,'staged_files':len(rr),'indexed_files':sum(r['index_entries']==1 for r in rr),'unique_texts':len({r['sha256'] for r in rr}),'words':sum(r['words'] for r in rr),'full_text_read_prior':sum(bool(r['prior_review_id']) for r in rr),'expanded_readings':sum(r['expanded_conclusion_review']=='completed_assistant_assessment' for r in rr),'partial_flagged':sum(r['partial'] is True for r in rr),'fallback_flagged':sum(r['model_fallback']!='null' for r in rr),'rejected_attempts':sum(r['artifact_type']=='rejected_attempt' for r in rr),'unresolved_metadata':sum(r['artifact_type']=='unindexed_file' for r in rr)})
    summary={'commit':manifest['commit'],'staged_files':len(rows),'indexed_report_artifacts':sum(r['artifact_type']=='indexed_report' for r in rows),'rejected_attempts':sum(r['artifact_type']=='rejected_attempt' for r in rows),'distinct_report_texts':len(duplicates),'total_words_in_staged_files':sum(r['words'] for r in rows),'previously_read_reports':sum(bool(r['prior_review_id']) for r in rows),'expanded_conclusion_reviews_complete':sum(r['expanded_conclusion_review']=='completed_assistant_assessment'for r in rows),'groups':groups,'cohorts':dict(sorted(Counter(r['cohort'] for r in rows).items())),'index_rows':index_totals,'duplicate_text_groups':[v for v in duplicates.values() if len(v)>1],'provenance_issues':issues,'scope_note':'File inventory with reading attestations joined from current review records; build_study.py separately validates hashes and complete reading coverage. Reports are dependent across followups, synthesis and duplicates; distinct texts are not independent runs.'}
    dumpcsv(out/'report-inventory.csv',rows)
    (out/'inventory-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cache',type=Path,required=True);p.add_argument('--out',type=Path,default=Path(__file__).resolve().parent/'results');a=p.parse_args();run(a.cache,a.out)
