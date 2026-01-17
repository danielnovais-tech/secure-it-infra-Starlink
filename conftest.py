from __future__ import annotations

import os
import sys
from pathlib import Path


# Put "src" ahead of the repo root on sys.path so imports like
# "secure_it_infra.*" and "starlink_security.*" resolve to packages under
# src/, not to legacy modules/folders at the repo root.
SRC_DIR = (Path(__file__).resolve().parent / "src").resolve()


def _ensure_src_first() -> None:
    if not SRC_DIR.is_dir():
        return

    src_str = str(SRC_DIR)
    try:
        while src_str in sys.path:
            sys.path.remove(src_str)
    except ValueError:
        pass

    sys.path.insert(0, src_str)

    for shadowed in ("secure_it_infra", "starlink_security"):
        sys.modules.pop(shadowed, None)


# Best-effort early insert (pytest may still reorder sys.path later)
_ensure_src_first()


def pytest_configure(config):  # noqa: D401
    """Ensure src/ stays first on sys.path for test collection."""
    _ensure_src_first()

    if os.getenv("DEBUG_PYTEST_PATHS"):
        print("[DEBUG] sys.path[0:5]=", sys.path[0:5])
        try:
            import secure_it_infra  # noqa: F401

            import secure_it_infra as _sii

            print(
                "[DEBUG] secure_it_infra file=",
                getattr(_sii, "__file__", None),
                "path=",
                getattr(_sii, "__path__", None),
            )
        except Exception as exc:  # pragma: no cover
            print("[DEBUG] secure_it_infra import failed:", repr(exc))

        try:
            import starlink_security  # noqa: F401

            import starlink_security as _ss

            print(
                "[DEBUG] starlink_security file=",
                getattr(_ss, "__file__", None),
                "path=",
                getattr(_ss, "__path__", None),
            )
        except Exception as exc:  # pragma: no cover
            print("[DEBUG] starlink_security import failed:", repr(exc))
