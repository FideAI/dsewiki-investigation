"""Download inert published run archives and check release hashes. Does not extract or execute."""
import argparse,concurrent.futures,hashlib,json,urllib.request
from pathlib import Path
HERE=Path(__file__).resolve().parent;CACHE=HERE.parents[2]/'.local/wiki-containment-20260915/log-archives'
def main(names):
    release=json.loads((HERE/'results/log-release-index.json').read_text());assets={x['name']:x for x in release['assets']}
    hashes={l.split()[1].lstrip('*'):l.split()[0]for l in(HERE/'results/log-archive-SHA256SUMS').read_text().splitlines()}
    CACHE.mkdir(exist_ok=True)
    def download(name):
        target=CACHE/name;a=assets[name]
        if not target.exists():
            temp=target.with_suffix('.download')
            with urllib.request.urlopen(a['url'],timeout=60)as response,temp.open('wb')as f:
                while chunk:=response.read(1024*1024):f.write(chunk)
            assert temp.stat().st_size==a['size'];temp.rename(target)
        sha=hashlib.file_digest(target.open('rb'),'sha256').hexdigest();assert sha==hashes[name],name
        return {'name':name,'url':a['url'],'bytes':target.stat().st_size,'sha256':sha}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:records=list(pool.map(download,names))
    (HERE/'results/run-archive-acquisition.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(records,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('names',nargs='*',default=['round4.tar','followup-5k-min5.tar']);main(p.parse_args().names)
