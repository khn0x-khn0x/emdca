"""
Tests for parsing boundaries: Foreign Reality → Domain.

Tests the factories that translate raw input into domain Sum Types.
"""

from __future__ import annotations

from pathlib import Path

import mirror
import pytest


class TestRawHookInputToDomain:
    """RawHookInput.to_domain() — the primary entry boundary."""

    def test_file_path_produces_file_edit_input(self) -> None:
        raw = mirror.RawHookInput(file_path=Path("/foo/bar.py"))
        result = raw.to_domain()

        match result:
            case mirror.FileEditInput(file_path=p):
                assert p == Path("/foo/bar.py")
            case _:
                pytest.fail(f"Expected FileEditInput, got {type(result).__name__}")

    def test_status_completed_produces_stop_input(self) -> None:
        raw = mirror.RawHookInput(status="completed")
        result = raw.to_domain()

        match result:
            case mirror.StopInput(status="completed"):
                pass
            case _:
                pytest.fail(
                    f"Expected StopInput(completed), got {type(result).__name__}"
                )

    def test_status_aborted_produces_stop_input(self) -> None:
        raw = mirror.RawHookInput(status="aborted")
        result = raw.to_domain()

        match result:
            case mirror.StopInput(status="aborted"):
                pass
            case _:
                pytest.fail(f"Expected StopInput(aborted), got {type(result).__name__}")

    def test_empty_produces_empty_input(self) -> None:
        raw = mirror.RawHookInput()
        result = raw.to_domain()

        match result:
            case mirror.EmptyInput():
                pass
            case _:
                pytest.fail(f"Expected EmptyInput, got {type(result).__name__}")


class TestRawRuleFrontmatterParseGlobs:
    """RawRuleFrontmatter.parse_globs() — extracts globs from YAML."""

    def test_valid_frontmatter_extracts_globs(self) -> None:
        content = """---
globs: ["domain/**/*.py", "src/**/*.py"]
---
# Rule content
"""
        raw = mirror.RawRuleFrontmatter(content=content)
        result = raw.parse_globs()

        match result:
            case mirror.GlobsParsed(globs=g):
                assert "domain/**/*.py" in g
                assert "src/**/*.py" in g
            case _:
                pytest.fail(f"Expected GlobsParsed, got {type(result).__name__}")

    def test_no_frontmatter_returns_not_found(self) -> None:
        content = "# Just markdown, no frontmatter"
        raw = mirror.RawRuleFrontmatter(content=content)
        result = raw.parse_globs()

        match result:
            case mirror.GlobsNotFound():
                pass
            case _:
                pytest.fail(f"Expected GlobsNotFound, got {type(result).__name__}")

    def test_frontmatter_without_globs_returns_not_found(self) -> None:
        content = """---
title: Some Rule
---
# Content
"""
        raw = mirror.RawRuleFrontmatter(content=content)
        result = raw.parse_globs()

        match result:
            case mirror.GlobsNotFound():
                pass
            case _:
                pytest.fail(f"Expected GlobsNotFound, got {type(result).__name__}")
