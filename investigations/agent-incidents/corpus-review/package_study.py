"""Prepare a local publication package from complete results; no deployment."""
import argparse,csv,hashlib,json,re,shutil,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent

def view_url(url):return url.replace('raw.githubusercontent.com/hamzah2304/messageboardauditbench/','github.com/hamzah2304/messageboardauditbench/blob/')

def main(destination):
 analysis=json.loads((HERE/'results/study/analysis.json').read_text());assert analysis['complete']
 coverage={r['artifact_id']:r for r in csv.DictReader((HERE/'results/study/coverage.csv').open())}
 meta={r['artifact_id']:r for r in csv.DictReader((HERE/'results/report-inventory.csv').open())}
 reviews=json.loads((HERE/'results/study/review-records.json').read_text())
 reports=[]
 for d in reviews:
  m=meta[d['artifact_id']];source=view_url(m['source_url'])
  if m['artifact_type']=='rejected_attempt':label='Rejected synthesis: '+Path(m['path']).stem.replace('_',' ')
  elif m['group']=='synthesis':label='Accepted synthesis · '+m['model_requested']
  else:
   budget=m['parent_budget_min'] or m['budget_min'];budget_label=('parent '+budget+' min')if m['parent_budget_min'] else budget+' min'
   label=f"{m['model_requested']} · {m['agent']} · {budget_label} · replicate {m['replicate']}"
   if m['model_fallback']not in ('','null'):label+=' · recorded fallback'
   if m['partial']=='True':label+=' · partial artifact'
   if m['prompt_id']=='66b7fb24'and m['group']=='main':label+=' · alternate attempt'
  claims=[dict(id=f"{d['review_id']}-{i:02d}",family=c['family'],judgment=c['judgment'],disputable=c['disputable'],claim=c['claim'],rationale=c['rationale'],sourceUrl=source+'#L'+str(min(c['lines'])),evidence=c['evidence'])for i,c in enumerate(d['claims'],1)]
  reports.append(dict(id=d['review_id'],label=label,group=m['group'],sourceUrl=source,summary=d['report_summary'],words=int(m['words']),claims=claims))
 destination.mkdir(parents=True,exist_ok=True)
 (destination/'corpus-explorer.json').write_text(json.dumps(dict(complete=True,reports=reports),ensure_ascii=False,separators=(',',':'))+'\n')
 loose={
  'paper.md':'corpus-paper.md','CODEBOOK.md':'corpus-codebook.md','PAIR_CODEBOOK.md':'corpus-pair-codebook.md','RECONCILIATION.md':'corpus-reconciliation.md',
  'results/report-inventory.csv':'corpus-report-inventory.csv','results/study/coverage.csv':'corpus-reading-coverage.csv',
  'results/study/claims.csv':'corpus-claims.csv','results/study/assessments.csv':'corpus-assessments.csv',
  'results/study/claim-transitions.csv':'claim-transitions.csv','results/study/paired-outcomes.csv':'corpus-paired-outcomes.csv',
  'results/study/analysis.json':'corpus-analysis.json','results/followup-pairs.csv':'corpus-published-pairs.csv',
  'results/followup-pairs-corrected.csv':'corpus-corrected-pairs.csv','results/followup-pair-repairs.csv':'corpus-pair-repairs.csv',
  'results/run-provenance-check.json':'corpus-run-provenance.json','results/followup-prompt-check.json':'corpus-followup-prompt.json','results/review-reference-check.json':'corpus-reference-check.json','results/selected-grade-audit.json':'corpus-selected-grade-audit.json',
  'results/selected-record-checks.json':'corpus-record-checks.json','results/request-save-pairs.json':'corpus-request-save-pairs.json',
  'results/contested-record-checks.json':'corpus-contested-record-checks.json',
  'results/contested-judgment-changes.json':'corpus-judgment-changes.json',
 }
 for source,target in loose.items():shutil.copyfile(HERE/source,destination/target)
 landing='''# DSEWiki: full-corpus study and evidence

Fide AI's complete staged-publication review: 297 indexed reports and seven rejected synthesis attempts, 303 distinct texts, 1,006,136 staged words. The primary comparison covers113reports and78continued investigations. One published parent mapping was repaired;79manual comparisons retain the original diagnostic link.

Full-text assistant assessment of eight questions. Independent human adjudication remains pending. These are descriptive, dependent observations from one incident benchmark, not a model ranking, certification or general error rate.

- [Read the methods paper](corpus-paper.md).
- [Download the reproducibility package](corpus-study.zip), including original analysis, review records and scripts.
- [Inspect the artifact inventory](corpus-report-inventory.csv) and [reading coverage](corpus-reading-coverage.csv).
- [Inspect claim judgments and source passages](corpus-claims.csv), [question assessments](corpus-assessments.csv), and [analysis results](corpus-analysis.json).
- [Inspect all manual claim transitions](claim-transitions.csv) and [corrected continuation outcomes](corpus-paired-outcomes.csv).
- [Compare published parent mappings](corpus-published-pairs.csv) with [corrected mappings](corpus-corrected-pairs.csv) and the [single repair](corpus-pair-repairs.csv).
- [Read the coding rules](corpus-codebook.md), [transition rules](corpus-pair-codebook.md), and [lead reconciliation](corpus-reconciliation.md).
- [Inspect the September 23 judgment changes](corpus-judgment-changes.json) and [independent raw-record and headline checks](corpus-contested-record-checks.json). These are internal assistant checks, not human adjudication.
- [Check selected record calculations](corpus-record-checks.json), [request/save correspondences](corpus-request-save-pairs.json), [run provenance](corpus-run-provenance.json), and [selected published grader rationales](corpus-selected-grade-audit.json).
- [Verify package checksums](corpus-package-manifest.json).

## Reproduce and challenge

Unpack the zip into a new workspace and follow its README. It preserves the expected `investigations/agent-incidents/corpus-review/` layout. Python3.11or later is required; the analysis uses the standard library. Acquiring public source reports and run archives requires internet access and approximately550MBfor the run archives. No model inference is invoked.

The scripts reproduce counts, joins, hashes and aggregation. They do not turn an assistant judgment into an independently verified fact. Each claim includes its source location, evidence and rationale so a reviewer can challenge the interpretation. Omitted topics are not counted as successes. A report with no scoped flag is not certified as wholly correct.

Source reports and incident data remain at their upstream locations. The package does not redistribute the full third-party corpus, raw run transcripts or executable incident payloads. Benchmark preparation uses synthetic names and selected records; derived counts describe that extract. Full source hashes and acquisition URLs are included for readers who obtain the sources themselves.

The website article is the narrative companion. This package adds methods and traceability; it has not been independently human-adjudicated or externally peer reviewed.
'''.replace('covers113reports and78continued','covers 113 reports and 78 continued').replace('link.\n','link.\n').replace(';79manual','; 79 manual').replace('Python3.11or','Python 3.11 or').replace('approximately550MBfor','approximately 550 MB for')
 (destination/'corpus-study.md').write_text(landing)
 # Allowlist original Fide analysis, derived metadata and source acquisition code.
 # Exclude raw reports, full grader quotations, incident bodies and run transcripts.
 included=[]
 for pattern in ['*.py','README.md','CODEBOOK.md','PAIR_CODEBOOK.md','RECONCILIATION.md','paper.md','paper-template.md','insights-template.mdx','newsletter-template.md','reviews/C*.json','pairs/*.json','pairs-repaired/*.json','results/*.json','results/*.csv','results/log-archive-SHA256SUMS','results/study/*.csv','results/study/*.json']:
  for path in HERE.glob(pattern):
   if path.name in ['record-anchors.json','synthesis-record-check.json','published-item-grades.csv','corpus-source-manifest.json']:continue
   if path.is_file():included.append(path)
 # The query replay includes hashes/metadata and a body-bearing private check. Ship
 # a public-safe query fixture containing only the numeric/date queries instead.
 fixture=json.loads((HERE/'results/synthesis-record-check.json').read_text());fixture.pop('counter_evidence',None)
 extras={'results/synthesis-record-check.json':json.dumps(fixture,indent=2)+'\n',
  'results/corpus-source-manifest.json':((HERE/'results/corpus-source-manifest.json') if (HERE/'results/corpus-source-manifest.json').exists() else (HERE.parents[2]/'.local/wiki-containment-20260915/corpus-manifest.json')).read_text()}
 archive=destination/'corpus-study.zip'
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  prefix='investigations/agent-incidents/corpus-review/'
  for path in sorted(set(included)):z.write(path,prefix+str(path.relative_to(HERE)))
  for name,content in extras.items():z.writestr(prefix+name,content)
 # Hash only this expanded package's outputs; preserve historical evidence files.
 names=['corpus-explorer.json','corpus-study.md','corpus-study.zip',*loose.values()]
 manifest=dict(scope='Expanded DSEWiki package; original Fide analysis and bounded derived records',files=[dict(path=n,bytes=(destination/n).stat().st_size,sha256=hashlib.sha256((destination/n).read_bytes()).hexdigest())for n in sorted(names)])
 (destination/'corpus-package-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(dict(files=len(names)+1,zip_bytes=archive.stat().st_size,explorer_reports=len(reports)),indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('destination',type=Path);main(p.parse_args().destination)
