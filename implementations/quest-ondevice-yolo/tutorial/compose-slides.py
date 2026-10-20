#!/usr/bin/env python3
"""Recreate the Quest teaching extension on a copy of its course template.

Dry-run by default. Caller owns authentication; no credential handling is included.
Google helper protocol: Google().presentation(id) -> dict; .batch(id, requests).
The original deck already contains these object IDs: do not reapply there.
"""
import argparse
import importlib
import json
import sys
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--presentation-id', required=True)
parser.add_argument('--media-json', type=Path, required=True,
                    help='JSON array [{"id":"IMAGE_DRIVE_ID"},{"id":"VIDEO_DRIVE_ID"}]')
parser.add_argument('--google-helper-dir', type=Path,
                    help='Directory containing caller-provided google_api.py (required with --apply)')
parser.add_argument('--work-dir', type=Path, required=True)
parser.add_argument('--apply', action='store_true', help='Mutate the named presentation; default only writes requests')
args = parser.parse_args()
R = args.work_dir.resolve()
R.mkdir(parents=True, exist_ok=True)
if (R/'manifest.json').exists() or (R/'requests.json').exists():
    parser.error('Use a fresh work directory to preserve prior plans.')
ID = args.presentation_id
M = json.loads(args.media_json.read_text())
if len(M) != 2 or any(not isinstance(row.get('id'),str) or not row['id'] for row in M):
    parser.error('media-json must contain exactly two nonempty Drive IDs, image then video.')
IMG, VID = M[0]['id'], M[1]['id']
REPO = 'https://github.com/ryosuzuki/digital-twin/tree/main/implementations/quest-ondevice-yolo'
SOURCE = REPO + '/unity/QuestYolo.cs'
INK={'red':.13,'green':.16,'blue':.18};TEAL={'red':.12,'green':.38,'blue':.40};ORANGE={'red':.75,'green':.47,'blue':.11};PALE={'red':.91,'green':.96,'blue':.95};GRAY={'red':.92,'green':.93,'blue':.94}
req=[];rows=[];seq=0

def geom(sid,x,y,w,h):return {'pageObjectId':sid,'size':{'width':{'magnitude':w,'unit':'PT'},'height':{'magnitude':h,'unit':'PT'}},'transform':{'scaleX':1,'scaleY':1,'translateX':x,'translateY':y,'unit':'PT'}}
def text(sid,s,x,y,w,h,size=16,bold=False,color=INK,fill=None,link=None,font='Arial'):
 global seq
 seq+=1;i=f'{sid}_e{seq}'
 req.append({'createShape':{'objectId':i,'shapeType':'ROUND_RECTANGLE' if fill else 'TEXT_BOX','elementProperties':geom(sid,x,y,w,h)}})
 props={'outline':{'propertyState':'NOT_RENDERED'},'contentAlignment':'MIDDLE' if fill else 'TOP','shapeBackgroundFill':{'solidFill':{'color':{'rgbColor':fill},'alpha':1}} if fill else {'propertyState':'NOT_RENDERED'}}
 req.append({'updateShapeProperties':{'objectId':i,'shapeProperties':props,'fields':','.join(props)}})
 req.append({'insertText':{'objectId':i,'text':s}})
 style={'fontFamily':font,'fontSize':{'magnitude':size,'unit':'PT'},'bold':bold,'foregroundColor':{'opaqueColor':{'rgbColor':color}}}
 if link:style['link']={'url':link}
 req.append({'updateTextStyle':{'objectId':i,'textRange':{'type':'ALL'},'style':style,'fields':','.join(style)}})
 if fill:req.append({'updateParagraphStyle':{'objectId':i,'textRange':{'type':'ALL'},'style':{'alignment':'CENTER'},'fields':'alignment'}})
 return i

def line(sid,x1,y1,x2,y2,color=TEAL,arrow=False,dash=False):
 global seq
 seq+=1;i=f'{sid}_e{seq}';req.append({'createLine':{'objectId':i,'lineCategory':'STRAIGHT','elementProperties':{'pageObjectId':sid,'size':{'width':{'magnitude':abs(x2-x1) or .01,'unit':'PT'},'height':{'magnitude':abs(y2-y1) or .01,'unit':'PT'}},'transform':{'scaleX':1 if x2>=x1 else -1,'scaleY':1 if y2>=y1 else -1,'translateX':x1,'translateY':y1,'unit':'PT'}}}})
 p={'startArrow':'NONE','endArrow':'NONE','lineFill':{'solidFill':{'color':{'rgbColor':color},'alpha':1}},'weight':{'magnitude':2,'unit':'PT'}}
 if arrow:p['endArrow']='FILL_ARROW'
 if dash:p['dashStyle']='DASH'
 req.append({'updateLineProperties':{'objectId':i,'lineProperties':p,'fields':','.join(p)}})

