"""Proves the interface layer (and its mocks) can be imported and used
without any ML/Qualcomm dependency present, and performs a static source
check that no interface/mock file imports one.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

FORBIDDEN_MODULES = (
    "qai_hub",
    "transformers",
    "torch",
    "onnxruntime",
    "qnn",
    "genie",
    "whisper",
    "qwen",
)

INTERFACES_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "src"
    / "perception_firewall"
    / "interfaces"
)

IMPORT_LINE_RE = re.compile(r"^\s*(?:import|from)\s+([\w.]+)", re.MULTILINE)


def _all_python_source_files() -> list[Path]:
    return sorted(INTERFACES_DIR.rglob("*.py"))


def test_interfaces_directory_is_non_empty():
    files = _all_python_source_files()
    assert files, "expected interface source files to exist"


@pytest.mark.parametrize("path", _all_python_source_files(), ids=lambda p: p.name)
def test_source_file_has_no_forbidden_imports(path: Path):
    source = path.read_text(encoding="utf-8")
    imported_roots = {
        match.split(".")[0].lower() for match in IMPORT_LINE_RE.findall(source)
    }
    hits = imported_roots & set(FORBIDDEN_MODULES)
    assert not hits, f"{path} imports forbidden module(s): {hits}"


def test_package_import_pulls_in_only_stdlib_and_own_package():
    before = set(sys.modules)
    import perception_firewall.interfaces  # noqa: F401
    import perception_firewall.interfaces.mocks  # noqa: F401

    after = set(sys.modules)
    new_top_level = {m.split(".")[0] for m in (after - before)}
    hits = new_top_level & set(FORBIDDEN_MODULES)
    assert not hits, f"importing interfaces pulled in forbidden module(s): {hits}"
