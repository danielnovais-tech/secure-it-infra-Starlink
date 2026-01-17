from __future__ import annotations

import sys
from pathlib import Path


# Ensure "src" is ahead of the repo root on sys.path so imports like
# "secure_it_infra.*" resolve to "src/secure_it_infra" (package) instead of the
# legacy root-level "secure_it_infra.py" module.
SRC_DIR = (Path(__file__).resolve().parent.parent / "src").resolve()
if SRC_DIR.is_dir():
    sys.path.insert(0, str(SRC_DIR))