def slide(key,title,takeaway,notes,section=False):
 sid='quest_lab_'+key;rows.append({'slide_id':sid,'title':title,'takeaway':takeaway,'notes':notes,'number':37+len(rows)+1})
 if section:
  req.append({'createSlide':{'objectId':sid,'slideLayoutReference':{'layoutId':'g78a891b14e_0_404'},'placeholderIdMappings':[{'layoutPlaceholder':{'type':'TITLE'},'objectId':sid+'_title'}]}})
  req.append({'insertText':{'objectId':sid+'_title','text':title}});return sid
 req.append({'duplicateObject':{'objectId':'lecture_slide_002','objectIds':{'lecture_slide_002':sid,'lecture_title_002':sid+'_title','lecture_body_002':sid+'_body','lecture_num_002':sid+'_num'}}})
 for i,s in [(sid+'_title',title),(sid+'_num',str(rows[-1]['number']))]:req.extend([{'deleteText':{'objectId':i,'textRange':{'type':'ALL'}}},{'insertText':{'objectId':i,'text':s}}])
 req.append({'deleteObject':{'objectId':sid+'_body'}})
 text(sid,takeaway,108,101,562,39,16)
 text(sid,'Classroom Local YOLO · native 0.2.0 · source + reproducible setup',108,378,562,16,9,color=TEAL,link=REPO)
 return sid

def photo(sid,x,y,w,h):req.append({'createImage':{'objectId':sid+'_photo','url':'https://drive.google.com/uc?export=view&id='+IMG,'elementProperties':geom(sid,x,y,w,h)}})

s=slide('section','Build it: object-aware AR','', 'Teaching extension: current implementation is local detection + approximate 3D localization. Object-bound menus are the XR-Objects-inspired next layer, not an implemented feature.',True)
s=slide('demo','Recognize objects in first person','Actual Quest 3 capture — no camera-preview panel, no external GPU.','Authentic frame from quest-firstperson-preview-020.mp4, native0.2.0, stationary Quest3. Left-eye compositor crop; not generated. Video source hash is recorded with artifacts.json. Person/chair/laptop labels are model predictions, not ground truth.')
photo(s,115,144,209,224)
text(s,'See the room normally',355,151,300,31,21,True)
text(s,'Passthrough is the background.\nOnly labels and outlines are virtual.',355,191,294,66,18)
text(s,'Current result',355,272,294,26,15,True,color=TEAL)
text(s,'Object detection + approximate\n3D placement from measured depth.',355,299,294,57,17)

s=slide('video','Demo: on-headset inference','15-second real-device recording; the model runs on the headset.','Actual native0.2.0 Quest3 compositor recording. This is stationary-device evidence only. Moving-head alignment and temporal identity tracking are not established. Native Drive video uses same course audience as the deck; fallback link provided.')
req.append({'createVideo':{'objectId':s+'_video','source':'DRIVE','id':VID,'elementProperties':geom(s,118,142,210,225)}})
text(s,'Watch for three things',357,157,290,31,21,True)
text(s,'1  No floating camera screen\n\n2  Boxes over real objects\n\n3  Depth-backed world positions',357,200,295,145,18)
text(s,'Open the original demo ↗',357,347,285,24,13,color=TEAL,link='https://drive.google.com/file/d/'+VID+'/view')

s=slide('xrobjects','From labels to XR-Objects','The goal is an interface attached to a real object — not just a box.','Related work: Augmented Object Intelligence with XR-Objects, Dogan et al., UIST2024, doi10.1145/3654777.3676379, https://xr-objects.github.io/. Original evaluated phone prototype uses ARFoundation/ARCore + on-device MediaPipe object detection and cloud PaLI. Diagram is a conceptual next step for this Quest sample; object menu, selection, LLM and actions are NOT implemented.')
for x,t,b in [(110,'Recognize','“This is a chair”'),(303,'Locate','A 3D surface point'),(496,'Interact','Open an object menu')]:
 text(s,t,x,162,174,45,19,True,fill=PALE);text(s,b,x,216,174,45,15)
