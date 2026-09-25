"""Refresh checksums only after reviewing intentional release changes."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.rglob('*')) if p.is_file() and not any(s in {'.git','.local','__pycache__'} for s in p.relative_to(ROOT).parts) and p.name not in {'release-manifest.json','.DS_Store'} and p.suffix!='.pyc'}
(ROOT/'release-manifest.json').write_text(json.dumps({'release':'0.1.0','date':'2026-09-25','review_status':'assistant-coded; independent human adjudication pending','files':files},indent=2)+'\n')
