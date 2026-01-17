from __future__ import annotations

import sys
from pathlib import Path


# Ensure "src" is ahead of the repo root on sys.path so imports like
# "secure_it_infra.*" resolve to "src/secure_it_infra" (package) instead of the
# legacy root-level "secure_it_infra.py" module.
SRC_DIR = (Path(__file__).resolve().parent.parent / "src").resolve()
if SRC_DIR.is_dir():
    sys.path.insert(0, str(SRC_DIR))

    # If these were imported before we reordered sys.path (e.g. by plugins or
    # other tests), drop them so they re-import from the correct location.
    for shadowed in ("secure_it_infra", "starlink_security"):
        sys.modules.pop(shadowed, None)
