"""Descriptive analysis of a fixed, dependent report census; no new model inference.

Primary continuation results use 77 unchanged published pairs plus the one
archive-verified repair. Published-index results are retained as a diagnostic.
No claim count is treated as an independent trial or model reliability score.
"""
import argparse, csv, json, statistics
from collections import Counter, defaultdict
from pathlib import Path
from build_study import FAMILIES, PROBLEMS, readcsv, writecsv, norm

HERE=Path(__file__).resolve().parent
RESULTS=HERE/'results'
STUDY=RESULTS/'study'
SUPPORT={'supported_observation','qualified_inference'}

def boolean(value):
    return value is True or str(value).lower()=='true'

def number(value):
    return float(value) if value not in ('',None) else None

def median(values):
    clean=[v for v in values if v is not None]
    return statistics.median(clean) if clean else None

def summarize_reports(rows, scope):
    return dict(scope=scope,reports=len(rows),
        with_supported_conclusion=sum(r['has_support'] for r in rows),
        with_problem=sum(r['has_problem'] for r in rows),
        with_contradiction=sum(r['has_contradiction'] for r in rows),
        with_contradiction_excluding_disputed=sum(r['has_contradiction_excluding_disputed'] for r in rows),
        with_problem_excluding_disputed=sum(r['has_problem_excluding_disputed'] for r in rows),
        with_support_and_problem=sum(r['has_support'] and r['has_problem'] for r in rows),
        with_support_and_problem_in_same_question=sum(r['mixed_question_count']>0 for r in rows),
        median_questions_discussed=median([r['questions_discussed'] for r in rows]),
        median_problem_questions=median([r['problem_question_count'] for r in rows]),
        median_supported_questions=median([r['supported_question_count'] for r in rows]),
        median_words=median([r['words'] for r in rows]),
        median_finding_coverage=median([r['finding_coverage'] for r in rows]),
        median_holistic=median([r['holistic'] for r in rows]))

