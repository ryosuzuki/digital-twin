import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.dirname(fileURLToPath(import.meta.url));
const port=Number(process.env.PORT||8818);
const mime={'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.json':'application/json','.jpg':'image/jpeg','.glb':'model/gltf-binary'};
http.createServer((req,res)=>{let url;try{url=decodeURIComponent(req.url.split('?')[0]);}catch{return res.writeHead(400).end();}const file=path.resolve(root,'.'+(url==='/'?'/index.html':url));
if(!file.startsWith(root+path.sep)){res.writeHead(403).end();return;}
fs.stat(file,(err,st)=>{if(err||!st.isFile()){res.writeHead(404).end();return;}
res.writeHead(200,{'Content-Type':mime[path.extname(file)]||'application/octet-stream','Content-Length':st.size});fs.createReadStream(file).pipe(res);});
}).listen(port,'127.0.0.1',()=>console.log(`Open http://127.0.0.1:${port}`));
