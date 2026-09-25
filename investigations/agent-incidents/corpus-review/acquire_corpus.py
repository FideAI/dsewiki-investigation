"""Fetch the pinned publication corpus as inert files; no inference or payload execution."""
import argparse,concurrent.futures,hashlib,json
from pathlib import Path
from urllib.request import Request,urlopen

COMMIT='e1eea3b4eaf93f9a7e2898da97096ef643916da1'
REPO='hamzah2304/messageboardauditbench'
EXTRA={'reports/round4/index.jsonl','reports/provider_swap/index.jsonl','reports/index.jsonl','benchmark/figures/combined_score.json','benchmark/figures/followup_5k.json','benchmark/figures/followup_5k.csv','docs/benchmark-data-index.md','docs/artifacts/inspect-logs.md','experiments/round4.toml','experiments/provider_swap.toml','experiments/ablations.md','viewers/figures/results_figures.md'}
def get(url):
    with urlopen(Request(url,headers={'User-Agent':'Fide-research'}),timeout=45) as r:return r.read()
def run(cache):
    treepath=cache/'repository-tree.json'
    tree=json.loads(treepath.read_text()) if treepath.exists() else json.loads(get(f'https://api.github.com/repos/{REPO}/git/trees/{COMMIT}?recursive=1'))
    assert not tree.get('truncated')
    cache.mkdir(parents=True,exist_ok=True);treepath.write_text(json.dumps(tree,indent=2)+'\n')
    entries=[x for x in tree['tree'] if x['type']=='blob' and (x['path'].startswith('benchmark/graded_inputs/') and x['path'].endswith(('.md','_index.jsonl')) or x['path'] in EXTRA or x['path'].startswith('reports/followup') and x['path'].endswith('index.jsonl'))]
    def fetch(x):
        dest=cache/x['path'];url=f'https://raw.githubusercontent.com/{REPO}/{COMMIT}/{x["path"]}'
        raw=dest.read_bytes() if dest.exists() else get(url)
        gitsha=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        assert gitsha==x['sha'],x['path']
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        return {'path':x['path'],'url':url,'git_blob_sha1':gitsha,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:results=list(pool.map(fetch,entries))
    manifest={'repository':REPO,'commit':COMMIT,'scope':'All staged report cohorts in pinned publication snapshot, plus comparison metadata; no historical tags','artifacts':sorted(results,key=lambda x:x['path'])}
    (cache/'corpus-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'downloaded_or_verified':len(results),'bytes':sum(x['bytes'] for x in results)},indent=2))
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--cache',type=Path,required=True);run(parser.parse_args().cache)
