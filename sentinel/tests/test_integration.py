"""Integration tests that hit live registries.

These tests require network access. Mark with pytest.mark.integration
so they can be skipped in CI with: pytest -m "not integration"
"""

from __future__ import annotations

import pytest

from sentinel.ingester import PackageNotFoundError, get_ingester
from sentinel.models import Ecosystem


pytestmark = pytest.mark.integration


class TestPyPIIntegration:
    @pytest.fixture
    def ingester(self):
        return get_ingester(Ecosystem.PYPI)

    async def test_fetch_metadata(self, ingester):
        meta = await ingester.fetch_metadata("six")
        assert meta["info"]["name"] == "six"

    async def test_resolve_latest_version(self, ingester):
        version = await ingester.resolve_latest_version("six")
        assert version  # non-empty string

    async def test_list_versions(self, ingester):
        versions = await ingester.list_versions("six")
        assert len(versions) > 10
        assert "1.16.0" in versions

    async def test_ingest(self, ingester):
        with await ingester.ingest("six", "1.16.0") as pkg:
            assert pkg.name == "six"
            assert pkg.version == "1.16.0"
            assert pkg.ecosystem == Ecosystem.PYPI
            assert pkg.source_dir.exists()
            py_files = pkg.source_files(extensions={".py"})
            assert len(py_files) > 0

    async def test_not_found(self, ingester):
        with pytest.raises(PackageNotFoundError):
            await ingester.fetch_metadata("this-package-definitely-does-not-exist-xyz-123")


class TestNpmIntegration:
    @pytest.fixture
    def ingester(self):
        return get_ingester(Ecosystem.NPM)

    async def test_fetch_metadata(self, ingester):
        meta = await ingester.fetch_metadata("is-odd")
        assert "versions" in meta

    async def test_resolve_latest_version(self, ingester):
        version = await ingester.resolve_latest_version("is-odd")
        assert version

    async def test_list_versions(self, ingester):
        versions = await ingester.list_versions("is-odd")
        assert len(versions) > 0

    async def test_ingest(self, ingester):
        with await ingester.ingest("is-odd", "3.0.1") as pkg:
            assert pkg.name == "is-odd"
            assert pkg.version == "3.0.1"
            assert pkg.ecosystem == Ecosystem.NPM
            assert pkg.source_dir.exists()
            js_files = pkg.source_files(extensions={".js"})
            assert len(js_files) > 0

    async def test_scoped_package(self, ingester):
        """Test that scoped packages (@scope/name) work."""
        meta = await ingester.fetch_metadata("@anthropic-ai/sdk")
        assert "versions" in meta

    async def test_postinstall_in_metadata(self, ingester):
        """Verify postinstall is surfaced as first-class field."""
        with await ingester.ingest("is-odd", "3.0.1") as pkg:
            # is-odd may or may not have postinstall, but the field must exist
            assert "postinstall" in pkg.metadata

    async def test_not_found(self, ingester):
        with pytest.raises(PackageNotFoundError):
            await ingester.fetch_metadata("this-npm-package-definitely-does-not-exist-xyz-123")
