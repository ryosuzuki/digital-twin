import pathlib,json,hashlib
root=pathlib.Path(__file__).resolve().parents[1]
n=0
for m in root.rglob('CATEGORY-SNAPSHOT.json'):
 data=json.loads(m.read_text())
 for f in data['files']:
  p=m.parent/f['path']
  assert p.is_file(),str(p)
  assert hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'],str(p)
  n+=1
print('PASS source hashes:',n)
