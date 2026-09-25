"""Reproduce saved read-only SQLite checks against the reconstructed archive."""
import json,sqlite3
from pathlib import Path
HERE=Path(__file__).resolve().parent
DB=HERE.parents[2]/'.local/wiki-containment-20260915/record-query.sqlite3'

def main():
    db=sqlite3.connect(f'file:{DB}?mode=ro',uri=True)
    checked=[]
    for filename in ['write-rate-check.json','synthesis-record-check.json']:
        checks=json.loads((HERE/'results'/filename).read_text())
        for name,check in checks.items():
            if name=='counter_evidence':continue  # Full body excerpts remain private; dated references are reproduced separately.
            assert check['sql'].lstrip().upper().startswith('SELECT ')
            actual=[list(row)for row in db.execute(check['sql'])]
            assert actual==check['rows'],(filename,name,actual)
            checked.append(dict(file=filename,check=name,rows=len(actual),matched=True))
    (HERE/'results/record-query-replay.json').write_text(json.dumps(checked,indent=2)+'\n')
    print(f'{len(checked)} saved record queries reproduced exactly.')
if __name__=='__main__':main()