line(s,285,184,300,184,arrow=True);line(s,478,184,493,184,arrow=True)
text(s,'IMPLEMENTED IN OUR SAMPLE',112,275,355,22,12,True,color=TEAL)
text(s,'NEXT: SELECT + MENU',496,275,175,22,12,True,color=ORANGE)
text(s,'Ask about it  ·  attach a note  ·  trigger an action',112,315,550,35,20)
text(s,'XR-Objects · UIST 2024 · original system ≠ standalone Quest port',112,353,550,20,10,color=TEAL,link='https://xr-objects.github.io/')

s=slide('levels','Detection is not yet tracking','Each additional capability needs a new representation.','Source: QuestYolo.cs Draw() destroys and recreates annotations each inference; no temporal IDs or persistent anchors. Ladder is a teaching classification, not a measured performance claim. Center ray surface point is not full 3D object center.')
levels=[('2D detection','class + confidence + image rectangle','DONE'),('3D localization','calibrated ray + depth → surface point','DONE / APPROX.'),('Temporal tracking','same object ID across time / motion','NEXT'),('Persistent anchoring','restore object UI after revisiting','NEXT')]
for j,(a,b,c) in enumerate(levels):
 y=148+j*53;text(s,a,110,y,158,44,17,True,fill=PALE if j<2 else GRAY);text(s,b,280,y+3,280,43,15);text(s,c,570,y+5,100,35,11,True,color=TEAL if j<2 else ORANGE)

s=slide('pipeline','How it runs on the headset','Pixels provide semantics; geometry places the result in the room.','Source QuestYolo.cs Start(), Decode(), Draw(). Snapshot resized640x640; YOLOv9 ONNX, class threshold.35 class-aware NMS.45, calibrated exposure-time camera pose. Environment depth used for center ray, corners projected on plane. Arrows show actual data flow; depth branch merges after inference.')
nodes=[(110,155,'Headset camera','RGB + exposure pose'),(303,155,'Local YOLO','640 × 640 · headset GPU'),(496,155,'2D detections','threshold + NMS'),(496,262,'Calibrated ray','center pixel → world ray'),(303,262,'Depth intersection','environment surface hit'),(110,262,'AR overlay','world-space lines + text')]
for x,y,a,b in nodes:text(s,a,x,y,174,47,17,True,fill=PALE);text(s,b,x,y+48,174,35,12)
for a,b,c,d in [(285,179,300,179),(478,179,493,179),(583,236,583,259),(493,286,481,286),(300,286,288,286)]:line(s,a,b,c,d,arrow=True)
text(s,'Environment depth',299,355,183,20,11,True,color=TEAL);line(s,390,351,390,316,arrow=True)

s=slide('geometry','A ray turns a pixel into a 3D point','Use the detection center — not the center of the headset display.','Conceptual geometry (not measured scale): captured camera position o and calibrated ViewportPointToRay direction d. EnvironmentRaycastManager.Raycast returns hit.point P=o+t*d. A camera-parallel plane through P supplies all four box corner intersections. Center may be background. No exact object mesh or geometric centroid is recovered.')
text(s,'Exposure-time\ncamera pose',110,181,135,55,16,True)
text(s,'o',239,225,22,26,17,True,color=TEAL)
for y in [155,283]:line(s,265,236,467,y,dash=True)
line(s,265,236,500,227,arrow=True)
line(s,467,155,467,283);line(s,467,155,558,172);line(s,467,283,558,300);line(s,558,172,558,300)
text(s,'P',503,211,30,27,18,True,color=ORANGE)
text(s,'Measured\ndepth hit',566,204,99,53,15)
text(s,'P = o + t · d',110,294,280,30,21,True,color=TEAL)
text(s,'Camera-parallel approximation plane through P.\nFour corner rays → approximate box, not a 3D mesh.',110,334,550,39,16)
text(s,'center ray',299,204,130,23,13,color=TEAL)

