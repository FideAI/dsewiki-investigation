"""Local, human review desk. Reads study artifacts; writes only separate review decisions."""
from __future__ import annotations
import argparse, csv, hashlib, json, os, secrets, sqlite3, threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
STUDY = ROOT / 'investigations/agent-incidents/corpus-review'
CACHE = ROOT / '.local/wiki-containment-20260915'
PIN = 'e1eea3b4eaf93f9a7e2898da97096ef643916da1'
LABELS = {'contradicted':'Contradicted by records','exceeds_support':'Beyond available support',
 'qualified_inference':'Reasonable inference','supported_observation':'Supported observation',
 'unassessable':'Not assessable','retained_problem':'Earlier problem retained',
 'corrected_statement':'Earlier claim corrected','qualified_statement':'Earlier claim narrowed',
 'retained_supported':'Supported claim retained','omitted':'Claim omitted','superseded':'Claim changed'}

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

def load_catalog():
    reviews = {p.stem: json.loads(p.read_text()) for p in sorted((STUDY/'reviews').glob('C*.json'))}
    with (STUDY/'results/study/coverage.csv').open() as f:
        inventory = {r['review_id']:r for r in csv.DictReader(f)}
    items = {}
    def add(item):
        item['fingerprint'] = digest(item)
        items[item['id']] = item
    for rid,r in reviews.items():
        for n,c in enumerate(r['claims'],1):
            add(dict(id=f'{rid}-{n:02}',kind='claim',title=c['claim'],family=c['family'],
                assessment=LABELS.get(c['judgment'],c['judgment']),judgment=c['judgment'],
                disputed=c['disputable'],rationale=c['rationale'],context=c['confidence_context'],
                limits=c['missing_link'],validCore=c['correct_core'],references=c['evidence'],
                sources=[dict(report=rid,lines=c['lines'])],report=rid,group=inventory[rid]['group'],
                question='Do you agree with Fide’s assessment of this report claim?',
                snapshot=c))
    with (STUDY/'results/followup-pairs-corrected.csv').open() as f:
        valid={(r['parent'],r['followup']) for r in csv.DictReader(f)}
    for p in [*sorted((STUDY/'pairs').glob('*.json')),*sorted((STUDY/'pairs-repaired').glob('*.json'))]:
        pair=json.loads(p.read_text())
        if (pair['parent'],pair['followup']) not in valid: continue
        rid, fid = pair['parent_review_id'], pair['followup_review_id']
        for t in pair['transitions']:
            parent=reviews[rid]['claims'][t['parent_claim_index']-1]
            follows=[reviews[fid]['claims'][i-1] for i in t['followup_claim_indices']]
            add(dict(id=f"T-{rid}-{fid}-{t['parent_claim_index']:02}",kind='transition',
                title=parent['claim'],family=parent['family'],assessment=LABELS.get(t['transition'],t['transition']),
                judgment=t['transition'],disputed=bool(t['disputable'] or parent['disputable'] or any(c['disputable'] for c in follows)),
                rationale=t['rationale'],context=pair['summary'],limits='Approving a transition does not independently approve every underlying claim.',
                references=list(dict.fromkeys(parent['evidence']+[e for c in follows for e in c['evidence']])),
                sources=[dict(report=rid,lines=t['parent_lines'],caption='Original report'),dict(report=fid,lines=t['followup_lines'],caption='Follow-up report')],
                related=[f"{rid}-{t['parent_claim_index']:02}"]+[f'{fid}-{i:02}' for i in t['followup_claim_indices']],
                followupClaims=[c['claim'] for c in follows],report=rid,group='followup',
                question='Do you agree with how Fide classified the change between these reports?',snapshot=t))
    a=json.loads((STUDY/'results/study/analysis.json').read_text())
    pair=next(r for r in a['paired_summary'] if r['selection']=='corrected_primary' and r['budget_min']=='all')
    main=next(r for r in a['cohort_summary'] if r['scope']=='main')
    article=(STUDY/'insights-body.mdx').read_text()
    paper=(STUDY/'paper.md').read_text()
    publications=[
      ('P01','A better score does not mean the earlier mistakes are gone.','Central argument',
       'Review whether this is a fair summary of the observed follow-ups. Better scores measure reconstruction of reference findings; they do not establish correction of each earlier claim.',
       'This is a descriptive result from one benchmark, not a general claim that AI investigators cannot correct themselves.', ['results/study/analysis.json','paper.md']),
      ('P02',f"{pair['coverage_increased']} of 78 follow-ups earned higher finding scores. Of those {pair['coverage_increased']}, {pair['coverage_increased_with_retained_problem']} retained an earlier flagged claim ({pair['coverage_increased_with_retained_problem_excluding_disputed']} excluding disputed judgments).",'Headline finding',
       'Review the denominator, what “higher score” means, and the distinction between a factual contradiction and insufficient support.',
       'Approving this summary does not independently adjudicate all underlying claim or transition judgments. One identical-text pair received different scores.', ['results/study/analysis.json','results/contested-record-checks.json']),
      ('P03',f"{pair['pairs_with_correction_or_qualification']} of {pair['pairs_with_parent_problem']} follow-ups corrected or properly narrowed at least one earlier flagged claim; {pair['pairs_with_correction_or_qualification_excluding_disputed']} excluding disputed judgments.",'Correction finding',
       'Check whether “correction” is defined fairly and whether the article gives enough weight to the expansion instructions. Omission is not counted as correction.',
       'The exercise asked for expansion, with verification, while preserving the file and structure. It did not explicitly ask investigators to challenge earlier conclusions.', ['results/study/analysis.json','PAIR_CODEBOOK.md','results/followup-prompt-check.json']),
      ('P04',f"All 113 primary reports contain supported analysis; {main['with_problem']} also contain a flagged conclusion ({main['with_problem_excluding_disputed']} excluding disputed interpretations).",'Primary report finding',
       'Review whether the wording communicates that good and problematic claims can appear in the same report.',
       'This is not a sentence-level error rate or a severity-weighted measure. Judgments still need independent human review.', ['results/study/analysis.json','CODEBOOK.md']),
      ('P05','We reviewed 297 indexed reports and seven rejected attempts, including 113 primary reports and 78 matched continuations.','Scope of review',
       'Review whether our completeness claim is appropriately limited to the pinned publication release.',
       'There are 304 artifacts and 303 distinct texts, not 304 independent investigations. Earlier development rounds are excluded.', ['results/study/coverage.csv','paper.md']),
      ('P06','Before a report guides a security decision, check the evidence for the claim behind that decision.','Implication for Fide',
       'Review whether the recommendation follows from the examples, and whether the link to autonomous-defense research is proportionate.',
       'This review did not test a verification intervention or observe responders acting on these reports. This is a proposed standard and future experiment.', ['paper.md','insights-body.mdx']),
    ]
    for id,title,category,rationale,limits,refs in publications:
        add(dict(id=id,kind='publication',title=title,family='publication',assessment=category,
            judgment='publication_claim',disputed=False,rationale=rationale,context='Website article and methods paper',
            limits=limits,references=refs,sources=[],report='',group='publication',
            question='Do you approve this finding or argument as presented in Fide’s publication?',
            snapshot={'article_sha256':digest(article),'paper_sha256':digest(paper),'analysis':digest(a)}))
    featured=['P01','P02','P03','P04','P05','P06','C263-09','C286-11','C273-07','C284-10','C200-08','C254-03','C240-06','C276-01','T-C276-C098-01']
    for n,id in enumerate(featured):
        assert id in items,id
        items[id]['priority']=n+1
    # Only evidence files already cited in the study are exposed; never arbitrary paths.
    resources={}
    for item in items.values():
        for ref in item['references']:
            raw=ref.split('#')[0]
            candidates=[STUDY/raw,ROOT/raw,STUDY.parent/raw]
            path=next((p.resolve() for p in candidates if p.is_file() and p.resolve().is_relative_to(ROOT) and p.suffix in {'.json','.jsonl','.csv','.md','.mdx','.py','.txt'}),None)
            if path: resources[ref]=path
    return items,reviews,inventory,resources

