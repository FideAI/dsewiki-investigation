"""Check published followup pairing, exact-text identity, and score arithmetic."""
import csv,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
CACHE=HERE.parents[2]/'.local/wiki-containment-20260915'

def normalize(x):return re.sub('[^a-zA-Z0-9]+','_',Path(x).stem).strip('_')
def main():
    inventory=list(csv.DictReader((HERE/'results/report-inventory.csv').open()))
    by={normalize(x['path']):x for x in inventory if x['artifact_type']=='indexed_report'}
    assert len(by)==sum(x['artifact_type']=='indexed_report' for x in inventory)
    figure=json.loads((CACHE/'benchmark/figures/followup_5k.json').read_text())
    rows=[]
    for point in figure['points']:
        for run in point['runs']:
            p,f=by[run['parent']],by[run['follow']]
            parent=(CACHE/p['path']).read_bytes();follow=(CACHE/f['path']).read_bytes()
            row={'parent':run['parent'],'followup':run['follow'],'parent_path':p['path'],'followup_path':f['path'],'parent_sha256':hashlib.sha256(parent).hexdigest(),'followup_sha256':hashlib.sha256(follow).hexdigest(),'identical_text':parent==follow,'parent_words':len(parent.decode().split()),'followup_words':len(follow.decode().split()),'parent_budget_min':run['budget'],'agent':run['agent'],'model_display':run['model'],'replicate':run['rep'],'published_parent_coverage':run['short'],'published_followup_coverage':run['long'],'published_parent_tldr':run['short_tldr'],'published_followup_tldr':run['long_tldr'],'support_improvement':'not_assessed','cause_of_score_change':'not_established'}
            rows.append(row)
    assert len({r['followup'] for r in rows})==len(rows)
    unmatched=[x['path'] for key,x in by.items() if x['group']=='followup_min5' and key not in {r['followup'] for r in rows}]
    same=[r for r in rows if r['identical_text']]
    with (HERE/'results/followup-pairs.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary={'published_pairs':len(rows),'indexed_min5_followups':sum(x['group']=='followup_min5' for x in inventory),'followups_absent_from_pair_figure':unmatched,'identical_text_pairs':same,'interpretation':'Identical published report texts receive different published scores. This does not establish why: scoring variation, export/staging differences or mapping need investigation. Grade movement alone cannot establish substantive improvement.','claims_not_made':['No full-text reading of additional reports claimed.','No causal effect of time or length estimated.','No fraud, misconduct or benchmark invalidity inferred.']}
    (HERE/'results/comparison-integrity.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
