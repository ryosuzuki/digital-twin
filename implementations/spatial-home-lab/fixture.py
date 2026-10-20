#!/usr/bin/env python3
"""Synthetic upstreams for gateway checks. No scan or camera input."""
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PAGE = '''<!doctype html><meta name="viewport" content="width=device-width"><title>SYNTHETIC {venue} fixture</title><style>body{{font:20px system-ui;margin:50px;background:#eff4f6}}.room{{width:300px;height:200px;border:4px solid #346;transform:perspective(500px) rotateX(25deg) rotateY(-15deg);position:relative;background:repeating-linear-gradient(90deg,#eee 0 29px,#ccd 30px)}}#object{{position:absolute;top:70px;width:40px;height:50px;background:#e87d32}}button{{padding:12px}}</style><h1>SYNTHETIC {venue} fixture</h1><p>This moving box is not a real room, camera or tracking output.</p><div class="room"><div id="object"></div></div><p id="status"></p><button id="event">Send fixture interaction</button><script type="module" src="/fixture.js"></script>'''
JS = b'''async function tick(){const s=await(await fetch('/state')).json();document.querySelector('#object').style.left=(s.sequence%200)+'px';document.querySelector('#status').textContent='Synthetic sequence '+s.sequence+' | interactions '+s.events;}document.querySelector('#event').onclick=async()=>{await fetch('/event',{method:'POST',body:'fixture interaction'});tick();};tick();setInterval(tick,500);'''

class Fixture(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass
    def do_GET(self):
        if self.path in ('/home.html', '/lab.html'):
            body = PAGE.format(venue=self.server.venue).encode()
            kind = 'text/html'
        elif self.path == '/fixture.js':
            body, kind = JS, 'text/javascript'
        elif self.path == '/state':
            body, kind = json.dumps({'venue': self.server.venue, 'sequence': int(time.time()*2), 'events': self.server.events}).encode(), 'application/json'
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header('Content-Type', kind)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def do_POST(self):
        if self.path != '/event':
            return self.send_error(404)
        self.rfile.read(int(self.headers.get('Content-Length', 0)))
        self.server.events += 1
        self.send_response(200)
        self.send_header('Content-Length', '2')
        self.end_headers()
        self.wfile.write(b'{}')

def start(port, venue):
    server = ThreadingHTTPServer(('127.0.0.1', port), Fixture)
    server.venue, server.events = venue, 0
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server

if __name__ == '__main__':
    servers = [start(41001, 'Home'), start(41002, 'Lab')]
    print('Synthetic Home / Lab upstreams ready. No private inputs.', flush=True)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for server in servers:
            server.shutdown()
