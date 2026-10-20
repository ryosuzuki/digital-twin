import pathlib,json,hashlib
root=pathlib.Path(__file__).resolve().parents[1]
n=0
for m in root.rglob('CATEGORY-SNAPSHOT.json'):
 data=json.loads(m.read_text())
 for f in data['files']:
  p=m.parent/f['path']
  assert p.is_file(),str(p)
  expected = f.get('englishDerivative', {}).get('sha256', f['sha256'])
  assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,str(p)
  if 'englishDerivative' in f:
   assert len(f['sha256']) == 64 and f['englishDerivative']['reason'],str(p)
  n+=1
print('PASS original source or explicitly recorded English-derivative hashes:',n)
