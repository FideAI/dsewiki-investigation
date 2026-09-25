"""Verify released files and reproducibility of derived outputs, offline."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];STUDY=ROOT/'investigations/agent-incidents/corpus-review'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((ROOT/'release-manifest.json').read_text())
for name,digest in manifest['files'].items():
    assert sha(ROOT/name)==digest,f'Release file changed: {name}'
outputs=[STUDY/'results/study/analysis.json',STUDY/'paper.md',STUDY/'insights-body.mdx',STUDY/'newsletter.md',ROOT/'explorer/data.json']
before={str(p):sha(p) for p in outputs}
for script in [STUDY/'analyze_study.py',STUDY/'render_deliverables.py',ROOT/'scripts/build_explorer.py']:
    subprocess.run([sys.executable,str(script)],cwd=ROOT,check=True)
assert all(sha(Path(p))==digest for p,digest in before.items()),'Regeneration changed released results.'
data=json.loads((ROOT/'explorer/data.json').read_text());ids=[i['id'] for i in data['items']]
assert len(ids)==len(set(ids))==4633
assert sum(i['kind']=='claim' for i in data['items'])==3715
assert sum(i['kind']=='transition' for i in data['items'])==912
assert not any('decisions' in i or 'reviewer' in i for i in data['items'])
print(f'Verified {len(manifest["files"])} released files; outputs reproduce exactly. Judgment adjudication is separate.')