def main(args):
    status=json.loads((STUDY/'summary.json').read_text())
    if not args.allow_partial:
        assert status['complete_reading_population'] and status['completed_manual_pairs']==status['expected_manual_pairs']
    inventory={r['artifact_id']:r for r in readcsv(RESULTS/'report-inventory.csv')}
    grades={r['artifact_id']:r for r in readcsv(RESULTS/'published-grades.csv')}
    provenance={r['report']:r for r in readcsv(RESULTS/'run-provenance.csv')}
    reviews=json.loads((STUDY/'review-records.json').read_text())
    review_by_id={r['review_id']:r for r in reviews}
    report_rows=[];family_rows=[]
    for d in reviews:
        m=inventory[d['artifact_id']];g=grades.get(d['artifact_id'],{});p=provenance.get(norm(d['path']),{})
        cs=d['claims'];supported=set();problem=set();strict_problem=set();mixed=set()
        for f in FAMILIES:
            fc=[c for c in cs if c['family']==f]
            has_support=any(c['judgment'] in SUPPORT for c in fc)
            has_problem=any(c['judgment'] in PROBLEMS for c in fc)
            strict=any(c['judgment'] in PROBLEMS and not c['disputable'] for c in fc)
            if has_support:supported.add(f)
            if has_problem:problem.add(f)
            if strict:strict_problem.add(f)
            if has_support and has_problem:mixed.add(f)
            family_rows.append(dict(review_id=d['review_id'],group=m['group'],artifact_type=m['artifact_type'],cohort=m['cohort'],family=f,
                discussed=d['questions'][f]['disposition']=='discussed',ambiguous=d['questions'][f]['disposition']=='ambiguous',
                supported=has_support,problem=has_problem,problem_excluding_disputed=strict,mixed=has_support and has_problem,
                contradiction=any(c['judgment']=='contradicted'for c in fc),overreach=any(c['judgment']=='exceeds_support'for c in fc)))
        report_rows.append(dict(review_id=d['review_id'],artifact_id=d['artifact_id'],group=m['group'],cohort=m['cohort'],artifact_type=m['artifact_type'],
            model_requested=m['model_requested'],model_served=m['model_served'],fallback=m['model_fallback'],replicate=m['replicate'],budget_min=m['budget_min'],
            words=int(m['words']),sha256=m['sha256'],source_url=m['source_url'],claim_entries=len(cs),
            questions_discussed=sum(q['disposition']=='discussed'for q in d['questions'].values()),supported_question_count=len(supported),
            problem_question_count=len(problem),problem_question_count_excluding_disputed=len(strict_problem),mixed_question_count=len(mixed),
            has_support=bool(supported),has_problem=bool(problem),has_problem_excluding_disputed=bool(strict_problem),
            has_contradiction=any(c['judgment']=='contradicted' for c in cs),has_contradiction_excluding_disputed=any(c['judgment']=='contradicted' and not c['disputable'] for c in cs),
            finding_coverage=number(g.get('finding_coverage')),holistic=number(g.get('holistic')),combined=number(g.get('combined')),
            actual_minutes=number(p.get('wall_seconds'))/60 if number(p.get('wall_seconds')) is not None else None,
            input_hash_status=p.get('input_hash_status','not_applicable'),staged_text_matches_run=boolean(p.get('staged_text_matches_run'))))
    scopes={'main':[r for r in report_rows if r['group']=='main']}
    for group in sorted({r['group']for r in report_rows}):
        scopes[group]=[r for r in report_rows if r['group']==group]
    for budget in ['10','30','120']:
        scopes['main_'+budget+'m']=[r for r in scopes['main']if r['budget_min']==budget]
    scopes['synthesis_accepted']=[r for r in report_rows if r['group']=='synthesis'and r['artifact_type']=='indexed_report']
    scopes['synthesis_rejected']=[r for r in report_rows if r['group']=='synthesis'and r['artifact_type']!='indexed_report']
    cohort_summary=[summarize_reports(v,k)for k,v in scopes.items()]
    family_summary=[]
    for scope,rr in scopes.items():
        ids={r['review_id']for r in rr}
        for family in FAMILIES:
            rows=[r for r in family_rows if r['review_id']in ids and r['family']==family]
            family_summary.append(dict(scope=scope,family=family,reports=len(rows),**{k:sum(r[k]for r in rows)for k in ['discussed','ambiguous','supported','problem','problem_excluding_disputed','mixed','contradiction','overreach']},not_discussed=sum(not(r['discussed']or r['ambiguous'])for r in rows)))
    # Fixed rank thirds within the primary cohort, with explicit tie handling.
    # These are descriptive strata; not a test of a score's causal effect.
    ranked=sorted((r for r in scopes['main']if r['finding_coverage']is not None),key=lambda r:(r['finding_coverage'],r['review_id']))
    score_rows=[]
    for label,a,b in [('lower',0,len(ranked)//3),('middle',len(ranked)//3,2*len(ranked)//3),('upper',2*len(ranked)//3,len(ranked))]:
        rr=ranked[a:b]
        if rr:score_rows.append(dict(**summarize_reports(rr,label+'_coverage_rank_third'),minimum_coverage=min(r['finding_coverage']for r in rr),maximum_coverage=max(r['finding_coverage']for r in rr),ties='Ties are ordered by stable review ID; thresholds are descriptive, not substantive cutoffs.'))
    pair_file=STUDY/'pair-summary.csv';transition_file=STUDY/'claim-transitions.csv'
    pairs=readcsv(pair_file)if pair_file.exists()else[];transitions=readcsv(transition_file)if transition_file.exists()else[]
    expected_corrected={r['parent']for r in readcsv(RESULTS/'followup-pairs-corrected.csv')}
    selected=[p for p in pairs if p['parent']in expected_corrected]
    assert len({p['followup']for p in selected})==len(selected)
    pair_rows=[];pair_aggregate=[]
    byid={r['review_id']:r for r in report_rows}
    for selection,pp in [('corrected_primary',selected),('published_index',[p for p in pairs if p['comparison_set']=='published'])]:
        for p in pp:
            tt=[t for t in transitions if t['parent']==p['parent']and t['comparison_set']==p['comparison_set']]
            problem=[t for t in tt if t['parent_judgment']in PROBLEMS]
            # A disputed follow-up judgment must not survive merely because its
            # parent and the transition itself were marked undisputed.
            def undisputed_followup(t):
                indices=[int(i) for i in t['followup_claim_indices'].split(';') if i]
                if not indices:return t['transition']=='omitted'
                claims=[review_by_id[p['followup_review_id']]['claims'][i-1] for i in indices]
                if t['transition'] in ['retained_problem','superseded']:
                    return any(c['judgment'] in PROBLEMS and not c['disputable'] for c in claims)
                if t['transition'] in ['corrected_statement','qualified_statement','retained_supported']:
                    return any(c['judgment'] in SUPPORT and not c['disputable'] for c in claims)
                return any(not c['disputable'] for c in claims)
            strict=[t for t in problem if not boolean(t['parent_disputable']) and not boolean(t['disputable']) and undisputed_followup(t)]
            a=byid[p['parent_review_id']];b=byid[p['followup_review_id']]
            row=dict(selection=selection,parent=p['parent'],followup=p['followup'],parent_review_id=a['review_id'],followup_review_id=b['review_id'],budget_min=p['parent_budget_min'],
                parent_problem_claims=len(problem),parent_problem_claims_excluding_disputed=len(strict),
                new_problem_claims=int(p['new_or_changed_problematic_followup_claims']),new_problem_claims_excluding_disputed=int(p['new_or_changed_problematic_followup_claims_excluding_disputed']),new_unmapped_problem_claims=int(p['new_problematic_followup_claims']),changed_problem_claims=int(p['changed_problematic_followup_claims']),
                parent_words=a['words'],followup_words=b['words'],parent_coverage=a['finding_coverage'],followup_coverage=b['finding_coverage'],
                parent_holistic=a['holistic'],followup_holistic=b['holistic'],same_text=a['sha256']==b['sha256'])
            for label in ['retained_problem','corrected_statement','qualified_statement','omitted','superseded','unassessable','retained_supported']:
                row['problem_'+label]=sum(t['transition']==label for t in problem)
                row['strict_problem_'+label]=sum(t['transition']==label for t in strict)
            row['explicit_repair_acknowledgments']=sum(t['transition']in ['corrected_statement','qualified_statement']and boolean(t['explicit_acknowledgment'])for t in problem)
            pair_rows.append(row)
        for budget in ['all','10','30','120']:
            rr=[r for r in pair_rows if r['selection']==selection and (budget=='all'or r['budget_min']==budget)]
            summary=dict(selection=selection,budget_min=budget,pairs=len(rr),pairs_with_parent_problem=sum(r['parent_problem_claims']>0 for r in rr),
                pairs_with_correction_or_qualification=sum(r['problem_corrected_statement']+r['problem_qualified_statement']>0 for r in rr),
                pairs_with_correction_or_qualification_excluding_disputed=sum(r['strict_problem_corrected_statement']+r['strict_problem_qualified_statement']>0 for r in rr),
                pairs_with_retained_problem=sum(r['problem_retained_problem']>0 for r in rr),pairs_with_new_problem=sum(r['new_problem_claims']>0 for r in rr),
                pairs_with_omitted_problem=sum(r['problem_omitted']>0 for r in rr),identical_text_pairs=sum(r['same_text']for r in rr),
                median_word_change=median([r['followup_words']-r['parent_words']for r in rr]),
                coverage_increased=sum(r['followup_coverage']>r['parent_coverage']for r in rr if r['parent_coverage']is not None and r['followup_coverage']is not None),
                median_coverage_change=median([r['followup_coverage']-r['parent_coverage']for r in rr if r['parent_coverage']is not None and r['followup_coverage']is not None]),
                coverage_increased_with_retained_problem=sum(r['followup_coverage']>r['parent_coverage'] and r['problem_retained_problem']>0 for r in rr if r['parent_coverage']is not None and r['followup_coverage']is not None),
                coverage_increased_with_repair=sum(r['followup_coverage']>r['parent_coverage'] and r['problem_corrected_statement']+r['problem_qualified_statement']>0 for r in rr if r['parent_coverage']is not None and r['followup_coverage']is not None),
                coverage_increased_with_retained_problem_excluding_disputed=sum(r['followup_coverage']>r['parent_coverage'] and r['strict_problem_retained_problem']>0 for r in rr if r['parent_coverage']is not None and r['followup_coverage']is not None),
                pairs_with_undisputed_problem_transition=sum(r['parent_problem_claims_excluding_disputed']>0 for r in rr),
                pairs_with_retained_problem_excluding_disputed=sum(r['strict_problem_retained_problem']>0 for r in rr))
            for key in ['parent_problem_claims','parent_problem_claims_excluding_disputed','new_problem_claims','new_problem_claims_excluding_disputed','new_unmapped_problem_claims','changed_problem_claims','explicit_repair_acknowledgments']+[prefix+label for prefix in ['problem_','strict_problem_']for label in ['retained_problem','corrected_statement','qualified_statement','omitted','superseded','unassessable','retained_supported']]:summary[key]=sum(r[key]for r in rr)
            pair_aggregate.append(summary)
    for name,rows in [('report-outcomes',report_rows),('question-outcomes',family_rows),('cohort-outcomes',cohort_summary),('question-summary',family_summary),('score-strata',score_rows),('paired-outcomes',pair_rows),('paired-summary',pair_aggregate)]:
        writecsv(STUDY/(name+'.csv'),rows)
    out=dict(complete=status['complete_reading_population']and len(selected)==78 and len(pairs)==79,
        reading_artifacts=len(reviews),distinct_texts=len({r['sha256']for r in report_rows}),primary_reports=len(scopes['main']),
        corrected_continuations=len(selected),manual_comparisons=len(pairs),cohort_summary=cohort_summary,
        primary_questions=[r for r in family_summary if r['scope']=='main'],paired_summary=pair_aggregate,score_strata=score_rows,
        limits=['Assistant-coded, not independently human-adjudicated.','Fixed dependent publication corpus; no population error rate or model ranking.','Grouped claims are interpretive units, not independent trials.','Question omission is distinct from supported analysis.','Rank thirds split ties by stable ID and are only a descriptive score check.','Corrected and published pair sets describe the same continuations and must not be added.'])
    (STUDY/'analysis.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items()if k not in ['cohort_summary','paired_summary','primary_questions','score_strata','limits']},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--allow-partial',action='store_true');main(parser.parse_args())
