"""Independent raw-record checks for the September 23 internal reassessment.

Uses the prepared JSONL directly, without the existing SQLite joins. It checks
observations, not the interpretive judgments. Incident content remains inert.
"""
import argparse
import base64
import csv
import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main(cache):
    source = cache / 'data/verbatim'
    data = {name: [json.loads(line) for line in (source / f'{name}.jsonl').open()]
            for name in ['revisions', 'events', 'pages', 'labels']}
    revisions, events = data['revisions'], data['events']
    deletions = [e for e in events if e['event_type'] == 'delete']
    by_page = defaultdict(list)
    for event in deletions:
        by_page[event['page_key']].append(event['time'])
    after_first = [r for r in revisions if r['page_key'] in by_page
                   and r['time'] > min(by_page[r['page_key']])]
    after_final = [r for r in revisions if r['page_key'] in by_page
                   and r['time'] > max(by_page[r['page_key']])]
    prefs = [e for e in events if e['event_type'] == 'request'
             and e.get('ip16') == '52.87' and e.get('request_action') == 'form_editprefs']
    edits = [r for r in revisions if r.get('ip16') == '52.87'
             and r.get('label') == 'AgentDataHelperX']
    pairs = []
    for edit in edits:
        for request in prefs:
            delta = (datetime.fromisoformat(edit['time']) - datetime.fromisoformat(request['time'])).total_seconds()
            if 0 <= delta <= 1:
                pairs.append(dict(request_id=request['event_id'], revision_id=edit['rev_id'], delta_seconds=int(delta)))
    request = next(e for e in events if e['event_id'] == 'request:dse:5911')
    literal = re.search(r'atob\([\"\']([A-Za-z0-9+/=]+)[\"\']\)', request['request']).group(1)
    payload = json.loads(base64.b64decode(literal, validate=True))
    target = [r for r in revisions if r['page_key'] == 'dse~' + payload['inputs']['id']]
    restoration = min((r for r in revisions if r.get('label') == 'MartinHuber'), key=lambda r: r['time'])
    facts = dict(
        after_first_deletion_revisions=len(after_first),
        after_first_deletion_pages=len({r['page_key'] for r in after_first}),
        after_final_deletion_revisions=len(after_final),
        deletion_events=len(deletions), distinct_deletion_targets=len(by_page),
        deletions_before_june18=sum(e['time'] < '2026-06-18' for e in deletions),
        deletions_before_june23=sum(e['time'] < '2026-06-23' for e in deletions),
        deletions_by_last_save=sum(e['time'] <= '2026-07-02T17:51:22Z' for e in deletions),
        first_moderator_revision=dict(id=restoration['rev_id'], time=restoration['time']),
        same_prefix_preference_requests=len(prefs), selected_edits=len(edits),
        matched_edits=len({p['revision_id'] for p in pairs}),
        same_second_pairs=sum(p['delta_seconds'] == 0 for p in pairs),
        next_second_pairs=sum(p['delta_seconds'] == 1 for p in pairs),
        preferences_without_selected_edit=[e['event_id'] for e in prefs
            if e['event_id'] not in {p['request_id'] for p in pairs}],
        target_revisions=len(target), initial_payload_exact_matches=sum(r['body'] == payload['text'] for r in target),
        target_revisions_before_payload=sum(r['time'] < request['time'] for r in target),
        summary_page_count=len(data['pages']),
        summary_pages_with_deletion=sum(p['page_key'] in by_page for p in data['pages']),
        late_sibling_revisions=sum(r['wiki'] != 'dse' and r['time'] >= '2026-06-23' for r in revisions),
    )
    expected = dict(after_first_deletion_revisions=420, after_first_deletion_pages=48,
                    after_final_deletion_revisions=0, deletion_events=5217, distinct_deletion_targets=5144,
                    deletions_before_june18=2, deletions_before_june23=444, deletions_by_last_save=2796,
                    same_prefix_preference_requests=25, selected_edits=14, matched_edits=14,
                    same_second_pairs=12, next_second_pairs=2, target_revisions=20,
                    initial_payload_exact_matches=0, summary_page_count=4579,
                    summary_pages_with_deletion=3898, late_sibling_revisions=11)
    for key, value in expected.items():
        assert facts[key] == value, (key, facts[key], value)
    assert restoration['rev_id'] == 'dse~StartSeite@254'
    assert facts['target_revisions_before_payload'] > 0
    by_id = {r['rev_id']: r for r in revisions}
    positive_ids = ['dse~UEFAU21PassAccuracySequenceOct18@3', 'dse~UEFAPassAccuracySequenceSep17@1',
                    'dse~UEFAPassAccuracySequenceSep17@14', 'dse~UEFAPassAccuracySequenceSep17@19',
                    'dse~Sector61State5LiveRelay@63', 'dse~DataUSALanguageR5LiveDec29@2',
                    'dse~DataUSALanguageR5LiveDec29@5']
    assert 'Slovenia69' in by_id[positive_ids[1]]['body']
    assert 'using leaked Slovenia 69%' in by_id[positive_ids[2]]['body']
    assert 'OCT18 R5 CONFIRMED: Slovenia 69%' in by_id[positive_ids[3]]['body']
    assert 'STATE5-ID CONFIRMED' in by_id[positive_ids[4]]['body']
    assert 'accidental endpoint test' in by_id[positive_ids[6]]['body']
    assert (datetime.fromisoformat(by_id[positive_ids[6]]['time']) - datetime.fromisoformat(by_id[positive_ids[5]]['time'])).total_seconds() == 140
    admin = next(r for r in data['labels'] if r['label'] == 'Friedrich1982')
    assert admin['role'] == 'administrator' and admin['stored_revisions'] == 0
    # Independently count the headline results from the authored review/pair
    # JSONs, rather than from build_study's derived transition CSVs.
    reviews = {f.stem: json.loads(f.read_text()) for f in (HERE / 'reviews').glob('C*.json')}
    inventory = {r['artifact_id']: r for r in csv.DictReader((HERE / 'results/report-inventory.csv').open())}
    grades = {r['artifact_id']: r for r in csv.DictReader((HERE / 'results/published-grades.csv').open())}
    problem = {'contradicted', 'exceeds_support'}
    primary = [r for r in reviews.values() if inventory[r['artifact_id']]['group'] == 'main']
    primary_counts = dict(with_problem=sum(any(c['judgment'] in problem for c in r['claims']) for r in primary),
        with_problem_excluding_disputed=sum(any(c['judgment'] in problem and not c['disputable'] for c in r['claims']) for r in primary))
    corrected = {r['parent'] for r in csv.DictReader((HERE / 'results/followup-pairs-corrected.csv').open())}
    comparisons = [json.loads(f.read_text()) for folder in ['pairs', 'pairs-repaired'] for f in (HERE / folder).glob('*.json')]
    selected = [p for p in comparisons if p['parent'] in corrected]
    assert len(selected) == len({p['followup'] for p in selected}) == 78
    pair_counts = dict(pairs_with_parent_problem=0, pairs_with_retained_problem=0,
        coverage_increased=0, coverage_increased_with_retained_problem=0,
        coverage_increased_with_retained_problem_excluding_disputed=0,
        pairs_with_correction_or_qualification=0, pairs_with_correction_or_qualification_excluding_disputed=0)
    for pair in selected:
        parent, followup = reviews[pair['parent_review_id']], reviews[pair['followup_review_id']]
        retained = strict_retained = repair = strict_repair = False
        has_problem = any(c['judgment'] in problem for c in parent['claims'])
        for transition in pair['transitions']:
            c = parent['claims'][transition['parent_claim_index'] - 1]
            if c['judgment'] not in problem:
                continue
            target = [followup['claims'][i - 1] for i in transition['followup_claim_indices']]
            disputed = c['disputable'] or transition['disputable']
            if transition['transition'] == 'retained_problem':
                retained = True
                strict_retained |= not disputed and any(x['judgment'] in problem and not x['disputable'] for x in target)
            if transition['transition'] in ['corrected_statement', 'qualified_statement']:
                repair = True
                strict_repair |= not disputed and any(x['judgment'] in {'supported_observation', 'qualified_inference'} and not x['disputable'] for x in target)
        gained = float(grades[followup['artifact_id']]['finding_coverage']) > float(grades[parent['artifact_id']]['finding_coverage'])
        values = [has_problem, retained, gained, gained and retained, gained and strict_retained, repair, strict_repair]
        for key, value in zip(pair_counts, values):
            pair_counts[key] += int(value)
    analysis = json.loads((HERE / 'results/study/analysis.json').read_text())
    aggregate_primary = next(r for r in analysis['cohort_summary'] if r['scope'] == 'main')
    aggregate_pairs = next(r for r in analysis['paired_summary'] if r['selection'] == 'corrected_primary' and r['budget_min'] == 'all')
    for counts, aggregate in [(primary_counts, aggregate_primary), (pair_counts, aggregate_pairs)]:
        for key, value in counts.items():
            assert value == aggregate[key], (key, value, aggregate[key])
    out = dict(scope='Selected contested cases; assistant reassessment, not a second full-corpus reading or human adjudication',
               input_sha256={n: hashlib.sha256((source / f'{n}.jsonl').read_bytes()).hexdigest() for n in data},
               facts=facts, request_save_pairs=pairs,
               positive_record_checks=[dict(id=i, time=by_id[i]['time'], body_sha256=hashlib.sha256(by_id[i]['body'].encode()).hexdigest()) for i in positive_ids],
               independent_headline_check=dict(primary=primary_counts, continuations=pair_counts),
               limits=['The prepared request sample is not a complete traffic denominator.',
                       'Later preference records often retain an action label, not the full payload. All 25 cannot be called verified injections.',
                       'Unmatched requests are not demonstrated failures; repeated matches are not direct browser traces.',
                       'Dated later saves support persistence at those times, not indefinite live access.'])
    (HERE / 'results/contested-record-checks.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(facts, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, default=HERE.parents[2] / '.local/wiki-containment-20260915')
    main(parser.parse_args().cache)
