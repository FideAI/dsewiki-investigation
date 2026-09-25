"""Reproduce temporal request/save correlation; correlation does not prove script execution."""
import json,sqlite3
from pathlib import Path
HERE=Path(__file__).resolve().parent;CACHE=HERE.parents[2]/'.local/wiki-containment-20260915'
def main():
    db=sqlite3.connect(CACHE/'record-query.sqlite3');db.row_factory=sqlite3.Row
    query="""SELECT r.id revision_id,r.time revision_time,r.page_key,r.label,r.ip16,e.id request_id,e.time request_time,json_extract(e.json,'$.request_action') request_action,cast(strftime('%s',r.time) AS integer)-cast(strftime('%s',e.time) AS integer) delta_seconds FROM revisions r JOIN events e ON e.kind='request' AND e.ip16=r.ip16 AND cast(strftime('%s',r.time) AS integer)-cast(strftime('%s',e.time) AS integer) BETWEEN 0 AND 1 WHERE r.label='AgentDataHelperX' AND r.ip16='52.87' ORDER BY r.time,e.time"""
    rows=[dict(r)for r in db.execute(query)];total=db.execute("SELECT count(*) FROM revisions WHERE label='AgentDataHelperX' AND ip16='52.87'").fetchone()[0]
    result={'sql':query,'total_selected_revisions':total,'matched_revision_count':len({r['revision_id']for r in rows}),'rows':rows,'interpretation':'All selected edits have a same-prefix request zero or one second earlier. This strengthens a qualified script-mediated-writing inference but does not identify the full later payload or browser execution path. Prefixes are not authenticated client identities.','prior_art':['C240: primary120-minuteAstrarep1','C035: exploratoryAstrafollowup','C284: primary30-minuteGeminiFlashrep3','C287: primary30-minuteMuserep3']}
    (HERE/'results/request-save-pairs.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'total_selected_revisions':total,'matched_revision_count':result['matched_revision_count'],'rows':len(rows),'actions':sorted({r['request_action']for r in rows})}))
if __name__=='__main__':main()
