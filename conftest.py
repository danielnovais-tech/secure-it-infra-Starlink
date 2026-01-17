from __future__ import annotations

import sys
from pathlib import Path


# Put "src" ahead of the repo root on sys.path so imports like
# "secure_it_infra.*" and "starlink_security.*" resolve to packages under
# src/, not to legacy modules/folders at the repo root.
SRC_DIR = (Path(__file__).resolve().parent / "src").resolve()
if SRC_DIR.is_dir():
    sys.path.insert(0, str(SRC_DIR))

    for shadowed in ("secure_it_infra", "starlink_security"):
        sys.modules.pop(shadowed, None)
