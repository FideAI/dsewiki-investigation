"""Reproduce the published identical-text grade discrepancy; does not infer its cause."""
import hashlib,json
from pathlib import Path
from urllib.request import urlopen
HERE=Path(__file__).resolve().parent
CACHE=HERE.parents[2]/'.local/wiki-containment-20260915'

def main():
    sources=json.loads((HERE/'results/grade-check-sources.json').read_text())
    grades={}
    for s in sources:
        p=CACHE/s['path']
        raw=p.read_bytes() if p.exists() else urlopen(s['url'],timeout=30).read()
        assert hashlib.sha256(raw).hexdigest()==s['sha256'],s['path']
        p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
        j=json.loads(raw);grades[(j['report'],j['rubric'])]=j
    source=json.loads((HERE/'results/comparison-integrity.json').read_text())
    pair=source['identical_text_pairs'][0]
    assert (CACHE/pair['parent_path']).read_bytes()==(CACHE/pair['followup_path']).read_bytes()
    results=[]
    for label in ['parent','followup']:
        name=pair[label];items=grades[(name,'v2')]['scores'];assert len(items)==38
        cov=sum(max(2*x['score']-1,0) for x in items.values())/len(items)
        tldr=grades[(name,'tldrh')]['total']
        assert abs(cov-pair[f'published_{label}_coverage'])<1e-12
        assert abs(tldr-pair[f'published_{label}_tldr'])<1e-12
        results.append({'report':name,'coverage':cov,'tldr':tldr,'headline':.7*cov+.3*tldr,'items':{k:v['score'] for k,v in items.items()}})
    result={'grade_sources':'grade-check-sources.json','recomputed':results,'interpretation':'Published staged texts are identical; four grade files confirm score differences. Source grading session inputs and reason for different judgments have not been validated.'}
    (HERE/'results/identical-text-grade-check.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Verified identical text and distinct published grade values; causal explanation remains unresolved.')
if __name__=='__main__':main()