s=slide('stack','What we used','A reproducible Unity project, built from a pinned Meta sample.','Source README.md, scripts/prepare-unity.py, unity/ClassroomBuild.cs. Unity6000.4.5f1, MRUK85.0.0, InferenceEngine2.6.1 OpenXR1.16.1. Meta source pinned3baac1a1a53aa00af3f639425914f14238a97f84. Camera API support scoped to Quest3/3S; physical test Quest3 only. Camera+spatial data permissions required.')
stack=[('Capture + calibration','Meta Passthrough Camera API'),('Environment geometry','MRUK 85 · EnvironmentRaycastManager'),('Local neural inference','YOLOv9 ONNX · Unity Inference Engine 2.6.1'),('XR rendering / Android','Unity 6000.4.5f1 · OpenXR 1.16.1')]
for j,(a,b) in enumerate(stack):
 y=148+j*48;text(s,a,111,y,186,38,15,True,fill=PALE);text(s,b,310,y+4,355,36,15)
text(s,'Quest 3 / 3S  ·  camera + spatial-data permission  ·  no inference server',112,349,550,26,14,True,color=TEAL)

s=slide('code','The center-ray step in code','Use camera calibration and the captured pose; do not guess a distance.','Excerpt from actual QuestYolo.cs Draw(). Requires configured PassthroughCameraAccess cameraAccess, EnvironmentRaycastManager environmentRaycast, exposure-time capturedPose, normalized box bounds. This excerpt is not standalone runnable code. Full setup and complete project generation linked below. If raycast fails no annotation is rendered.')
code='var uv = new Vector2((left + right) / 2,\n                     (bottom + top) / 2);\nvar ray = cameraAccess.ViewportPointToRay(\n    uv, capturedPose);\nif (environmentRaycast.Raycast(ray, out var hit, 12f))\n{\n    Vector3 positionInWorld = hit.point;\n}'
text(s,code,110,148,561,177,12,font='Roboto Mono',fill=GRAY)
text(s,'No hit? Hide the label. A hit may still be background.',111,334,555,25,16,True,color=ORANGE)
text(s,'Read the full source and setup ↗',111,358,555,22,12,color=TEAL,link='https://github.com/ryosuzuki/digital-twin/blob/main/implementations/quest-ondevice-yolo/unity/QuestYolo.cs')

s=slide('platforms','Unity native versus WebXR','Local inference is possible in both; camera and geometry access differ.','README/VERIFICATION: native physically accepted; Web model inference verified on desktop CPU WASM only. Current WebXR displays preview panel, not equivalent first-person object overlay. Quest Browser camera during XR, performance and Raw Camera Access support unverified. WebGPU is not the current web backend.')
text(s,'UNITY NATIVE — CURRENT',110,150,270,39,16,True,fill=PALE);text(s,'WEBXR — CURRENT',399,150,270,39,16,True,fill=GRAY)
text(s,'Headset camera + calibrated rays\n\nGPUCompute on Quest\n\nEnvironment-depth placement\n\nFirst-person overlays verified',111,198,269,155,16)
text(s,'Readable camera / file input\n\nONNX Runtime Web · WASM CPU\n\nPreview panel inside WebXR\n\nQuest browser path unverified',400,198,269,155,16)

s=slide('evidence','What the real-device test shows','Stationary Quest 3 · native 0.2.0 · one short acceptance run.','VERIFICATION.md actual0.2.0 acceptance:122 new-process inference samples, median pipeline271.61ms;121/122 samples had3–5 depth-backed annotations. Not per-object accuracy/depth success rate. Includes preprocessing/scheduling/readback/decode/draw until logging, not just neural model execution or XR FPS.14.954811s stereo video415decodedframes; preview left-eye crop. Motion alignment, physical A-button, long duration, physical unplug remain unverified.')
for x,a,b in [(110,'271.61 ms','median pipeline turnaround'),(303,'122','inference samples'),(496,'121 / 122','samples with 3–5 labels')]:text(s,a,x,159,174,56,26,True,fill=PALE);text(s,b,x,224,174,48,14)
text(s,'Not rendering FPS. Not an object-accuracy benchmark.',111,288,550,31,19,True)
text(s,'Still to measure: moving-head alignment, thermal endurance,\ncontroller interaction, and browser behavior on Quest.',111,329,550,43,16)

