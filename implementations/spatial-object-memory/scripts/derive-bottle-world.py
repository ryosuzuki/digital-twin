"""Offline, reviewed green-bottle track + recorded depth + calibrated sensor pose.
Private input paths are explicit; output is derived local data, never source Git.
"""
import json, argparse
from pathlib import Path
import cv2, numpy as np
ap=argparse.ArgumentParser();ap.add_argument('--editor',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--audit',type=Path,required=True);a=ap.parse_args()
s=json.load(open(a.editor/'sessions/quest-215403/session.json'));k=s['intrinsics'];track=json.load(open(a.audit/'bottle-track.json'));align=json.load(open(a.editor/'private/object-room-alignment.json'))
def rot(q):
 x,y,z,w=q
 return np.array([[1-2*y*y-2*z*z,2*x*y-2*z*w,2*x*z+2*y*w],[2*x*y+2*z*w,1-2*x*x-2*z*z,2*y*z-2*x*w],[2*x*z-2*y*w,2*y*z+2*x*w,1-2*x*x-2*y*y]])
rows=[];rejected=[]
for o in track['frames']:
 i=o['frameIndex'];mask=cv2.resize(cv2.imread(str(a.audit/o['mask']),0),(320,320),interpolation=cv2.INTER_NEAREST)>0
 d=np.fromfile(a.audit/f'registered-depth/{i:06d}.bin',dtype='<u2').reshape(320,320)/1000
 # Reviewed held bottle is within arm's reach. Reject background depths; no range substitution.
 good=mask&(d>.15)&(d<.95);z=d[good]
 if len(z)<8: rejected.append({'frame':i,'reason':'insufficient foreground depth'});continue
 depth=float(np.percentile(z,25));u,v=o['centroid'];f=s['frames'][i]
 world=rot(f['quaternion'])@np.array([(u-k['cx'])/k['fx']*depth,-(v-k['cy'])/k['fy']*depth,-depth])+f['position']
 scan=np.array(align['rotation'])@world+align['translation']
 rows.append(dict(id='green-bottle-1',frame=i,t=o['timeSeconds'],box=[o['bbox'][0],o['bbox'][1],o['bbox'][0]+o['bbox'][2],o['bbox'][1]+o['bbox'][3]],position=world.tolist(),scanPosition=scan.tolist(),depth=depth,depthSamples=len(z)))
out={'method':'Reviewed HSV green-pixel association within 63.78–67.60 s; masked recorded depth 25th percentile; calibrated camera pose; approximate scan registration. Single interval identity, not general re-identification. No authored range.','limits':'Surface point, not object center or 6DoF. Depth ~5 Hz and RGB ~9.6 Hz; short invalid gaps interpolated for display. Last valid observation persists, not confirmed current location.','samples':rows,'rejected':rejected,'endpointDisplacementMeters':float(np.linalg.norm(np.array(rows[-1]['position'])-rows[0]['position']))}
json.dump(out,open(a.editor/'private/bottle-world-track.json','w'),indent=2);print(json.dumps({k:v for k,v in out.items() if k!='samples'},indent=2))
