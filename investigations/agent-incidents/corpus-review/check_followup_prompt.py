"""Check the continuation instruction against pinned Codex and ReAct exports."""
import csv,hashlib,json,urllib.request
from pathlib import Path
HERE=Path(__file__).resolve().parent
CACHE=HERE.parents[2]/'.local/wiki-containment-20260915'
COMMIT='e1eea3b4eaf93f9a7e2898da97096ef643916da1'
def main():
 rows=[]
 for agent in ['codex','react']:
  p=f'reports/followup-5k-min5/{agent}/prompts/93b57375.txt';url=f'https://raw.githubusercontent.com/hamzah2304/messageboardauditbench/{COMMIT}/{p}';dest=CACHE/p
  raw=dest.read_bytes()if dest.exists()else urllib.request.urlopen(url).read()
  assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()=='ac3adcfbed6a248fea77f07baa3be0c9b3a2f793'
  dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
  rows.append(dict(agent=agent,path=p,url=url,sha256=hashlib.sha256(raw).hexdigest()))
 assert rows[0]['sha256']==rows[1]['sha256']
 inventory=list(csv.DictReader((HERE/'results/report-inventory.csv').open()));f=[r for r in inventory if r['group']=='followup_min5']
 out=dict(sources=rows,indexed_followups=len(f),recorded_prompt_ids=sorted({r['prompt_id']for r in f}),summary='The continuation asks for expansion to 4,500–5,000 words with more evidence, fuller mechanisms and restored omitted findings. It allows returning to data and asks for verification, but does not specifically direct a systematic audit of prior conclusions. It requires editing the existing file in place without deleting, moving or truncating it.',inference_limit='Observed retention under this expansion instruction does not estimate ability to self-correct under a targeted verification or correction prompt.')
 (HERE/'results/followup-prompt-check.json').write_text(json.dumps(out,indent=2)+'\n');print(raw.decode());print(json.dumps(out,indent=2))
if __name__=='__main__':main()
