"""Read the installed release identity without network access or persisted state."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent


def installed_version(root=None):
    root = ROOT if root is None else Path(root)
    # Native packages carry their exact build version in the manifest.
    for path in (root / 'manifest.json', root / 'install/release-image.json'):
        if not path.exists():
            continue
        try:
            value = json.loads(path.read_text())['version']
            if isinstance(value, str) and re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9][A-Za-z0-9.-]*)?', value):
                return 'v' + value
        except (OSError, ValueError, KeyError, TypeError):
            pass
        return None
    return None