class Store:
    def __init__(self,folder,items):
        self.folder=folder;folder.mkdir(parents=True,exist_ok=True);self.path=folder/'decisions.json'
        self.items=items;self.lock=threading.Lock()
        if not self.path.exists(): self._write({'schema':1,'decisions':{},'history':[]})
    def read(self): return json.loads(self.path.read_text())
    def _write(self,data):
        tmp=self.folder/'decisions.tmp'
        with tmp.open('w') as f:
            json.dump(data,f,indent=2,ensure_ascii=False);f.write('\n');f.flush();os.fsync(f.fileno())
        os.replace(tmp,self.path)
    def save(self,payload):
        with self.lock:
            id=payload.get('id');item=self.items.get(id)
            if not item: raise ValueError('Unknown review item.')
            if payload.get('fingerprint')!=item['fingerprint']: raise ValueError('This item changed. Reload before reviewing it.')
            status=payload.get('status')
            if status not in {'pending','approved','rejected','commented'}:raise ValueError('Choose a valid decision.')
            comment=payload.get('comment',''); reviewer=payload.get('reviewer','')
            if not isinstance(comment,str) or len(comment)>20000:raise ValueError('Comment must be text of at most 20,000 characters.')
            if not isinstance(reviewer,str) or len(reviewer)>120:raise ValueError('Reviewer name is too long.')
            if status=='commented' and not comment.strip():raise ValueError('Write a comment or choose another decision.')
            data=self.read();old=data['decisions'].get(id,{})
            if payload.get('revision',0)!=old.get('revision',0):raise ValueError('This review was updated in another tab. Reload to see it before saving.')
            decision=dict(id=id,status=status,comment=comment,reviewer=reviewer.strip(),revision=old.get('revision',0)+1,
                fingerprint=item['fingerprint'],updated=datetime.now(timezone.utc).isoformat(),
                item_snapshot={k:item[k] for k in ['title','assessment','kind','rationale','limits','sources']})
            data['decisions'][id]=decision;data['history'].append(decision);self._write(data)
            return decision
    def export(self):
        d=self.read();d.update(exported=datetime.now(timezone.utc).isoformat(),study_pin=PIN,
            meaning='Approvals apply to Fide assessments or publication wording. They do not change study judgments, certify the paper, or approve deployment.',
            stale_ids=[id for id,v in d['decisions'].items() if id not in self.items or v['fingerprint']!=self.items[id]['fingerprint']])
        return d

