"""Local source locations must never enter a portable App release binding."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('reference_release_refresh',
    Path(__file__).resolve().parents[1] / 'refresh_component_releases.py')
refresh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(refresh)


class ReferenceAttachmentPackagingTests(unittest.TestCase):
    def test_app_refresh_retains_code_and_excludes_local_source_attachment(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[2]) as folder:
            root = Path(folder)
            app = root / 'IRGS_Web'
            (app / 'cache').mkdir(parents=True)
            (app / 'server.py').write_text('print("synthetic app")\n')
            (app / 'cache/reference_sources.json').write_text(json.dumps({
                'historical_archive': {'path': '/local-only/reference.zip'}}))
            with patch.object(refresh, 'ROOT', root): refresh.refresh('app')
            binding = json.loads((app / 'release.json').read_text())
            self.assertIn('server.py', binding['files_sha256'])
            self.assertNotIn('cache/reference_sources.json', binding['files_sha256'])
            self.assertNotIn('/local-only', json.dumps(binding))


if __name__ == '__main__': unittest.main()
