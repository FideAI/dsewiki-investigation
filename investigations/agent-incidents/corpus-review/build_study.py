"""Validate and aggregate assistant-coded full readings and manual claim transitions."""
import argparse,csv,hashlib,json,re
from collections import Counter,defaultdict
from pathlib import Path
HERE=Path(__file__).resolve().parent
FAMILIES=('attribution','authority','coordination','techniques','persistence','impact','recovery','chronology')
LABELS={'supported_observation','qualified_inference','exceeds_support','contradicted','unassessable'}
PROBLEMS={'contradicted','exceeds_support'}
def readcsv(p):return list(csv.DictReader(p.open()))
def writecsv(p,rows):
    if not rows:return
    with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def norm(s):return re.sub('[^a-zA-Z0-9]+','_',Path(s).stem).strip('_')
def validate_review(d,m,cache):
    assert d['path']==m['path'] and d['artifact_id']==m['artifact_id'],d['review_id']
    raw=(cache/d['path']).read_bytes();lines=raw.decode().splitlines()
    assert hashlib.sha256(raw).hexdigest()==d['sha256']==m['sha256'],d['review_id']
    assert d['full_text_read'] is True and d['total_lines']==len(lines),d['review_id']
    for ranges in [d['read_ranges'],[(x['start'],x['end']) for x in d['section_coverage']]]:
        covered=set()
        for a,b in ranges:assert 1<=a<=b<=len(lines);covered.update(range(a,b+1))
        assert covered==set(range(1,len(lines)+1)),('coverage',d['review_id'])
    assert set(d['questions'])==set(FAMILIES),('questions',d['review_id'])
    for c in d['claims']:
        assert c['family'] in FAMILIES and c['judgment'] in LABELS,(d['review_id'],c)
        assert c['lines'] and all(type(n)==int and 1<=n<=len(lines) for n in c['lines']),(d['review_id'],'claimlines')
        assert type(c['disputable'])==bool
        for key in ['claim','confidence_context','rationale']:
            assert isinstance(c[key],str) and c[key].strip(),(d['review_id'],key)
        assert isinstance(c['evidence'],list) and c['evidence'],(d['review_id'],'evidence')
        for key in ['claim_type','asserted_strength','correct_core','missing_link','decision_relevance','report_next_check','fide_next_check','rubric_ids']:assert key in c,(d['review_id'],key)
    for fam,q in d['questions'].items():
        assert q['disposition'] in ['discussed','not_discussed','ambiguous']
        if q['disposition']=='not_discussed':assert not any(c['family']==fam for c in d['claims']),(d['review_id'],fam)
    return len(raw.decode().split())
