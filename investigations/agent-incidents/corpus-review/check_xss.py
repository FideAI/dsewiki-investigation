"""Decode an inert payload as JSON and compare its intended body with saved revisions.
No JavaScript, URLs, incident commands or model calls are executed.
"""
import base64,json,re,sqlite3
from pathlib import Path
HERE=Path(__file__).resolve().parent
CACHE=HERE.parents[2]/'.local/wiki-containment-20260915'

def main():
    db=sqlite3.connect(CACHE/'record-query.sqlite3');db.row_factory=sqlite3.Row
    request=dict(db.execute("SELECT * FROM events WHERE id='request:dse:5911'").fetchone())
    # request text is decoded in the supplied export. Decode only the static base64 JSON literal.
    match=re.search(r'atob\([\"\']([A-Za-z0-9+/=]+)[\"\']\)',request['request'])
    assert match,'Static base64 literal missing'
    payload=json.loads(base64.b64decode(match.group(1),validate=True));key='dse~'+payload['inputs']['id']
    rows=[]
    for r in db.execute('SELECT * FROM revisions WHERE page_key=? ORDER BY time',(key,)):
        rows.append({'id':r['id'],'label':r['label'],'ip16':r['ip16'],'time':r['time'],'change_summary':r['change_summary'],'exact_payload_body_match':r['body']==payload['text'],'chars':r['actual_chars'],'after_request':r['time']>request['time']})
    out={'request_id':request['id'],'request_time':request['time'],'payload_target':key,'payload_text_chars':len(payload['text']),'target_revisions':rows,'xss_label_revision_count':db.execute("SELECT count(*) FROM revisions WHERE label='XSSChainUser'").fetchone()[0],'limits':['A recorded payload is not proof of execution.','Absent exact body is not proof of failure: capture omissions and transformations are possible.','A later same-prefix save is circumstantial corroboration but does not exclude an ordinary submission.'],'prior_art':['C197: 10-minute Luna report distinguishes temporal corroboration from proof.','C231: 120-minute report compares the payload with later saves and preserves uncertainty.','C304: accepted synthesis makes the distinction explicitly.']}
    (HERE/'results/xss-record-check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'target':key,'revisions':len(rows),'exact_matches':sum(r['exact_payload_body_match']for r in rows),'xss_label_revision_count':out['xss_label_revision_count']}))
if __name__=='__main__':main()
