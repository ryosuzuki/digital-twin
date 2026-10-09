import json,numpy as np
from scipy.spatial import cKDTree
from pathlib import Path
root=Path(__file__).resolve().parents[1];r=json.load(open(root/'sessions/quest-215403/room-geometry.json'))
a=np.array(next(p['vertices'] for p in r['parts'] if p['label']=='GLOBAL_MESH')).reshape(-1,3)
b=np.array([[float(v) for v in l.split()[1:4]] for l in open('/path/to/local-assets') if l.startswith('v ')])
print('bounds',a.min(0),a.max(0),b.min(0),b.max(0),flush=True)
def voxel(p,step):return p[np.unique(np.floor(p/step).astype(int),axis=0,return_index=True)[1]]
a=voxel(a,.12);b=voxel(b,.10);tree=cKDTree(b);best=None
for angle in np.linspace(0,2*np.pi,48,endpoint=False):
 c=np.cos(angle);s=np.sin(angle);rot=np.array([[c,0,s],[0,1,0],[-s,0,c]]);t=np.median(b,axis=0)-np.median(a@rot.T,axis=0)
 for it in range(55):
  p=a@rot.T+t;dist,inds=tree.query(p);mask=dist<np.percentile(dist,75);x=p[mask];y=b[inds[mask]];xc=x.mean(0);yc=y.mean(0);u,_,vt=np.linalg.svd((x-xc).T@(y-yc));rr=vt.T@u.T
  if np.linalg.det(rr)<0:vt[-1]*=-1;rr=vt.T@u.T
  tt=yc-rr@xc;rot=rr@rot;t=rr@t+tt
 dist,_=tree.query(a@rot.T+t);score=np.mean(np.sort(dist)[:int(len(dist)*.8)])
 if best is None or score<best[0]:best=(score,rot,t,dist);print('best',angle,score,flush=True)
score,rot,t,dist=best
out={'method':'Multi-start trimmed point-to-point ICP of Quest first GLOBAL_MESH to October 8 textured scan; approximate and not ground truth','rotation':rot.tolist(),'translation':t.tolist(),'scale':1,'meanTrimmedDistanceMeters':float(score),'medianNearestSurfaceMeters':float(np.median(dist)),'p90NearestSurfaceMeters':float(np.percentile(dist,90)),'questPoints':len(a),'scanPoints':len(b)}
(root/'private/object-room-alignment.json').write_text(json.dumps(out,indent=2));print(out)