s=slide('next','Next: make each object actionable','An XR-Objects-inspired extension — not yet in this demo.','Proposed next layer, not implemented: class-aware temporal association and depth gated smoothing; stable object record; selection using hand/controller ray; contextual menu attached to measured object point; local actions first, optional remote reasoning separately disclosed. Original XR-Objects phone prototype uses cloud reasoning; our local YOLO claim does not imply local LLM. Semantic object point must remain distinguishable from actual mesh/anchor.')
for j,(a,b) in enumerate([('Keep an identity','Associate detections across frames; reject jumps.'),('Select the object','Hand / controller ray selects a tracked object.'),('Attach an interface','Menu, note, timer, or a classroom-specific action.')]):
 y=151+j*64;text(s,str(j+1),110,y,39,39,20,True,fill=PALE);text(s,a,164,y,490,27,19,True);text(s,b,164,y+29,490,32,15)
text(s,'Perception can stay local; cloud reasoning is an optional extra.',111,350,550,24,14,color=TEAL)

s=slide('exercise','Try it, then change one layer','Start from the working sample instead of rebuilding the SDK setup.','Reproduce via README: python3 implementations/quest-ondevice-yolo/scripts/prepare-unity.py /absolute/new/quest-yolo-unity; open Unity6000.4.5f1; ClassroomPrepare then BuildAndroidAPK; install own org.openclaw.classroom.yolo. Existing demo installed0.2.0. Exercise extensions not accepted implementation. Repo publication main and exact source hashes verified separately.')
text(s,'1  Generate the pinned Unity project\n2  Prepare the scene and build Android APK\n3  Grant camera + spatial-data permissions\n4  Look at a chair; inspect the center-depth hit',111,151,551,130,19)
text(s,'Exercise: add one object-bound action',111,296,550,30,20,True,color=TEAL)
text(s,'Keep the label stable, select it, and attach a note or timer.',111,331,550,25,16)
text(s,'GitHub: digital-twin / quest-ondevice-yolo ↗',111,359,550,21,13,color=TEAL,link=REPO)

(R/'manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));(R/'requests.json').write_text(json.dumps(req))
if not args.apply:
    print('DRY RUN: wrote',len(req),'requests and',len(rows),'slide descriptions to',R)
    print('No authentication or Google API request was performed.')
    raise SystemExit(0)
if args.google_helper_dir is None:
    parser.error('--apply requires a caller-provided --google-helper-dir')
sys.path.insert(0, str(args.google_helper_dir.resolve()))
G = importlib.import_module('google_api').Google()
current=G.presentation(ID)
assert len(current['slides']) == 37, 'Expected the 37-slide source template copy; inspect before applying.'
assert {'lecture_slide_002'}.issubset({s['objectId'] for s in current['slides']}), 'Missing source slide template'
assert 'g78a891b14e_0_404' in {x['objectId'] for x in current.get('layouts',[])}, 'Missing section layout'
existing={s['objectId'] for s in current['slides']};assert not existing.intersection(r['slide_id'] for r in rows),'Already present: inspect before retry'
# All changes are append-only task-owned duplicates/new slides. Existing deck/media audience confirmed.
# Small batches avoid Slides quota/oversized transactions; a batch is atomic.
for i in range(0,len(req),90):
 G.batch(ID,req[i:i+90]);print('Applied requests',min(i+90,len(req)),len(req),flush=True)
p=G.presentation(ID);notes=[]
for j,r in enumerate(rows):
 # Index is in the pre-removal slide list: move each new slide to the end.
 notes.append({'updateSlidesPosition':{'slideObjectIds':[r['slide_id']],'insertionIndex':37+len(rows)}})
 s=next(s for s in p['slides'] if s['objectId']==r['slide_id']);n=s['slideProperties']['notesPage']['notesProperties']['speakerNotesObjectId']
 ne=next((e for e in s['slideProperties']['notesPage'].get('pageElements',[]) if e['objectId']==n),{})
 if ne.get('shape',{}).get('text',{}).get('textElements'):notes.append({'deleteText':{'objectId':n,'textRange':{'type':'ALL'}}})
 notes.append({'insertText':{'objectId':n,'text':r['notes']+'\n\nImplementation source: '+REPO+'\nEvidence: VERIFICATION.md and artifacts.json. Existing first37 slides preserved. Diagram is conceptual unless actual demo explicitly stated.'}})
G.batch(ID,notes);p=G.presentation(ID);(R/'after.json').write_text(json.dumps(p));print('DONE',len(p['slides']))
