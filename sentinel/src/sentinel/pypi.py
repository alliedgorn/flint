"""PyPI package ingester."""

from __future__ import annotations

import io
import tarfile
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

import httpx

from sentinel.ingester import (
    HTTP_TIMEOUT_SECONDS,
    MAX_DOWNLOAD_BYTES,
    MAX_EXTRACTED_BYTES,
    DownloadTooLargeError,
    ExtractionTooLargeError,
    PackageIngester,
    PackageNotFoundError,
    PathTraversalError,
)
from sentinel.models import Ecosystem, IngestedPackage

PYPI_BASE = "https://pypi.org/pypi"


class PyPIIngester(PackageIngester):
    """Ingester for PyPI packages."""

    ecosystem = Ecosystem.PYPI

    async def fetch_metadata(self, name: str, version: str | None = None) -> dict:
        url = f"{PYPI_BASE}/{name}/json" if version is None else f"{PYPI_BASE}/{name}/{version}/json"
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_SECONDS) as client:
            resp = await client.get(url)
            if resp.status_code == 404:
                raise PackageNotFoundError(f"PyPI package not found: {name}" + (f"=={version}" if version else ""))
            resp.raise_for_status()
            return resp.json()

    async def resolve_latest_version(self, name: str) -> str:
        data = await self.fetch_metadata(name)
        return data["info"]["version"]

    async def list_versions(self, name: str) -> list[str]:
        data = await self.fetch_metadata(name)
        return list(data.get("releases", {}).keys())

    async def ingest(self, name: str, version: str | None = None) -> IngestedPackage:
        if version is None:
            version = await self.resolve_latest_version(name)

        data = await self.fetch_metadata(name, version)
        urls = data.get("urls", [])
        download_url = _pick_download_url(urls)

        if download_url is None:
            raise PackageNotFoundError(f"No downloadable distribution for {name}=={version}")

        archive_bytes = await _download(download_url)
        temp_dir = TemporaryDirectory(prefix=f"sentinel-pypi-{name}-{version}-")
        dest = Path(temp_dir.name)
        dest.chmod(0o700)

        try:
            _extract(archive_bytes, download_url, dest)
        except Exception:
            temp_dir.cleanup()
            raise

        # Find the actual source directory — sdists often have a top-level dir
        source_dir = _find_source_dir(dest)

        return IngestedPackage(
            name=name,
            version=version,
            ecosystem=Ecosystem.PYPI,
            source_dir=source_dir,
            metadata=data.get("info", {}),
            _temp_dir=temp_dir,
        )


def _pick_download_url(urls: list[dict]) -> str | None:
    """Pick the best download URL: prefer sdist, fall back to wheel."""
    sdists = [u for u in urls if u.get("packagetype") == "sdist"]
    if sdists:
        return sdists[0]["url"]
    wheels = [u for u in urls if u.get("packagetype") == "bdist_wheel"]
    if wheels:
        return wheels[0]["url"]
    if urls:
        return urls[0]["url"]
    return None


async def _download(url: str) -> bytes:
    """Download a file with size limit enforcement."""
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_SECONDS) as client:
        async with client.stream("GET", url) as resp:
            resp.raise_for_status()

            content_length = resp.headers.get("content-length")
            if content_length and int(content_length) > MAX_DOWNLOAD_BYTES:
                raise DownloadTooLargeError(
                    f"Download would be {int(content_length)} bytes, limit is {MAX_DOWNLOAD_BYTES}"
                )

            chunks = []
            total = 0
            async for chunk in resp.aiter_bytes():
                total += len(chunk)
                if total > MAX_DOWNLOAD_BYTES:
                    raise DownloadTooLargeError(
                        f"Download exceeded {MAX_DOWNLOAD_BYTES} bytes"
                    )
                chunks.append(chunk)

            return b"".join(chunks)


def _validate_path(member_path: str, dest: Path) -> Path:
    """Validate that an archive member path doesn't escape the destination."""
    resolved = (dest / member_path).resolve()
    if not str(resolved).startswith(str(dest.resolve())):
        raise PathTraversalError(f"Path traversal detected: {member_path}")
    return resolved


def _is_zip_symlink(info: zipfile.ZipInfo) -> bool:
    """Check if a zip entry is a symlink (Unix external attributes)."""
    # Unix symlink: external_attr >> 16 gives Unix mode, 0o120000 = symlink
    unix_mode = info.external_attr >> 16
    return (unix_mode & 0o170000) == 0o120000


def _extract(archive_bytes: bytes, url: str, dest: Path) -> None:
    """Extract an archive with security checks."""
    total_extracted = 0

    if url.endswith((".tar.gz", ".tgz")):
        with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as tf:
            for member in tf.getmembers():
                _validate_path(member.name, dest)

                if member.isfile():
                    total_extracted += member.size
                    if total_extracted > MAX_EXTRACTED_BYTES:
                        raise ExtractionTooLargeError(
                            f"Extracted content exceeded {MAX_EXTRACTED_BYTES} bytes"
                        )

            tf.extractall(dest, filter="data")

    elif url.endswith((".zip", ".whl")):
        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as zf:
            for info in zf.infolist():
                _validate_path(info.filename, dest)

                # Skip symlinks — zip symlinks have external_attr with
                # the symlink flag set (0xA0000000). No equivalent to
                # tarfile's filter="data" for zip, so we skip manually.
                if _is_zip_symlink(info):
                    continue

                if not info.is_dir():
                    total_extracted += info.file_size
                    if total_extracted > MAX_EXTRACTED_BYTES:
                        raise ExtractionTooLargeError(
                            f"Extracted content exceeded {MAX_EXTRACTED_BYTES} bytes"
                        )

            # Extract member by member, skipping symlinks
            for info in zf.infolist():
                if _is_zip_symlink(info):
                    continue
                target = _validate_path(info.filename, dest)
                zf.extract(info, dest)
    else:
        raise ValueError(f"Unsupported archive format: {url}")


def _find_source_dir(dest: Path) -> Path:
    """Find the actual source directory inside the extraction target.

    sdists typically extract to a single top-level directory like
    'requests-2.31.0/'. If there's exactly one directory at the top level,
    return it. Otherwise return dest itself.
    """
    entries = list(dest.iterdir())
    if len(entries) == 1 and entries[0].is_dir():
        return entries[0]
    return dest
