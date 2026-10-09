import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
const root=path.dirname(new URL(import.meta.url).pathname);
const originalSource='/path/to/local-assets';
const source=fs.existsSync(path.join(root,'scan'))?path.join(root,'scan'):originalSource;
const mime={'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.json':'application/json','.jpg':'image/jpeg','.obj':'text/plain'};
http.createServer((req,res)=>{let url=decodeURIComponent(req.url.split('?')[0]); const base=url.startsWith('/scan/')?source:root;
let file=path.resolve(base,url.startsWith('/scan/')?url.slice(6):'.'+(url==='/'?'/index.html':url));
if(!file.startsWith(base+'/')){res.writeHead(403).end();return;}
fs.stat(file,(err,st)=>{if(err||!st.isFile()){res.writeHead(404).end();return;}
res.writeHead(200,{'Content-Type':mime[path.extname(file)]||'application/octet-stream','Content-Length':st.size});fs.createReadStream(file).pipe(res);});
}).listen(Number(process.env.PORT||8827),'127.0.0.1',()=>console.log('http://127.0.0.1:8827'));
