"""Windows launcher probes use temporary HTTP fixtures, never real saves."""
import json
import os
import sys
import subprocess
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'IRGS_Web'))
from engine_paths import ENGINE_ROOT
CANONICAL = ENGINE_ROOT / 'Start-IRGS-3.3.ps1'
WEB = ROOT / 'IRGS_Web' / 'Start-IRGS.ps1'


def ps_quote(value):
    return "'" + str(value).replace("'", "''") + "'"


@unittest.skipUnless(os.name == 'nt', 'The installed launchers target Windows PowerShell')
class LauncherTests(unittest.TestCase):
    def powershell(self, command, *, timeout=15):
        return subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', command],
                              capture_output=True, text=True, timeout=timeout)

    def fixture(self, *, valid=False, session=True):
        paths = []

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                paths.append(self.path)
                if self.path == '/api/catalog' and valid:
                    data = {'core': {'id': 'IRGS-CORE-3.3', 'version': '3.3', 'single_world_per_campaign': True}}
                elif self.path == '/api/campaigns' and session:
                    data = {'campaigns': [], 'token': 'synthetic-local-session-token'}
                else:
                    data = {'message': 'An unrelated site can mention IRGS without being an IRGS host'}
                raw = json.dumps(data).encode()
                self.send_response(200); self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(raw))); self.end_headers(); self.wfile.write(raw)

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        self.addCleanup(server.server_close); self.addCleanup(thread.join)
        self.addCleanup(server.shutdown)
        return server, paths

    def probe(self, port):
        result = self.powershell('. ' + ps_quote(CANONICAL) + '; Get-IrgsHostState ' + str(port))
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def test_powershell_entrypoints_parse_without_execution(self):
        for path in (CANONICAL, WEB):
            result = self.powershell("$t=$null;$e=$null;[System.Management.Automation.Language.Parser]::ParseFile(" +
                ps_quote(path) + ",[ref]$t,[ref]$e)|Out-Null;if($e.Count){$e|Out-String;exit 1}")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_complete_irgs_health_is_ready_and_uses_only_read_routes(self):
        server, paths = self.fixture(valid=True)
        self.assertEqual(self.probe(server.server_port), 'Ready')
        self.assertEqual(paths, ['/api/catalog', '/api/campaigns'])

    def test_unrelated_http_listener_is_occupied_not_reused(self):
        server, paths = self.fixture()
        self.assertEqual(self.probe(server.server_port), 'Occupied')
        self.assertEqual(paths, ['/api/catalog'])

    def test_irgs_looking_catalogue_without_session_health_is_occupied(self):
        server, _ = self.fixture(valid=True, session=False)
        self.assertEqual(self.probe(server.server_port), 'Occupied')

    def test_closed_listener_is_stopped(self):
        server, _ = self.fixture(valid=True)
        port = server.server_port
        server.shutdown(); server.server_close()
        self.assertEqual(self.probe(port), 'Stopped')

    def test_occupied_main_entrypoint_fails_readably_without_launching(self):
        server, paths = self.fixture()
        result = subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                                 str(CANONICAL), '-NoBrowser', '-Port', str(server.server_port)],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 1)
        self.assertIn('Another application is using port', result.stdout)
        self.assertIn('left it running', result.stdout)
        self.assertEqual(paths, ['/api/catalog'])
        self.assertEqual(self.probe(server.server_port), 'Occupied')

    def test_repeated_ready_launches_reuse_without_starting_process_or_browser(self):
        server, paths = self.fixture(valid=True)
        # Release verification itself is covered by activation. This fixture
        # isolates reuse and forbids every process/browser launch explicitly.
        command = ('. ' + ps_quote(CANONICAL) + '; function Confirm-IrgsRelease {};' +
                   "function Start-Process {throw 'Unexpected second host or browser'};" +
                   'Start-IrgsWebsite -HostPort ' + str(server.server_port) + ' -OpenBrowser $false -WaitSeconds 2')
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: self.powershell(command), range(2)))
        for result in results:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('Reusing the existing website', result.stdout)
        self.assertEqual(len(paths), 8)


if __name__ == '__main__':
    unittest.main()
