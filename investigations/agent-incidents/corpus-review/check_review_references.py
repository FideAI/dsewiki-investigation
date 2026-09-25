"""Validate direct evidence record IDs; this checks existence, not interpretation."""
import json,re,sqlite3
from collections import defaultdict
from pathlib import Path
HERE=Path(__file__).resolve().parent
CACHE=HERE.parents[2]/'.local/wiki-containment-20260915'
def main():
 db=sqlite3.connect(f'file:{CACHE / "record-query.sqlite3"}?mode=ro',uri=True)
 ids={r[0]for r in db.execute('SELECT id FROM revisions UNION SELECT id FROM events')}
 for p in (CACHE/'data/verbatim_anthropic').glob('*.jsonl'):
  for line in p.open():
   d=json.loads(line)
   for key in ['rev_id','event_id']:
    if key in d:ids.add(d[key])
 unresolved=[];checked=0
 for p in sorted((HERE/'reviews').glob('C*.json')):
  d=json.loads(p.read_text())
  for i,c in enumerate(d['claims'],1):
   for e in c['evidence']:
    if re.fullmatch(r'(?:dse|fractal|probier|dorfwiki)~[^ ]+@\d+|(?:request|delete|save):[^ ]+',e):
     checked+=1
     if e not in ids:unresolved.append(dict(review_id=d['review_id'],claim_index=i,reference=e))
 out=dict(direct_references_checked=checked,unresolved=unresolved,limits='Existence check only. Shorthand ranges and prose references are not expanded. Source relevance and interpretation require reading.')
 (HERE/'results/review-reference-check.json').write_text(json.dumps(out,indent=2)+'\n')
 assert not unresolved,json.dumps(unresolved,indent=2)
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
