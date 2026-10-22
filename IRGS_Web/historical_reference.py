"""Creator reference selection. Parsing and archive verification belong to Engine.

Only the pinned Catalog location and the owner's explicit ZIP registration are
considered. No campaign, world, dispatcher or save is passed to this boundary.
"""
import json
from pathlib import Path
import threading
import zipfile

from catalog_paths import CATALOG_ROOT
from historical_archive import from_registration


APP_ROOT = Path(__file__).resolve().parent
NOTICES = {
    'not_attached': 'No historical archive is attached on this installation.',
    'incomplete': 'Historical Details is incomplete. Every archive part is required before browsing.',
    'corrupt': 'Historical Details failed verification. Repair the source before browsing.',
    'unavailable': 'The selected historical archive cannot be read on this installation.',
}
SOURCE_ERRORS = (OSError, ValueError, KeyError, TypeError, EOFError, zipfile.BadZipFile)


class ReferenceUnavailable(ValueError):
    def __init__(self, status):
        self.status = status if status in NOTICES else 'unavailable'
        super().__init__(NOTICES[self.status])


def catalog_library(manifest, pin, cache):
    # This is an Engine API: App never reconstructs or parses archive parts.
    try:
        from historical_archive import from_catalog_manifest
    except ImportError as err:
        raise ReferenceUnavailable('unavailable') from err
    return from_catalog_manifest(manifest, pin, cache_dir=cache)


class HistoricalReferences:
    def __init__(self, *, config=None, manifest=None, manifest_pin=None, cache=None, library=None,
                 error=False):
        self.config = Path(config) if config is not None else APP_ROOT / 'cache/reference_sources.json'
        self.manifest = Path(manifest) if manifest is not None else CATALOG_ROOT / 'historical_details/manifest.json'
        self.manifest_pin = manifest_pin
        self.cache = Path(cache) if cache is not None else APP_ROOT / 'cache/historical_details'
        self.fixed_library = library
        self.fixed_error = error
        self._key = None
        self._library = None
        self._lock = threading.RLock()

    def _open(self):
        if self.fixed_library is not None:
            return self.fixed_library, 'local_zip'
        if self.fixed_error:
            raise ReferenceUnavailable('unavailable')
        # An explicit attachment takes precedence, including when it is broken.
        # Never silently substitute a different archive for a selected source.
        if self.config.exists():
            path, kind = self.config, 'local_zip'
        elif self.manifest.exists():
            path, kind = self.manifest, 'catalog_multipart'
        else:
            raise ReferenceUnavailable('not_attached')
        stat = path.stat()
        key = (kind, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)
        if key != self._key:
            if kind == 'local_zip':
                library = from_registration(path)
            else:
                pin = self.manifest_pin
                if pin is None:
                    # Select the source identity from the pinned Catalog release,
                    # never compute a new trusted pin from mutable archive bytes.
                    relative = path.relative_to(CATALOG_ROOT).as_posix()
                    release = json.loads((CATALOG_ROOT / 'release.json').read_text(encoding='utf-8'))
                    pin = release['files_sha256'].get(relative)
                if not isinstance(pin, str) or len(pin) != 64:
                    raise ReferenceUnavailable('unavailable')
                library = catalog_library(path, pin, self.cache)
            self._library, self._key = library, key
        return self._library, kind

    def _failure(self, error):
        self._library, self._key = None, None
        if isinstance(error, ReferenceUnavailable):
            return error
        status = getattr(error, 'status', getattr(error, 'code', None))
        if status not in NOTICES:
            status = 'unavailable' if isinstance(error, OSError) else 'corrupt'
        return ReferenceUnavailable(status)

    def status(self):
        with self._lock:
            try:
                library, kind = self._open()
                result = library.verify_collections()
                return {**result, 'source_kind': kind, 'campaign_effects': False,
                        'adoption_performed': False}
            except (ReferenceUnavailable, *SOURCE_ERRORS) as error:
                failure = self._failure(error)
                return {'id': 'historical-grand-archive', 'title': 'Historical Details',
                        'status': failure.status, 'notice': str(failure),
                        'collections': [], 'campaign_effects': False,
                        'adoption_performed': False}

    def read(self, operation, *args, **kwargs):
        if operation not in ('search', 'record'):
            raise ValueError('Unknown historical reference operation')
        with self._lock:
            try:
                library, _ = self._open()
                return getattr(library, operation)(*args, **kwargs)
            except (ReferenceUnavailable, *SOURCE_ERRORS) as error:
                # Source paths and exception text remain private to the owner.
                raise self._failure(error) from error
