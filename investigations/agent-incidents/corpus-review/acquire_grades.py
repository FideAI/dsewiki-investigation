"""Acquire the pinned grade sources listed in the local manifest; never regrade."""
import argparse,concurrent.futures,hashlib,json,urllib.request
from pathlib import Path
HERE=Path(__file__).resolve().parent

def main(cache):
    manifest=json.loads((HERE/'results/grade-source-manifest.json').read_text())
    def fetch(row):
        p=cache/row['path']
        if p.exists(): raw=p.read_bytes()
        else:
            raw=urllib.request.urlopen(row['url'],timeout=60).read()
            assert hashlib.sha256(raw).hexdigest()==row['sha256'],row['path']
            p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
        assert hashlib.sha256(raw).hexdigest()==row['sha256'],row['path']
        return row['path']
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        done=list(pool.map(fetch,manifest))
    print(f'Hash-verified {len(done)} pinned sources; no new model scoring.')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cache',type=Path,default=HERE.parents[2]/'.local/wiki-containment-20260915');main(p.parse_args().cache)
