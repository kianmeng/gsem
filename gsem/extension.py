import json
import os
from gi.repository import Gio

from gsem.utils import get_json_response
from gsem.config import (
    EXTENSION_DIR,
    GNOME_SHELL_VERSION,
    API_DETAIL,
)


class Extension:

    def __init__(self, uuid):
        self.uuid = uuid
        self._meta = None
        self._remote_meta = None

    @property
    def meta(self):
        """Local metadata dict."""
        if not self._meta:
            with open(os.path.join(EXTENSION_DIR, self.uuid, 'metadata.json')) as f:
                self._meta = json.load(f)
        return self._meta

    @property
    def remote_meta(self):
        """Remote metadata dict."""
        if not self._remote_meta:
            self._remote_meta = get_json_response(API_DETAIL, {
                'uuid': self.uuid,
                'shell_version': '.'.join(str(v) for v in GNOME_SHELL_VERSION),
            })
        return self._remote_meta

    def outdated(self):
        return self.remote_meta['version'] > self.meta['version']

    def enabled(self):
        return self.uuid in (Gio.Settings
                             .new('org.gnome.shell')
                             .get_value('enabled-extensions'))


class ExtensionManager:

    def __init__(self, ext_dir=EXTENSION_DIR):
        self.ext_dir = ext_dir

    def enabled_extensions(self):
        return set(
            Gio.Settings.new('org.gnome.shell')
            .get_value('enabled-extensions')
        ).intersection({ex.uuid for ex in self.installed()})

    def installed(self):
        for uuid in os.listdir(self.ext_dir):
            yield Extension(uuid)

    def enabled(self):
        for uuid in self.enabled_extensions():
            yield Extension(uuid)
