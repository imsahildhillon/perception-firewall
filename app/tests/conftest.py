"""Pytest configuration.

Adds ``app/src`` to the import path so the test suite can import
``perception_firewall`` without the package being installed. This keeps
STEP 2 free of any dependency-installation step.
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
