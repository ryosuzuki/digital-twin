"""Conservative RGB-D point cloud fusion. Does not claim new sensor resolution."""
import json,time,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.spatial import cKDTree
SRC=Path('/path/to/local-assets')
OUT=Path('/path/to/local-assets');OUT.mkdir(parents=True,exist_ok=True)
START=time.time()
files=sorted(SRC.glob('frame_*.jpg'))
def load(f,stride=3,scale=.001,sign=(1,-1,-1),offset=(0,0,0)):
 n=f.stem.split('_')[1];meta=json.loads(f.with_suffix('.json').read_text());K=np.array(meta['intrinsics']).reshape(3,3);T=np.array(meta['cameraPoseARFrame']).reshape(4,4)
 d=np.array(Image.open(SRC/f'depth_{n}.png'))[::stride,::stride]*scale;c=np.array(Image.open(SRC/f'conf_{n}.png'))[::stride,::stride]
 v,u=np.mgrid[0:192:stride,0:256:stride]; x=(u*7.5-K[0,2])/K[0,0]*d;y=(v*7.5-K[1,2])/K[1,1]*d
 p=np.stack([x,y,d],-1)*sign;p=p@T[:3,:3].T+T[:3,3]+offset
 rgb=np.array(Image.open(f).resize((256,192),Image.Resampling.BILINEAR))[::stride,::stride]
 mask=(c==2)&(d>.2)&(d<8)&np.isfinite(p).all(-1)
 return p[mask],rgb[mask],meta
mesh=np.array([[float(x) for x in l.split()[1:4]] for l in (SRC/'export.obj').open() if l.startswith('v ')],dtype=np.float32)
tree=cKDTree(mesh);checks=[]
for scale in [.001,.01,1.]:
 for sign in [(1,-1,-1),(1,1,1)]:
  for offset in [(0,0,0),(.30967346,.68,1.306515),(-.30967346,-.68,-1.306515)]:
   ds=[]
   for f in files[::110]:
    p,_,_=load(f,12,scale,sign,offset)
    if len(p): ds.extend(tree.query(p)[0].tolist())
   if ds: checks.append({'scale':scale,'sign':sign,'offset':offset,'median_nearest_mesh_vertex_m':float(np.median(ds)),'p90_m':float(np.percentile(ds,90))})
checks.sort(key=lambda x:x['median_nearest_mesh_vertex_m']);best=checks[0];print('convention',best,flush=True)
# Do not silently produce a false aligned reconstruction.
if best['median_nearest_mesh_vertex_m']>.15: raise RuntimeError('Convention cannot be validated below 15cm median')
# Reserve frame groups; nearest neighboring RGB frames also excluded from fusion.
held_indices=list(range(20,len(files)-2,60));blocked={j for i in held_indices for j in range(i-2,i+3)}
ps=[];cs=[];training=[]
for i,f in enumerate(files):
 if i in blocked or i%2: continue
 p,c,_=load(f,3,best['scale'],best['sign'],best['offset']);ps.append(p);cs.append(c);training.append(f.name)
p=np.concatenate(ps);c=np.concatenate(cs).astype(float);print('training points',len(p),flush=True)
held=np.concatenate([load(files[i],4,best['scale'],best['sign'],best['offset'])[0] for i in held_indices]);results=[]
def metrics(points):
 d=cKDTree(points).query(held)[0]
 return {'heldout_points':len(d),'median_nearest_distance_m':float(np.median(d)),'p90_m':float(np.percentile(d,90)),'within_3cm_fraction':float(np.mean(d<.03))}
results.append({'label':'original_export_mesh_vertices','points':len(mesh),**metrics(mesh),'warning':'Original mesh used all frames; not an equal held-out-training baseline.'})
clouds=[]
for voxel in [.02,.01]:
 q=np.floor(p/voxel).astype(np.int32);_,inv,counts=np.unique(q,axis=0,return_inverse=True,return_counts=True);N=len(counts)
 pp=np.column_stack([np.bincount(inv,weights=p[:,j])/counts for j in range(3)]).astype('<f4');cc=np.column_stack([np.bincount(inv,weights=c[:,j])/counts for j in range(3)]).clip(0,255).astype('u1')
 name=f'confidence-fused-{int(voxel*1000)}mm.ply';out=OUT/name
 ar=np.empty(N,dtype=[('x','<f4'),('y','<f4'),('z','<f4'),('red','u1'),('green','u1'),('blue','u1')])
 for j,key in enumerate(['x','y','z']):ar[key]=pp[:,j]
 for j,key in enumerate(['red','green','blue']):ar[key]=cc[:,j]
 header='ply\nformat binary_little_endian 1.0\ncomment RGB-D fusion experiment; not upgraded texture\nelement vertex '+str(N)+'\nproperty float x\nproperty float y\nproperty float z\nproperty uchar red\nproperty uchar green\nproperty uchar blue\nend_header\n'
 with out.open('wb') as fh:fh.write(header.encode());fh.write(ar.tobytes())
 row={'label':name,'voxel_m':voxel,'points':N,**metrics(pp),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()};results.append(row);clouds.append((pp,cc,row));print(row,flush=True)
# Matched oblique orthographic evidence views; do not depict as a textured mesh.
canvas=Image.new('RGB',(1800,1020),(18,22,29));draw=ImageDraw.Draw(canvas)
for panel,(pp,cc,row) in enumerate(clouds):
 # Camera looking down and across room; common fixed projection.
 xx=pp[:,0]+.35*pp[:,2];yy=.65*pp[:,2]-.75*pp[:,1]
 xy=np.column_stack([xx,yy]);lo=np.array([-8.,-6.]);hi=np.array([7.,7.]);uv=((xy-lo)/(hi-lo)*np.array([850,900])).astype(int);uv[:,0]+=panel*900+20;uv[:,1]+=80
 valid=(uv[:,0]>=panel*900+20)&(uv[:,0]<panel*900+870)&(uv[:,1]>=80)&(uv[:,1]<980)
 pixels=canvas.load()
 order=np.argsort(pp[:,1]+.7*pp[:,2])
 for k in order[valid[order]]:pixels[int(uv[k,0]),int(uv[k,1])]=tuple(cc[k])
 draw.text((panel*900+25,25),f"{row['label']} | {row['points']:,} points",fill='white')
 draw.text((panel*900+25,45),f"Held-out median: {row['median_nearest_distance_m']*1000:.1f} mm (agreement, not ground truth)",fill='white')
canvas.save(OUT/'fusion-comparison.png')
report={'source':str(SRC),'source_not_modified':True,'method':'Confidence=2; depth 0.2–8 m; every second RGB keyframe; stride3 depth; voxel centroid/color mean. No TSDF, meshing, pose optimization, or learned detail.','convention_candidates':checks,'selected_convention':best,'training_frames':training,'heldout_frames':[files[i].name for i in held_indices],'neighbor_exclusion_rgb_frames':2,'raw_training_points':len(p),'results':results,'runtime_seconds':time.time()-START,'limitations':['Agreement against other noisy source depth is not ground truth accuracy.','Original mesh saw all observations and is not a fair held-out reconstruction competitor.','RGB resized to depth resolution for point colors; this is not improved visual texture.','1cm voxel does not imply 1cm true resolution.','Existing 10K textured OBJ and Scaniverse splat remain realism baselines.']}
(OUT/'comparison-metrics.json').write_text(json.dumps(report,indent=2))
print('DONE',time.time()-START,flush=True)