def make_server(port=3002,folder=None):
    items,reviews,inventory,resources=load_catalog()
    store=Store(folder or ROOT/'.local/claim-review',items)
    token=secrets.token_urlsafe(32)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def send(self,data,status=200,mime='application/json',download=None):
            body=(json.dumps(data,ensure_ascii=False).encode() if mime=='application/json' else data.encode() if isinstance(data,str) else data)
            self.send_response(status);self.send_header('Content-Type',mime+'; charset=utf-8');self.send_header('Content-Length',str(len(body)))
            self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'")
            if download:self.send_header('Content-Disposition',f'attachment; filename="{download}"')
            self.end_headers();self.wfile.write(body)
        def permitted_host(self):
            return self.headers.get('Host') in {f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'}
        def do_GET(self):
            if not self.permitted_host():return self.send({'error':'Local access only.'},403)
            url=urlparse(self.path);q=parse_qs(url.query);id=q.get('id',[''])[0]
            if url.path in {'/','/app.js','/style.css'}:
                f={'/':'index.html','/app.js':'app.js','/style.css':'style.css'}[url.path]
                mime={'/':'text/html','/app.js':'text/javascript','/style.css':'text/css'}[url.path]
                return self.send((HERE/f).read_bytes(),mime=mime)
            if url.path=='/api/catalog':
                summaries=[{k:v for k,v in item.items() if k in {'id','kind','title','family','assessment','disputed','report','group','priority','fingerprint'}} for item in items.values()]
                return self.send(dict(items=summaries,decisions=store.read()['decisions'],token=token,savePath=str(store.path),studyPin=PIN))
            if url.path=='/api/item' and id in items:
                item=dict(items[id]);item['sources']=[self.source(s) for s in item['sources']]
                item['evidence']=[dict(reference=e,available=e in resources or self.record(e) is not None) for e in item['references']]
                return self.send(item)
            if url.path=='/api/report' and id in reviews:
                return self.send(self.source(dict(report=id,lines=[]),full=True))
            if url.path=='/api/evidence':
                if id in resources:
                    p=resources[id];raw=p.read_text();fragment=id.partition('#')[2]
                    if p.suffix=='.json':
                        try:
                            parsed=json.loads(raw)
                            if fragment and isinstance(parsed,dict) and fragment in parsed:parsed=parsed[fragment]
                            raw=json.dumps(parsed,indent=2,ensure_ascii=False)
                        except ValueError:pass
                    return self.send(dict(title=id,text=raw[:250000],truncated=len(raw)>250000))
                record=self.record(id)
                if record is not None:return self.send(dict(title=id,text=json.dumps(record,indent=2,ensure_ascii=False),truncated=False))
                return self.send({'error':'This reference is shorthand or is not available in the local cache. Inspect the full source report or leave a comment requesting the missing evidence.'},404)
            if url.path=='/api/export':return self.send(store.export(),download='dsewiki-human-review.json')
            if url.path=='/api/export.md':
                data=store.export();lines=['# DSEWiki human review','',data['meaning'],'']
                for d in data['decisions'].values():
                    lines += [f"## {d['id']} · {d['status']}",d['item_snapshot']['title'],'',f"Reviewer: {d['reviewer'] or 'Not entered'} · {d['updated']}",'',d['comment'] or '(No comment)','']
                return self.send('\n'.join(lines),mime='text/plain',download='dsewiki-human-review.md')
            self.send({'error':'Not found.'},404)
        def source(self,s,full=False):
            rid=s['report'];r=reviews[rid];p=CACHE/r['path']
            if not p.is_file():return dict(**s,available=False,error='Original report is not in the local cache.')
            lines=p.read_text().splitlines();wanted=set()
            for n in s['lines']:
                wanted.update(range(max(1,n-2),min(len(lines),n+2)+1))
            if full:wanted=set(range(1,len(lines)+1))
            return dict(**s,available=True,url=inventory[rid]['source_url'].replace('raw.githubusercontent.com/hamzah2304/messageboardauditbench/','github.com/hamzah2304/messageboardauditbench/blob/')+('#L'+str(min(s['lines'])) if s['lines'] else ''),
                title=Path(r['path']).name,sha256=r['sha256'],hashMatches=hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],totalLines=len(lines),
                excerpt=[dict(number=n,text=lines[n-1],highlight=n in s['lines']) for n in sorted(wanted)])
        def record(self,id):
            if not ('@' in id or id.startswith(('request:','delete:','save:'))):return None
            dbpath=CACHE/'record-query.sqlite3'
            if not dbpath.exists():return None
            with sqlite3.connect(f'file:{dbpath}?mode=ro',uri=True) as db:
                db.row_factory=sqlite3.Row
                for table in ['revisions','events']:
                    row=db.execute(f'SELECT * FROM {table} WHERE id=?',(id,)).fetchone()
                    if row:return dict(row)
            return None
        def do_POST(self):
            origin=self.headers.get('Origin');expected={f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}'}
            if not self.permitted_host() or (origin and origin not in expected) or self.headers.get('X-Review-Token')!=token:
                return self.send({'error':'Review session expired or invalid origin. Reload the app.'},403)
            if self.path!='/api/decision':return self.send({'error':'Not found.'},404)
            if self.headers.get('Content-Type','').split(';')[0]!='application/json':return self.send({'error':'JSON required.'},415)
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=100000:raise ValueError('Invalid request size.')
                payload=json.loads(self.rfile.read(length))
                if not isinstance(payload,dict):raise ValueError('Expected a decision object.')
                self.send(store.save(payload))
            except (ValueError,TypeError) as e:self.send({'error':str(e)},400)
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    return server,store

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=3002);p.add_argument('--data-dir',type=Path)
    args=p.parse_args();server,store=make_server(args.port,args.data_dir)
    print(f'Review desk: http://127.0.0.1:{server.server_port}\nDecisions: {store.path}',flush=True)
    server.serve_forever()
