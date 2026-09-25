"""Build the public, read-only catalog without source caches or private decisions."""
import importlib.util,json
from pathlib import Path
from urllib.parse import quote
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('review_desk', ROOT/'tools/claim-review/server.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
items,reviews,inventory,resources=mod.load_catalog()
for item in items.values():
    item.pop('snapshot',None);item.pop('fingerprint',None)
    public_rationales={
      'P01':'Better scores measure reconstruction of reference findings. They do not establish correction of each earlier claim. We compared the score changes with mapped claim transitions.',
      'P02':'The denominator is the 61 verified follow-ups whose published finding score increased. Retained problems include factual contradictions and claims judged insufficiently supported. The narrower count excludes disputed parent, follow-up and transition judgments.',
      'P03':'A correction repairs a prior claim; a qualification narrows it to the evidence. Merely omitting a claim is not counted as correction. The expansion instructions are an important limit on interpretation.',
      'P04':'The same report can contain supported analysis and a flagged conclusion. Counts are reports with at least one scoped example, not a rate over all sentences.',
      'P05':'Completeness applies to the pinned staged publication collection. Rejected attempts and secondary experiments remain separate from the primary comparison.',
      'P06':'The examples show why the specific claim behind a proposed security action needs evidence. Testing whether an explicit verification requirement improves decisions is future work.'
    }
    if item['id'] in public_rationales:item['rationale']=public_rationales[item['id']]
    for source in item['sources']:
        url=inventory[source['report']]['source_url'].replace('raw.githubusercontent.com/hamzah2304/messageboardauditbench/','github.com/hamzah2304/messageboardauditbench/blob/')
        lines=source['lines'];source['url']=url+(f'#L{min(lines)}-L{max(lines)}' if lines else '')
    item['evidence']=[{'reference':r,'url':'https://github.com/FideAI/dsewiki-investigation/blob/main/'+quote(str(resources[r].relative_to(ROOT)),safe='/') if r in resources else None} for r in item.pop('references')]
(ROOT/'explorer/data.json').write_text(json.dumps({'pin':mod.PIN,'items':list(items.values())},ensure_ascii=False,separators=(',',':'))+'\n')
print(f'Built public explorer: {len(items)} items; no reviewer decisions or source bodies.')
