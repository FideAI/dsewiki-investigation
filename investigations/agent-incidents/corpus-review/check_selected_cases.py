"""Reproduce consequential examples used in the expanded paper, read-only."""
import json,sqlite3,datetime
from pathlib import Path
HERE=Path(__file__).resolve().parent
DB=HERE.parents[2]/'.local/wiki-containment-20260915/record-query.sqlite3'
QUERIES={
 'delete_targets_are_pages':("SELECT id,page_key,time FROM events WHERE id='delete:dse:rclog:131972'",[['delete:dse:rclog:131972','dse~TestFoobaAgent','2026-06-04T10:53:40Z']]),
 'moderator_writes':("SELECT count(*),sum(length(body)=0),sum(length(body)>0) FROM revisions WHERE label='MartinHuber'",[[26,2,24]]),
 'after_first_delete':("SELECT count(*),count(DISTINCT r.page_key) FROM revisions r JOIN (SELECT page_key,min(time) AS first_delete FROM events WHERE kind='delete' GROUP BY page_key)d USING(page_key) WHERE r.time>d.first_delete",[[420,48]]),
 'after_last_delete':("SELECT count(*) FROM revisions r JOIN (SELECT page_key,max(time) AS final_delete FROM events WHERE kind='delete' GROUP BY page_key)d USING(page_key) WHERE r.time>d.final_delete",[[0]]),
 'delete_events_with_later_write':("SELECT count(*) FROM events e WHERE kind='delete' AND EXISTS(SELECT 1 FROM revisions r WHERE r.page_key=e.page_key AND r.time>e.time)",[[66]]),
 'repeated_delete_keys':("SELECT count(*) FROM (SELECT page_key FROM events WHERE kind='delete' GROUP BY page_key HAVING count(*)>1)",[[55]]),
 'archived_summary_coverage':("SELECT p.wiki,count(*),sum(EXISTS(SELECT 1 FROM events e WHERE e.kind='delete' AND e.page_key=p.page_key)),sum(NOT EXISTS(SELECT 1 FROM events e WHERE e.kind='delete' AND e.page_key=p.page_key)) FROM pages p GROUP BY p.wiki ORDER BY p.wiki",[['dorfwiki',2,0,2],['dse',3908,3898,10],['fractal',68,0,68],['probier',601,0,601]]),
 'welcome_sizes':("SELECT count(*),sum(actual_chars),max(actual_chars),max(utf8_bytes) FROM revisions WHERE page_key='dse~WillkommenImWiki'",None),
 'welcome_final_save':("SELECT id,time,label,actual_chars FROM revisions WHERE page_key='dse~WillkommenImWiki' ORDER BY time DESC LIMIT 1",None),
 'oecd_deletes_and_next_save':("SELECT e.id,e.time,min(r.time) FROM events e LEFT JOIN revisions r ON r.page_key=e.page_key AND r.time>e.time WHERE e.kind='delete' AND e.page_key='dse~OECDEducationEquitySequence' GROUP BY e.id ORDER BY e.time",None),
 'cleanup_adaptation':("SELECT id,time FROM revisions WHERE id IN ('dse~DataUSAConstructionWageSep18Live@16','dse~ZZZDataUSAConstructionWageLive@1') ORDER BY time",None),
 'counter_false_positive_retracted':("SELECT id,time FROM revisions WHERE id IN ('dse~DataUSALanguageR5LiveDec29@2','dse~DataUSALanguageR5LiveDec29@5') ORDER BY time",[['dse~DataUSALanguageR5LiveDec29@2','2026-06-17T00:01:03Z'],['dse~DataUSALanguageR5LiveDec29@5','2026-06-17T00:03:23Z']])
}
def main():
 db=sqlite3.connect(f'file:{DB}?mode=ro',uri=True);out={}
 for name,(sql,expected)in QUERIES.items():
  rows=[list(x)for x in db.execute(sql)]
  if expected is not None:assert rows==expected,(name,rows)
  out[name]=dict(sql=sql,rows=rows,expected=expected,matched_expected=rows==expected if expected is not None else None)
 assert len(out['oecd_deletes_and_next_save']['rows'])==8 and out['oecd_deletes_and_next_save']['rows'][-1][-1] is None
 assert out['welcome_sizes']['rows'][0][0]==2327 and out['welcome_sizes']['rows'][0][2]==24139
 (HERE/'results/selected-record-checks.json').write_text(json.dumps(out,indent=2)+'\n')
 print(f'{len(out)} selected-case queries reproduced; explicit expectations passed.')
if __name__=='__main__':main()
