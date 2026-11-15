"""Owned temporary fixtures outside public checkouts on Windows and Linux."""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from workspace import current


def temporary_directory():
    if os.name == "posix":
        # Native private 0700 fixtures avoid cross-filesystem metadata costs on WSL.
        return tempfile.TemporaryDirectory()
    root = current().runtime() / "unit-fixtures"
    root.mkdir(parents=True, exist_ok=True)
    return tempfile.TemporaryDirectory(dir=root)
