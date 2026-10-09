"""Offline local object detections; recorded depth backprojection is performed by viewer."""
import json, pathlib, hashlib
from ultralytics import YOLO
root=pathlib.Path(__file__).resolve().parents[1]
s=json.loads((root/'sessions/quest-215403/session.json').read_text())
assert s['name']=='20261002_215403' and not s['synthetic']
model=YOLO('/tmp/openclaw/quest-object-yolo/yolo11n.pt')
observations=[]
for i,f in enumerate(s['frames']):
    if i%10: continue
    result=model.predict(str(root/'sessions/quest-215403'/f['image']),device='cpu',conf=.38,imgsz=960,verbose=False)[0]
    for b in result.boxes:
        cls=int(b.cls.item()); label=result.names[cls]
        if label=='person': continue
        observations.append(dict(frame=i,t=f['t'],label=label,confidence=round(b.conf.item(),4),box=[round(x,2) for x in b.xyxy[0].tolist()]))
    print('frame',i,'observations',len(observations),flush=True)
output={'capture':s['name'],'model':'YOLO11n COCO pretrained','method':'Local CPU inference on every tenth recorded RGB frame; no manual labels. Class observations, not persistent instance identities.','observations':observations}
(root/'private/object-memory-detections.json').write_text(json.dumps(output))
print('DONE',len(observations))
