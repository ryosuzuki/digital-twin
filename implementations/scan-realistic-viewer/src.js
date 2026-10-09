import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {SparkRenderer,SplatMesh} from '@sparkjsdev/spark';
const scene=new THREE.Scene(); scene.background=new THREE.Color('#101821');
const camera=new THREE.PerspectiveCamera(65,innerWidth/innerHeight,.03,200);
const renderer=new THREE.WebGLRenderer({antialias:false,preserveDrawingBuffer:true});
renderer.setSize(innerWidth,innerHeight);renderer.setPixelRatio(Math.min(devicePixelRatio,1.5)); document.body.appendChild(renderer.domElement);
const spark=new SparkRenderer({renderer});scene.add(spark);
const room=new SplatMesh({url:'/room.spz'});room.quaternion.set(0,0,0,1);scene.add(room);
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;
let touring=false,start=0,homePos=[-1,.25,-.35],homeTarget=[1.8,-.25,.1];
function home(){touring=false;controls.enableDamping=false;controls.update();camera.position.fromArray(homePos);controls.target.fromArray(homeTarget);controls.update();controls.enableDamping=true;document.querySelector('#tour').textContent='Start walkthrough';}
document.querySelector('#home').onclick=home;document.querySelector('#tour').onclick=()=>{touring=!touring;start=performance.now();document.querySelector('#tour').textContent=touring?'Pause walkthrough':'Start walkthrough';};
window.demo={camera,controls,room,renderer,scene,setView(p,t){homePos=p;homeTarget=t;home();},getView(){return {position:camera.position.toArray(),target:controls.target.toArray()}},tour(t){const s=t/1000;camera.position.set(homePos[0]+.48*Math.sin(s*.23),homePos[1]+.08*Math.sin(s*.3),homePos[2]+.15*Math.sin(s*.18));controls.target.set(homeTarget[0]+.5*Math.sin(s*.19),homeTarget[1],homeTarget[2]);controls.update();}};
await room.initialized;
const box=room.getBoundingBox();window.demo.bounds={min:box.min.toArray(),max:box.max.toArray()};
home();window.demo.ready=true;document.querySelector('#status').textContent='Original scan · no generative enhancement';
renderer.setAnimationLoop(()=>{if(touring)window.demo.tour(performance.now()-start);else controls.update();renderer.render(scene,camera)});
onresize=()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight)};
