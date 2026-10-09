import json,pathlib,numpy as np,cv2
from PIL import Image
from ultralytics import YOLO
root=pathlib.Path(__file__).resolve().parents[1];s=json.load(open(root/'sessions/quest-215403/session.json'));d=json.load(open(root/'private/object-memory-spatial.json'));model=YOLO('/tmp/openclaw/quest-object-yolo/yolo11n-seg.pt');ref={}
for label in ['refrigerator','couch','potted plant','dining table','laptop']:
 o=max([o for o in d['observations'] if o['position'] and o['label']==label],key=lambda o:o['confidence']);f=s['frames'][o['frame']];r=model.predict(str(root/'sessions/quest-215403'/f['image']),device='cpu',imgsz=960,conf=.25,verbose=False)[0]
 candidates=[]
 for j,b in enumerate(r.boxes):
  if r.names[int(b.cls.item())]!=label:continue
  bb=b.xyxy[0].cpu().numpy();aa=np.array(o['box']);inter=np.maximum(0,np.minimum(bb[2:],aa[2:])-np.maximum(bb[:2],aa[:2])).prod();iou=inter/((bb[2:]-bb[:2]).prod()+(aa[2:]-aa[:2]).prod()-inter);candidates.append((iou,j))
 if not candidates or max(candidates)[0]<.3:continue
 iou,j=max(candidates);mask=cv2.resize(r.masks.data[j].cpu().numpy(),(320,320),interpolation=cv2.INTER_NEAREST)>.5;mask=cv2.erode(mask.astype(np.uint8),np.ones((3,3),np.uint8))>0
 raw=np.asarray(Image.open('/path/to/local-assets'%o['frame'])).astype(float);dep=(raw[:,:,0]*256+raw[:,:,1])/1000;ys,xs=np.where(mask&(raw[:,:,2]>0)&(dep>.2)&(dep<8));z=dep[ys,xs];k=s['intrinsics'];points=np.stack([((xs+.5)*4-k['cx'])/k['fx']*z,-((ys+.5)*4-k['cy'])/k['fy']*z,-z],axis=1);med=np.median(points,axis=0);idx=np.argmin(np.linalg.norm(points-med,axis=1));v=points[idx];q=np.array(f['quaternion']);world=v+2*np.cross(q[:3],np.cross(q[:3],v)+q[3]*v)+np.array(f['position']);ref[o['id']]={'position':world.tolist(),'sourcePixel':[(float(xs[idx])+.5)*4,(float(ys[idx])+.5)*4],'method':'YOLO11n-seg mask erosion; valid-depth medoid nearest coordinatewise median in camera space','validPixels':len(z),'segmentationBoxIoU':float(iou),'label':label};print(label,ref[o['id']],flush=True)
(root/'private/object-room-refinements.json').write_text(json.dumps(ref,indent=2))
