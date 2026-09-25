"""Read JSON metadata from hash-checked tar/zip run archives, without executing logs."""
import hashlib,io,json,tarfile,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;CACHE=HERE.parents[2]/'.local/wiki-containment-20260915'
def main():
    manifest=json.loads((HERE/'results/log-archive-manifest.json').read_text());expected={x['path']:x for x in manifest['logs']};result=[]
    for archive in sorted((CACHE/'log-archives').glob('*.tar')):
        with tarfile.open(archive)as t:
            for m in t.getmembers():
                if not m.isfile() or not m.name.endswith('.eval'):continue
                raw=t.extractfile(m).read();sha=hashlib.sha256(raw).hexdigest();assert sha==expected[m.name]['sha256']
                with zipfile.ZipFile(io.BytesIO(raw))as z:
                    for name in z.namelist():
                        if not(name.startswith('samples/')and name.endswith('.json')):continue
                        s=json.loads(z.read(name));md=s.get('metadata',{});out=s.get('output',{}).get('completion','')
                        if not isinstance(out,str):out=''
                        result.append({'archive':archive.name,'log_path':m.name,'log_basename':Path(m.name).name,'log_sha256':sha,'sample_member':name,'sample_json_sha256':hashlib.sha256(z.read(name)).hexdigest(),'sample_id':s['id'],'epoch':s['epoch'],'run_id':md.get('run_id'),'thread_id':md.get('cli_codex_thread_id'),'output_sha256':hashlib.sha256(out.encode()).hexdigest(),'output_normalized_sha256':hashlib.sha256((out.strip()+'\n').encode()).hexdigest(),'output_words':len(out.split()),'input_sha256':hashlib.sha256(str(s.get('input','')).encode()).hexdigest(),'data_variant':md.get('data_variant'),'preflight_files':md.get('sandbox_preflight',{}).get('files',{}),'has_scores':bool(s.get('scores')),'partial_error':bool(s.get('error')),'model_served':md.get('model_served'),'parent_log':md.get('parent_log'),'parent_epoch':md.get('parent_epoch'),'parent_run_id':md.get('parent_run_id'),'record_note':'Parsed metadata and output hashes; not a full behavioral reading of the run transcript.'})
    (HERE/'results/archive-samples.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'archives':len({r['archive']for r in result}),'logs':len({r['log_path']for r in result}),'samples':len(result),'samples_with_preflight_hashes':sum(bool(r['preflight_files'])for r in result)},indent=2))
if __name__=='__main__':main()
