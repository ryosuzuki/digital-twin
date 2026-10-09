import json,pathlib,numpy as np
from PIL import Image
root=pathlib.Path(__file__).resolve().parents[1]
s=json.loads((root/'sessions/quest-215403/session.json').read_text());d=json.loads((root/'private/object-memory-detections.json').read_text());k=s['intrinsics']; cache={}
for idx,o in enumerate(d['observations']):
 i=o['frame'];f=s['frames'][i]
 if i not in cache: cache[i]=np.asarray(Image.open('/path/to/local-assets'%i)).astype(float)
 im=cache[i];x1,y1,x2,y2=o['box'];u=(x1+x2)/2;v=(y1+y2)/2;dx=int(u/4);dy=int(v/4);patch=im[max(0,dy-2):min(320,dy+3),max(0,dx-2):min(320,dx+3)];valid=patch[:,:,2]>0;depth=(patch[:,:,0]*256+patch[:,:,1])[valid]/1000;depth=depth[(depth>.2)&(depth<8)]
 o['id']='obs-%04d'%idx
 if len(depth)<5: o['position']=None;continue
 z=float(np.median(depth));vec=np.array([(u-k['cx'])/k['fx']*z,-(v-k['cy'])/k['fy']*z,-z]);q=np.array(f['quaternion']);xyz=vec+2*np.cross(q[:3],np.cross(q[:3],vec)+q[3]*vec)+np.array(f['position']);o['position']=xyz.tolist();o['depthMeters']=z;o['depthSpreadMeters']=float(np.percentile(depth,90)-np.percentile(depth,10))
d['spatialMethod']='Median registered axial depth in 5x5 neighborhood at detection-box center; inverse calibrated projection and recorded Three.js camera quaternion. Approximate surface point, not object center or 3D box. No cross-frame identity association.'
(root/'private/object-memory-spatial.json').write_text(json.dumps(d))
print('Valid',sum(bool(o['position']) for o in d['observations']),'of',len(d['observations']))
print(sorted(set(o['label'] for o in d['observations'] if o['position'])))