def main(args):
    inventory=readcsv(HERE/'results/report-inventory.csv');meta={r['artifact_id']:r for r in inventory}
    reviews={};claims=[];assess=[];coverage=[];errors=[]
    for p in sorted((HERE/'reviews').glob('C*.json')):
        try:
            d=json.loads(p.read_text());m=meta[d['artifact_id']];words=validate_review(d,m,args.cache)
            assert d['review_id'] not in reviews
            reviews[d['review_id']]=d
            coverage.append({'review_id':d['review_id'],'artifact_id':d['artifact_id'],'group':m['group'],'cohort':m['cohort'],'artifact_type':m['artifact_type'],'sha256':d['sha256'],'words':words,'lines':d['total_lines'],'full_text_read':True,'section_coverage_complete':True,'source_url':m['source_url'],'independent_human_review':'pending'})
            for i,c in enumerate(d['claims'],1):
                claims.append({'claim_id':f'{d["review_id"]}-{i:02d}','review_id':d['review_id'],'artifact_id':d['artifact_id'],'group':m['group'],'cohort':m['cohort'],'claim_index':i,'family':c['family'],'claim':c['claim'],'judgment':c['judgment'],'disputable':c['disputable'],'lines':';'.join(map(str,c['lines'])),'source_url':m['source_url'].replace('raw.githubusercontent.com/hamzah2304/messageboardauditbench/','github.com/hamzah2304/messageboardauditbench/blob/')+'#L'+str(min(c['lines'])),'confidence_context':c['confidence_context'],'rationale':c['rationale'],'evidence':json.dumps(c['evidence'],ensure_ascii=False),'claim_type':c['claim_type'],'asserted_strength':c['asserted_strength'],'decision_relevance':c['decision_relevance'],'missing_link':c['missing_link'],'correct_core':c['correct_core'],'report_next_check':c['report_next_check'],'fide_next_check':c['fide_next_check'],'rubric_ids':';'.join(c['rubric_ids'])})
            for fam in FAMILIES:
                cc=[c for c in d['claims'] if c['family']==fam];labels={c['judgment'] for c in cc}
                assess.append({'review_id':d['review_id'],'artifact_id':d['artifact_id'],'group':m['group'],'cohort':m['cohort'],'artifact_type':m['artifact_type'],'family':fam,'disposition':d['questions'][fam]['disposition'],'claim_count':len(cc),'has_contradiction':'contradicted'in labels,'has_overreach':'exceeds_support'in labels,'has_problem':bool(labels&PROBLEMS),'has_problem_excluding_disputed':any(c['judgment']in PROBLEMS and not c['disputable']for c in cc),'has_supported_observation':'supported_observation'in labels,'has_qualified_inference':'qualified_inference'in labels,'has_unassessable':'unassessable'in labels})
        except Exception as e:errors.append({'file':p.name,'error':str(e)})
    if errors:raise RuntimeError(json.dumps(errors,indent=2))
    assert len({d['artifact_id'] for d in reviews.values()})==len(reviews)
    complete=len(reviews)==len(inventory)
    if not args.allow_partial:assert complete,('incomplete reviews',len(reviews),len(inventory))
    groups=[]
    for group in sorted({x['group']for x in coverage}):
        for fam in FAMILIES:
            aa=[x for x in assess if x['group']==group and x['family']==fam and x['artifact_type']=='indexed_report']
            groups.append({'group':group,'family':fam,'reports':len(aa),**{k:sum(x[k]for x in aa)for k in ['has_contradiction','has_overreach','has_problem','has_problem_excluding_disputed','has_supported_observation','has_qualified_inference','has_unassessable']},'not_discussed':sum(x['disposition']=='not_discussed'for x in aa)})
    expected_pairs={p['parent']:p for p in readcsv(HERE/'results/followup-pairs.csv')}
    repairs={p['parent']:p for p in readcsv(HERE/'results/followup-pair-repairs.csv')}
    pairs=[];trans=[]
    files=[(p,'published') for p in sorted((HERE/'pairs').glob('*.json'))]+[(p,'repair') for p in sorted((HERE/'pairs-repaired').glob('*.json'))]
    for p,comparison_set in files:
        d=json.loads(p.read_text());e=(expected_pairs if comparison_set=='published' else repairs)[d['parent']];assert d['followup']==e['followup'] and d['manual_comparison']is True
        a=reviews[d['parent_review_id']];b=reviews[d['followup_review_id']]
        assert d['parent_sha256']==a['sha256']==e['parent_sha256'];assert d['followup_sha256']==b['sha256']==e['followup_sha256']
        assert norm(a['path'])==d['parent'] and norm(b['path'])==d['followup']
        assert sorted(t['parent_claim_index']for t in d['transitions'])==list(range(1,len(a['claims'])+1)),('parent coverage',p.name)
        matched=set()
        for t in d['transitions']:
            assert t['transition']in {'retained_supported','retained_problem','corrected_statement','qualified_statement','omitted','superseded','unassessable'}
            ai=t['parent_claim_index'];fi=t['followup_claim_indices'];assert all(1<=n<=len(b['claims'])for n in fi);matched.update(fi)
            ac=a['claims'][ai-1];fc=[b['claims'][n-1]for n in fi]
            assert t['rationale'].strip() and type(t['disputable']) is bool and type(t['explicit_acknowledgment']) is bool,('transition fields',p.name,ai)
            assert all(1<=n<=a['total_lines']for n in t['parent_lines']) and all(1<=n<=b['total_lines']for n in t['followup_lines']),('transition source lines',p.name,ai)
            if t['transition']=='retained_problem':assert ac['judgment']in PROBLEMS and any(c['judgment']in PROBLEMS for c in fc),('retained problem mismatch',p.name,ai)
            if t['transition']=='retained_supported':assert ac['judgment']not in PROBLEMS and not any(c['judgment']in PROBLEMS for c in fc),('retained support mismatch',p.name,ai)
            if t['transition']=='omitted':assert not fi,('omission with mapped claim',p.name,ai)
            if t['transition']in ['corrected_statement','qualified_statement']:assert any(c['judgment']in {'supported_observation','qualified_inference'}for c in fc),('repair without supported follow-up',p.name,ai)
            trans.append({'comparison_set':comparison_set,'parent':d['parent'],'followup':d['followup'],'parent_review_id':a['review_id'],'followup_review_id':b['review_id'],'parent_claim_index':ai,'family':ac['family'],'parent_judgment':ac['judgment'],'parent_disputable':ac['disputable'],'followup_claim_indices':';'.join(map(str,fi)),'transition':t['transition'],'rationale':t['rationale'],'explicit_acknowledgment':t['explicit_acknowledgment'],'disputable':t['disputable'],'followup_has_problem':any(c['judgment']in PROBLEMS for c in fc)})
        new=set(d['new_followup_claim_indices']);assert not(new&matched);assert new|matched==set(range(1,len(b['claims'])+1)),('follow-up coverage',p.name,sorted(set(range(1,len(b['claims'])+1))-(new|matched)))
        retained_problem_indices={i for t in d['transitions'] if t['transition']=='retained_problem' for i in t['followup_claim_indices'] if b['claims'][i-1]['judgment']in PROBLEMS}
        changed_problem_indices={i for t in d['transitions'] if t['transition']=='superseded' for i in t['followup_claim_indices'] if b['claims'][i-1]['judgment']in PROBLEMS}-retained_problem_indices
        new_problem_indices={i for i in new if b['claims'][i-1]['judgment']in PROBLEMS}
        new_or_changed=new_problem_indices|changed_problem_indices
        disputed_transition_indices={i for t in d['transitions'] if t['disputable'] for i in t['followup_claim_indices']}
        strict_new_or_changed={i for i in new_or_changed if not b['claims'][i-1]['disputable'] and i not in disputed_transition_indices}
        pairs.append({'comparison_set':comparison_set,'parent_review_id':a['review_id'],'followup_review_id':b['review_id'],'parent':d['parent'],'followup':d['followup'],'parent_budget_min':e['parent_budget_min'],'parent_claims':len(a['claims']),'followup_claims':len(b['claims']),'new_followup_claims':len(new),'changed_problematic_followup_claims':len(changed_problem_indices),'new_or_changed_problematic_followup_claims':len(new_or_changed),'new_or_changed_problematic_followup_claims_excluding_disputed':len(strict_new_or_changed),'new_or_changed_problematic_followup_indices':';'.join(map(str,sorted(new_or_changed))),'new_problematic_followup_claims':sum(b['claims'][i-1]['judgment']in PROBLEMS for i in new),'new_problematic_followup_claims_excluding_disputed':sum(b['claims'][i-1]['judgment']in PROBLEMS and not b['claims'][i-1]['disputable'] for i in new),'summary':d['summary']})
    assert len({p['parent']for p in pairs})==len(pairs)
    if not args.allow_partial:
        assert {p['parent']for p in pairs if p['comparison_set']=='published'}==set(expected_pairs),('incomplete published pairs',len(pairs))
        assert {p['parent']for p in pairs if p['comparison_set']=='repair'}==set(repairs),('incomplete repaired comparisons',len(pairs))
    out=HERE/'results/study';out.mkdir(parents=True,exist_ok=True)
    for name,rows in [('claims',claims),('assessments',assess),('coverage',coverage),('family-summary',groups),('pair-summary',pairs),('claim-transitions',trans)]:writecsv(out/(name+'.csv'),rows)
    summary={'scope':'Expanded eight-question assistant assessment; independent human adjudication pending','expected_artifacts':len(inventory),'completed_full_readings':len(reviews),'complete_reading_population':complete,'complete':complete and len(pairs)==len(expected_pairs)+len(repairs),'words_read':sum(c['words']for c in coverage),'claim_entries':len(claims),'report_question_assessments':len(assess),'completed_manual_pairs':len(pairs),'expected_manual_pairs':len(expected_pairs)+len(repairs),'completed_published_pairs':sum(p['comparison_set']=='published'for p in pairs),'completed_repaired_pairs':sum(p['comparison_set']=='repair'for p in pairs),'primary_continuations':len(expected_pairs),'family_summary':groups,'claim_label_counts':dict(Counter(c['judgment']for c in claims)),'transition_counts':dict(Counter(t['transition']for t in trans)),'limits':['Descriptive fixed-corpus analysis; categories overlap and grouped claims are dependent.','No causal isolation of time, prompt, length or provider substitutions.','Recorded preflight input hashes match 113 native runs; input identity remains unverified where hashes were not recorded.','Full reading across eight questions does not validate every incidental assertion.']}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (out/'review-records.json').write_text(json.dumps(list(reviews.values()),ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items()if k not in ['family_summary','limits']},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cache',type=Path,default=HERE.parents[2]/'.local/wiki-containment-20260915');p.add_argument('--allow-partial',action='store_true');main(p.parse_args())
