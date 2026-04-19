"""npm registry package ingester."""

from __future__ import annotations

import io
import tarfile
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

NPM_REGISTRY = "https://registry.npmjs.org"


class NpmIngester(PackageIngester):
    """Ingester for npm packages."""

    ecosystem = Ecosystem.NPM

    async def fetch_metadata(self, name: str, version: str | None = None) -> dict:
        # Handle scoped packages: @scope/name
        encoded_name = name.replace("/", "%2F")
        url = f"{NPM_REGISTRY}/{encoded_name}"
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_SECONDS) as client:
            resp = await client.get(url)
            if resp.status_code == 404:
                raise PackageNotFoundError(f"npm package not found: {name}")
            resp.raise_for_status()
            data = resp.json()

        if version is not None:
            versions = data.get("versions", {})
            if version not in versions:
                raise PackageNotFoundError(f"npm package version not found: {name}@{version}")
            return versions[version]

        return data

    async def resolve_latest_version(self, name: str) -> str:
        data = await self.fetch_metadata(name)
        dist_tags = data.get("dist-tags", {})
        latest = dist_tags.get("latest")
        if not latest:
            raise PackageNotFoundError(f"No latest version for npm package: {name}")
        return latest

    async def list_versions(self, name: str) -> list[str]:
        data = await self.fetch_metadata(name)
        return list(data.get("versions", {}).keys())

    async def ingest(self, name: str, version: str | None = None) -> IngestedPackage:
        if version is None:
            version = await self.resolve_latest_version(name)

        version_data = await self.fetch_metadata(name, version)
        tarball_url = version_data.get("dist", {}).get("tarball")
        if not tarball_url:
            raise PackageNotFoundError(f"No tarball URL for {name}@{version}")

        archive_bytes = await _download(tarball_url)
        temp_dir = TemporaryDirectory(prefix=f"sentinel-npm-{name}-{version}-")
        dest = Path(temp_dir.name)
        dest.chmod(0o700)

        try:
            _extract_npm_tarball(archive_bytes, dest)
        except Exception:
            temp_dir.cleanup()
            raise

        # npm tarballs contain a 'package/' prefix directory
        source_dir = _find_source_dir(dest)

        metadata = _build_metadata(version_data)

        return IngestedPackage(
            name=name,
            version=version,
            ecosystem=Ecosystem.NPM,
            source_dir=source_dir,
            metadata=metadata,
            _temp_dir=temp_dir,
        )


def _build_metadata(version_data: dict) -> dict:
    """Build normalized metadata from npm version data.

    Surfaces scripts.postinstall as a first-class field per Gnarl's
    architecture review — the Axios attack (scan #108) used this vector.
    """
    scripts = version_data.get("scripts", {})
    return {
        "description": version_data.get("description", ""),
        "maintainers": version_data.get("maintainers", []),
        "scripts": scripts,
        "postinstall": scripts.get("postinstall"),
        "preinstall": scripts.get("preinstall"),
        "install": scripts.get("install"),
        "dependencies": version_data.get("dependencies", {}),
        "devDependencies": version_data.get("devDependencies", {}),
        "dist": version_data.get("dist", {}),
    }


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
    # is_relative_to — not str.startswith — a sibling whose name shares dest's
    # prefix (e.g. dest='/tmp/abc', sibling='/tmp/abcde') would pass startswith.
    if not resolved.is_relative_to(dest.resolve()):
        raise PathTraversalError(f"Path traversal detected: {member_path}")
    return resolved


def _extract_npm_tarball(archive_bytes: bytes, dest: Path) -> None:
    """Extract an npm tarball with security checks."""
    total_extracted = 0

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


def _find_source_dir(dest: Path) -> Path:
    """Find the source dir. npm tarballs typically have a 'package/' prefix."""
    package_dir = dest / "package"
    if package_dir.is_dir():
        return package_dir
    entries = list(dest.iterdir())
    if len(entries) == 1 and entries[0].is_dir():
        return entries[0]
    return dest
