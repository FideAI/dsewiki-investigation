"""Recompute bounded record observations; no incident text or URLs are executed."""
import argparse,csv,hashlib,json,sqlite3
from collections import defaultdict,Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent

def run(cache):
    src=cache/'data/verbatim';rows={f:[json.loads(x) for x in (src/f'{f}.jsonl').open()] for f in ['revisions','pages','events','labels']}
    rev=rows['revisions'];pages=rows['pages'];events=rows['events'];deletes=[x for x in events if x['event_type']=='delete']
    out=HERE/'results';out.mkdir(exist_ok=True)
    db=sqlite3.connect(cache/'record-query.sqlite3')
    db.executescript('DROP TABLE IF EXISTS revisions;DROP TABLE IF EXISTS events;DROP TABLE IF EXISTS pages;CREATE TABLE revisions(id TEXT PRIMARY KEY,page_key TEXT,wiki TEXT,label TEXT,ip16 TEXT,time TEXT,body TEXT,declared_len INT,actual_chars INT,utf8_bytes INT,change_summary TEXT);CREATE TABLE events(id TEXT PRIMARY KEY,kind TEXT,page_key TEXT,time TEXT,label TEXT,ip16 TEXT,request TEXT,json TEXT);CREATE TABLE pages(page_key TEXT PRIMARY KEY,wiki TEXT,name TEXT,n_revs INT,n_revs_before INT,body_bytes INT);')
    db.executemany('INSERT INTO revisions VALUES(?,?,?,?,?,?,?,?,?,?,?)',[(r['rev_id'],r['page_key'],r['wiki'],r.get('label'),r.get('ip16'),r.get('time'),r.get('body',''),r.get('body_len'),len(r.get('body','')),len(r.get('body','').encode()),r.get('change_summary')) for r in rev])
    db.executemany('INSERT INTO events VALUES(?,?,?,?,?,?,?,?)',[(e['event_id'],e['event_type'],e.get('page_key'),e.get('time'),e.get('actor_label',e.get('label')),e.get('ip16'),e.get('request',e.get('request_action')),json.dumps(e,ensure_ascii=False)) for e in events])
    db.executemany('INSERT INTO pages VALUES(?,?,?,?,?,?)',[(p['page_key'],p['wiki'],p['name'],p['n_revs'],p['n_revs_before'],p['body_bytes']) for p in pages]);db.executescript('CREATE INDEX rev_page ON revisions(page_key,time); CREATE INDEX event_page ON events(page_key,time);');db.commit()
    queries={
      'revision_scale':'SELECT COUNT(*),COUNT(DISTINCT page_key),SUM(declared_len),SUM(actual_chars),SUM(utf8_bytes),MAX(actual_chars),MIN(time),MAX(time) FROM revisions',
      'page_scale':'SELECT COUNT(*),SUM(body_bytes),MAX(body_bytes) FROM pages',
      'largest_cumulative_page':'SELECT p.page_key,p.body_bytes,COUNT(r.id),MAX(r.actual_chars),SUM(r.actual_chars) FROM pages p JOIN revisions r USING(page_key) GROUP BY p.page_key ORDER BY p.body_bytes DESC LIMIT 5',
      'largest_single_snapshots':'SELECT id,actual_chars,utf8_bytes FROM revisions ORDER BY actual_chars DESC LIMIT 5',
      'moderator_prefix_writes':"SELECT label,COUNT(*),MIN(time),MAX(time) FROM revisions WHERE ip16='2.202' GROUP BY label",
      'delete_targets':'SELECT COUNT(*),COUNT(DISTINCT page_key),MIN(time),MAX(time) FROM events WHERE kind=\'delete\'',
      'unicode_name_writes':"SELECT label,COUNT(*) FROM revisions WHERE label LIKE 'Fri%1982' GROUP BY label",
      'later_revisions':'SELECT COUNT(*),COUNT(DISTINCT r.page_key) FROM revisions r JOIN (SELECT page_key,MIN(time) AS t FROM events WHERE kind=\'delete\' GROUP BY page_key) d ON r.page_key=d.page_key WHERE r.time>d.t',
      'after_final_delete':'SELECT COUNT(*) FROM revisions r JOIN (SELECT page_key,MAX(time) AS t FROM events WHERE kind=\'delete\' GROUP BY page_key) d ON r.page_key=d.page_key WHERE r.time>d.t',
      'request_schema':"SELECT COUNT(*),MIN(time),MAX(time) FROM events WHERE kind='request'"
    }
    result={'input_hashes':{f:hashlib.sha256((src/f'{f}.jsonl').read_bytes()).hexdigest() for f in rows},'queries':{name:{'sql':q,'columns':[d[0] for d in db.execute(q).description],'rows':db.execute(q).fetchall()} for name,q in queries.items()},'limits':['Stored body totals aggregate revisions and can repeat the same content; they do not measure bytes actually transmitted or largest live page.','body_len and body_bytes are retained declared character-based metadata, affected by prior transformations; explicit actual_chars/utf8_bytes measure current restored text.','Name labels and truncated prefixes are not authentication.','Static request/payload or participant text is not proof of browser execution, network response, task outcome or external process survival.']}
    (out/'expanded-record-checks.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    selected=[]
    for e in events:
        if e['event_id'] in ['delete:dse:rclog:131972','delete:dse:rclog:151005'] or e.get('time_precision')=='day' or e.get('time')=='2026-06-18T17:44:47Z':selected.append(e)
    (out/'record-anchors.json').write_text(json.dumps(selected,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:v['rows'] for k,v in result['queries'].items()},indent=2,ensure_ascii=False))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cache',type=Path,required=True);run(p.parse_args().cache)
