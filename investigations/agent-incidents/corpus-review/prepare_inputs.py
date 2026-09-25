"""Reconstruct the pinned input variants using inspected upstream data transforms.

Only three hash-verified preparation scripts run. Incident URLs and embedded
payloads remain inert strings. Zip extraction is restricted to four JSONL files.
"""
import argparse,hashlib,json,subprocess,sys,zipfile
from pathlib import Path
from acquire_corpus import COMMIT,REPO,get
HERE=Path(__file__).resolve().parent
FILES=['events.jsonl','labels.jsonl','pages.jsonl','revisions.jsonl']
ARCHIVE_SHA='eb68aa12d26bf189d8bfc4ce47f4d8af66ae5ba7ebbadd429738297a3cbb25ae'

def main(cache):
 tree=json.loads((cache/'repository-tree.json').read_text())
 entries={x['path']:x for x in tree['tree']if x['type']=='blob'}
 sources=[]
 for path in ['scripts/strip_analysis_fields.py','scripts/fill_verbatim.py','scripts/swap_provider.py','benchmark/human_report.txt']:
  target=cache/path;url=f'https://raw.githubusercontent.com/{REPO}/{COMMIT}/{path}'
  raw=target.read_bytes()if target.exists()else get(url)
  assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==entries[path]['sha'],path
  target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
  sources.append(dict(path=path,url=url,sha256=hashlib.sha256(raw).hexdigest()))
 archive=cache/'data/raw/full-wiki-logs.zip';archive.parent.mkdir(parents=True,exist_ok=True)
 raw=archive.read_bytes()if archive.exists()else get('https://collusion.wiki/explorer/download/full-wiki-logs.zip')
 assert hashlib.sha256(raw).hexdigest()==ARCHIVE_SHA
 archive.write_bytes(raw)
 with zipfile.ZipFile(archive)as z:
  for name in FILES:
   matches=[n for n in z.namelist()if Path(n).name==name]
   assert len(matches)==1,(name,matches)
   (archive.parent/name).write_bytes(z.read(matches[0]))
 commands=[['scripts/strip_analysis_fields.py','data/raw','data/raw_stripped'],['scripts/fill_verbatim.py','data/raw_stripped','data/verbatim','benchmark/human_report.txt'],['scripts/swap_provider.py','data/verbatim','data/verbatim_anthropic']]
 for command in commands:subprocess.run([sys.executable,*command],cwd=cache,check=True,capture_output=True,text=True)
 checks=json.loads((HERE/'results/variant-checks.json').read_text())['checks']
 for check in checks:assert hashlib.sha256((cache/check['file']).read_bytes()).hexdigest()==check['expected'],check['file']
 (HERE/'results/input-preparation-sources.json').write_text(json.dumps(dict(commit=COMMIT,archive_sha256=ARCHIVE_SHA,sources=sources,verified_input_files=len(checks)),indent=2)+'\n')
 print(f'{len(checks)} reconstructed input hashes match the pinned expected files.')
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cache',type=Path,default=HERE.parents[2]/'.local/wiki-containment-20260915');main(p.parse_args().cache.resolve())
