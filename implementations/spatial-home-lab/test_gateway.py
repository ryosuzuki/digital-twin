import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path
from http.server import ThreadingHTTPServer
from gateway import Handler, load_config
from fixture import start

class GatewayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.home, cls.lab = start(0, 'Home'), start(0, 'Lab')
        cls.servers = []
        cls.config = {}
        for name, upstream in [('home', cls.home), ('lab', cls.lab)]:
            venue = {'host': '127.0.0.1', 'port': upstream.server_port, 'upstream': f'http://127.0.0.1:{upstream.server_port}', 'route': f'/{name}.html'}
            server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
            server.venue = venue
            venue['proxy_port'] = server.server_port
            cls.config[name] = venue
            cls.servers.append(server)
        dashboard = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        dashboard.venue, dashboard.config = None, cls.config
        cls.dashboard = dashboard
        cls.servers.append(dashboard)
        for server in cls.servers:
            threading.Thread(target=server.serve_forever, daemon=True).start()
    @classmethod
    def tearDownClass(cls):
        for server in cls.servers + [cls.home, cls.lab]:
            server.shutdown()
            server.server_close()
    def request(self, index, path, method='GET', body=None, headers=None):
        c = http.client.HTTPConnection('127.0.0.1', self.servers[index].server_port, timeout=3)
        c.request(method, path, body=body, headers=headers or {})
        r = c.getresponse()
        out = r.status, r.read()
        c.close()
        return out
    def test_home_lab_separate(self):
        self.assertIn(b'SYNTHETIC Home', self.request(0, '/home.html')[1])
        self.assertIn(b'SYNTHETIC Lab', self.request(1, '/lab.html')[1])
        self.assertEqual(json.loads(self.request(0, '/state')[1])['venue'], 'Home')
        self.assertEqual(json.loads(self.request(1, '/state')[1])['venue'], 'Lab')
    def test_root_module_forwarding(self):
        self.assertIn(b"fetch('/state')", self.request(0, '/fixture.js')[1])
    def test_interaction_forwarding(self):
        old = json.loads(self.request(0, '/state')[1])['events']
        self.assertEqual(self.request(0, '/event', 'POST', 'demo')[0], 200)
        self.assertEqual(json.loads(self.request(0, '/state')[1])['events'], old+1)
    def test_dashboard_status(self):
        status, data = self.request(2, '/status')
        self.assertEqual(status, 200)
        self.assertTrue(all(v['available'] for v in json.loads(data).values()))
    def test_hostile_origin(self):
        self.assertEqual(self.request(0, '/state', headers={'Origin':'https://hostile.invalid'})[0], 403)
    def test_hostile_host(self):
        self.assertEqual(self.request(0, '/state', headers={'Host':'hostile.invalid'})[0], 403)
    def test_dashboard_no_mutations(self):
        self.assertEqual(self.request(2, '/status', 'POST', 'x')[0], 405)
    def test_missing_path(self):
        self.assertEqual(self.request(0, '/missing')[0], 404)
    def test_bad_configs(self):
        base=json.loads(Path(__file__).with_name('config.example.json').read_text())
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'config.json'
            for origin in ['http://example.com', 'http://user:secret@localhost:1234', 'https://127.0.0.1', 'http://127.0.0.1/path']:
                base['home']['upstream']=origin
                p.write_text(json.dumps(base))
                with self.assertRaises(ValueError):load_config(p)
    def test_valid_config(self):
        self.assertEqual(load_config(Path(__file__).with_name('config.example.json'))['lab']['port'],41002)

if __name__ == '__main__':
    unittest.main()
