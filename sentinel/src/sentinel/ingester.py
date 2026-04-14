"""Abstract base for package ingesters."""

from __future__ import annotations

from abc import ABC, abstractmethod

from sentinel.models import Ecosystem, IngestedPackage

# Limits
MAX_DOWNLOAD_BYTES = 100 * 1024 * 1024  # 100 MB
MAX_EXTRACTED_BYTES = 500 * 1024 * 1024  # 500 MB
HTTP_TIMEOUT_SECONDS = 30


class IngesterError(Exception):
    """Base error for ingester operations."""


class PackageNotFoundError(IngesterError):
    """Package or version not found in the registry."""


class DownloadTooLargeError(IngesterError):
    """Download exceeds the size limit."""


class ExtractionTooLargeError(IngesterError):
    """Extracted content exceeds the decompressed size limit."""


class PathTraversalError(IngesterError):
    """Archive member attempts path traversal outside destination."""


class PackageIngester(ABC):
    """Abstract base class for ecosystem-specific package ingesters."""

    ecosystem: Ecosystem

    @abstractmethod
    async def fetch_metadata(self, name: str, version: str | None = None) -> dict:
        """Fetch package metadata from the registry.

        Args:
            name: Package name.
            version: Specific version, or None for latest.

        Returns:
            Registry-specific metadata dict.

        Raises:
            PackageNotFoundError: If the package or version doesn't exist.
        """

    @abstractmethod
    async def ingest(self, name: str, version: str | None = None) -> IngestedPackage:
        """Download and unpack a package for analysis.

        Args:
            name: Package name.
            version: Specific version, or None for latest.

        Returns:
            IngestedPackage with unpacked source files in a temp directory.

        Raises:
            PackageNotFoundError: If the package or version doesn't exist.
            DownloadTooLargeError: If the download exceeds the size limit.
            ExtractionTooLargeError: If extracted content exceeds the limit.
            PathTraversalError: If the archive contains path traversal attempts.
        """

    @abstractmethod
    async def resolve_latest_version(self, name: str) -> str:
        """Resolve the latest version string for a package.

        Args:
            name: Package name.

        Returns:
            Latest version string.

        Raises:
            PackageNotFoundError: If the package doesn't exist.
        """

    @abstractmethod
    async def list_versions(self, name: str) -> list[str]:
        """List all available versions for a package.

        Args:
            name: Package name.

        Returns:
            List of version strings.

        Raises:
            PackageNotFoundError: If the package doesn't exist.
        """


def get_ingester(ecosystem: Ecosystem) -> PackageIngester:
    """Get the appropriate ingester for an ecosystem.

    Args:
        ecosystem: The package ecosystem.

    Returns:
        A PackageIngester instance for the given ecosystem.
    """
    from sentinel.pypi import PyPIIngester
    from sentinel.npm import NpmIngester

    ingesters = {
        Ecosystem.PYPI: PyPIIngester,
        Ecosystem.NPM: NpmIngester,
    }

    ingester_cls = ingesters.get(ecosystem)
    if ingester_cls is None:
        raise ValueError(f"Unsupported ecosystem: {ecosystem}")

    return ingester_cls()
