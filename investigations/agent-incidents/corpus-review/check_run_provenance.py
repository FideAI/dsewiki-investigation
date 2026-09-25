"""Trace report identities, input hashes and corrected followup linkage from run metadata."""
import csv,json,re,statistics
from collections import Counter,defaultdict
from pathlib import Path
HERE=Path(__file__).resolve().parent;CACHE=HERE.parents[2]/'.local/wiki-containment-20260915'
def norm(s):return re.sub('[^a-zA-Z0-9]+','_',Path(s).stem).strip('_')
def readcsv(p):return list(csv.DictReader(p.open()))
def writecsv(p,rows):
    if rows:
        with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    metadata={};rows=[]
    samples=json.loads((HERE/'results/archive-samples.json').read_text());by_log={(x['log_basename'],x['sample_id'],x['epoch']):x for x in samples};by_run={x['run_id']:x for x in samples if x['run_id']}
    inventory={norm(x['path']):x for x in readcsv(HERE/'results/report-inventory.csv')if x['artifact_type']=='indexed_report'}
    by_sha={x['sha256']:k for k,x in inventory.items()}
    grades={x['report']:x for x in readcsv(HERE/'results/published-grades.csv')}
    variants={v:{p.name:__import__('hashlib').sha256(p.read_bytes()).hexdigest()for p in(CACHE/'data'/v).glob('*.jsonl')}for v in ['verbatim','verbatim_anthropic']}
    for p in sorted((CACHE/'benchmark/graded_inputs').glob('*/_index.jsonl')):
        for line in p.read_text().splitlines():
            m=json.loads(line);k=norm(m['graded_input']);assert k not in metadata;metadata[k]=m
            s=by_log.get((Path(m.get('log_file','')).name,m.get('sample_id'),m.get('replicate')))
            if not s and m.get('run_id'):s=by_run.get(m['run_id'])
            pf=s.get('preflight_files',{})if s else {};expected=variants.get(m.get('data_variant'),{});hash_status='not_recorded'
            if pf:hash_status='match' if len(pf)==4 and all(expected.get(name)==v['sha256']for name,v in pf.items())else 'mismatch'
            rows.append({'report':k,'cohort':p.parent.name,'wall_seconds':m.get('wall_seconds'),'prompt_id':m.get('prompt_id'),'budget_min':m.get('budget_min'),'parent_budget_min':m.get('parent_budget_min'),'data_variant':m.get('data_variant'),'archive_sample_match':bool(s),'staged_text_matches_run':bool(s and inventory[k]['sha256']in[s['output_sha256'],s['output_normalized_sha256']]),'input_hash_status':hash_status,'log_basename':s['log_basename']if s else '', 'source_run_id':s.get('run_id')if s else m.get('run_id'),'sample_id':m.get('sample_id',''),'epoch':m.get('replicate'),'model_requested':m.get('model'),'model_served':m.get('model_served'),'fallback':json.dumps(m.get('model_fallback')),'partial':bool(m.get('partial')),'terminal_refusal':bool(m.get('terminal_refusal')),'report_words':m.get('report_words'),'accept_min_words':m.get('report_accept_min_words'),'length_compliant':m.get('report_length_compliant')})
    pairs=[];corrected=[];repairs=[]
    for p in readcsv(HERE/'results/followup-pairs.csv'):
        a,b=metadata[p['parent']],metadata[p['followup']]
        if b.get('parent_run_id'):
            parent_sample=by_run.get(b['parent_run_id']);method='archived_parent_run_id'
            thread_matches=bool(parent_sample and parent_sample.get('thread_id')==b.get('parent_thread_id'))
        else:
            matches=[s for s in samples if s['log_basename']==Path(b.get('parent_log','')).name and s['epoch']==b.get('parent_epoch')];assert len(matches)==1
            parent_sample=matches[0];method='archived_parent_log_and_epoch';thread_matches=None
        assert parent_sample,('missing parent',p['parent'])
        actual=by_sha.get(parent_sample['output_sha256'])or by_sha.get(parent_sample['output_normalized_sha256']);assert actual,('parent output not staged',p['parent'])
        okay=actual==p['parent'];actual_meta=metadata[actual]
        pairs.append({'published_parent':p['parent'],'actual_parent':actual,'followup':p['followup'],'published_identity_matches':okay,'method':method,'thread_id_matches':thread_matches,'parent_budget_matches':b.get('parent_budget_min')==actual_meta.get('budget_min'),'archive':parent_sample['archive'],'log_path':parent_sample['log_path'],'sample_member':parent_sample['sample_member'],'output_sha256':parent_sample['output_sha256']})
        r=dict(p);r['published_parent']=p['parent'];r['pairing_repaired']=not okay
        if not okay:
            m=inventory[actual];g=grades[actual];r.update(parent=actual,parent_path=m['path'],parent_sha256=m['sha256'],parent_words=m['words'],published_parent_coverage=g['finding_coverage'],published_parent_tldr=g['holistic'],identical_text=m['sha256']==p['followup_sha256']);repairs.append(r)
        corrected.append(r)
    assert len(pairs)==78 and all(x['parent_budget_matches']for x in pairs)
    for name,data in [('run-provenance',rows),('pair-provenance',pairs),('followup-pairs-corrected',corrected),('followup-pair-repairs',repairs)]:writecsv(HERE/'results'/f'{name}.csv',data)
    budgets=[]
    for n in [10,30,120]:
        x=[r for r in rows if r['cohort']==f'round4_blind{n}'];times=[r['wall_seconds']/60 for r in x if r['wall_seconds']is not None]
        budgets.append({'budget_min':n,'reports':len(x),'median_actual_minutes':statistics.median(times),'minimum_actual_minutes':min(times),'maximum_actual_minutes':max(times),'prompt_ids':sorted({r['prompt_id']for r in x}),'fallbacks':sum(r['fallback']!='null'for r in x)})
    out={'indexed_reports':len(rows),'published_pairs_checked':len(pairs),'published_pairs_matching_actual_parent':sum(x['published_identity_matches']for x in pairs),'repaired_pairs':len(repairs),'archive_sample_matches':sum(x['archive_sample_match']for x in rows),'staged_text_matches_run':sum(x['staged_text_matches_run']for x in rows),'input_hash_status_counts':dict(Counter(x['input_hash_status']for x in rows)),'input_hash_mismatches':[x['report']for x in rows if x['input_hash_status']=='mismatch'],'primary_budget_conditions':budgets,'limits':['Run JSON metadata and output hashes were inspected; behavioral transcripts were not comprehensively read.','Input hashes substantiate the recorded preflight for matched native samples; no hashes were available for some subscription runs.','Historical grades are separate from these run logs.','Budget conditions differ in prompts and runtime; the report census includes retries and missing requested replicates.']}
    (HERE/'results/run-provenance-check.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
