#!/usr/bin/env python3
"""Loopback-only gateway for the current, separate Home and Lab Spatial apps.
No dependencies; no room data or runtime configuration is bundled.
"""
import argparse
import http.client
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

HOP = {'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
       'te', 'trailer', 'transfer-encoding', 'upgrade', 'host', 'content-length'}

def load_config(path):
    config = json.loads(Path(path).read_text())
    ports = [config.get('dashboard_port', 39800)]
    for name in ('home', 'lab'):
        venue = config[name]
        u = urlsplit(venue['upstream'])
        if u.scheme != 'http' or u.hostname not in ('127.0.0.1', 'localhost', '::1') or u.username or u.password or u.path not in ('', '/') or u.query or u.fragment:
            raise ValueError(f'{name}: upstream must be a loopback HTTP origin, without credentials or path')
        route = venue['route']
        if not route.startswith('/') or route.startswith('//') or any(c in route for c in ('?', '#', '\r', '\n')):
            raise ValueError(f'{name}: route must be an absolute local path')
        venue['host'], venue['port'] = u.hostname, u.port or 80
        ports.append(venue['proxy_port'])
    if len(set(ports)) != 3 or any(not isinstance(x, int) or not 1024 <= x <= 65535 for x in ports):
        raise ValueError('three distinct, unprivileged local listening ports are required')
    if any(v['port'] in ports for v in (config['home'], config['lab'])):
        raise ValueError('upstreams must not point back to a gateway listener')
    return config

def probe(venue):
    conn = http.client.HTTPConnection(venue['host'], venue['port'], timeout=3)
    try:
        conn.request('GET', venue['route'])
        response = conn.getresponse()
        response.read(1024)
        return {'available': response.status == 200, 'http_status': response.status}
    except (OSError, http.client.HTTPException):
        return {'available': False, 'http_status': None}
    finally:
        conn.close()

class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    def log_message(self, *_):
        pass  # Private request paths and query strings must not enter logs.
    def trusted(self):
        host = self.headers.get('Host', '')
        allowed = {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
        origin = self.headers.get('Origin')
        return host in allowed and (not origin or origin in {'http://' + x for x in allowed})
    def respond(self, code, body, content_type='application/json'):
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(body)
    def do_GET(self):
        self.dispatch()
    def do_HEAD(self):
        self.dispatch()
    def do_POST(self):
        self.dispatch()
    def dispatch(self):
        if not self.trusted():
            return self.respond(403, b'{"error":"loopback same-origin access only"}')
        if self.path.startswith('//') or not self.path.startswith('/'):
            return self.respond(400, b'{"error":"local path required"}')
        if self.server.venue is None:
            if self.command not in ('GET', 'HEAD'):
                return self.respond(405, b'{}')
            if self.path == '/status':
                status = {name: dict(probe(self.server.config[name]),
                    url=f"http://127.0.0.1:{self.server.config[name]['proxy_port']}{self.server.config[name]['route']}")
                    for name in ('home', 'lab')}
                return self.respond(200, json.dumps(status).encode())
            if self.path in ('/', '/index.html'):
                return self.respond(200, Path(__file__).with_name('index.html').read_bytes(), 'text/html; charset=utf-8')
            return self.respond(404, b'{}')
        self.proxy()
    def proxy(self):
        venue = self.server.venue
        conn = http.client.HTTPConnection(venue['host'], venue['port'], timeout=15)
        started = False
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length < 0 or length > 16 * 1024 * 1024 or self.headers.get('Transfer-Encoding'):
                return self.respond(413, b'{"error":"unsupported request body"}')
            body = self.rfile.read(length) if length else None
            headers = {k: v for k, v in self.headers.items() if k.lower() not in HOP | {'origin', 'referer', 'authorization', 'cookie'}}
            conn.request(self.command, self.path, body=body, headers=headers)
            response = conn.getresponse()
            started = True
            self.send_response(response.status)
            for key, value in response.getheaders():
                if key.lower() not in HOP | {'set-cookie', 'access-control-allow-origin'}:
                    if key.lower() == 'location' and value.startswith(venue['upstream']):
                        value = f'http://127.0.0.1:{self.server.server_port}' + value[len(venue['upstream']):]
                    self.send_header(key, value)
            self.send_header('Connection', 'close')
            self.end_headers()
            if self.command != 'HEAD':
                while True:
                    chunk = response.read1(65536)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
            self.close_connection = True
        except (OSError, http.client.HTTPException, ValueError):
            if started:
                self.close_connection = True
            else:
                self.respond(502, b'{"error":"configured twin unavailable"}')
        finally:
            conn.close()

def serve(config):
    servers = []
    try:
        for name in (None, 'home', 'lab'):
            venue = config[name] if name else None
            port = venue['proxy_port'] if venue else config.get('dashboard_port', 39800)
            server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
            server.daemon_threads = True
            server.venue, server.config = venue, config
            servers.append(server)
        for server in servers:
            threading.Thread(target=server.serve_forever, daemon=True).start()
        print(f"Home / Lab catalog: http://127.0.0.1:{servers[0].server_port}/", flush=True)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        for server in servers:
            server.shutdown()
            server.server_close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True, help='Private JSON configuration; never commit this file')
    args = parser.parse_args()
    serve(load_config(args.config))
