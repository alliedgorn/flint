"""Core data models for Sentinel."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Self


class Ecosystem(Enum):
    PYPI = "pypi"
    NPM = "npm"


@dataclass
class IngestedPackage:
    """A downloaded and unpacked package ready for analysis."""

    name: str
    version: str
    ecosystem: Ecosystem
    source_dir: Path
    metadata: dict
    _temp_dir: TemporaryDirectory | None = field(default=None, repr=False)

    def source_files(self, extensions: set[str] | None = None) -> list[Path]:
        """List source files, optionally filtering by extension.

        Args:
            extensions: Set of extensions to filter by (e.g. {".py", ".js"}).
                       If None, returns all files.
        """
        files = [p for p in self.source_dir.rglob("*") if p.is_file()]
        if extensions:
            files = [f for f in files if f.suffix in extensions]
        return sorted(files)

    def cleanup(self) -> None:
        """Remove the temporary directory and all unpacked files."""
        if self._temp_dir is not None:
            self._temp_dir.cleanup()
            self._temp_dir = None

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc: object) -> None:
        self.cleanup()
