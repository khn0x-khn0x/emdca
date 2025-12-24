"""
Tests for signal detection: SourceFile.scan().

Fixture files are named by the signal they should trigger.
No hardcoding — the filename IS the expected signal kind.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import mirror
from conftest import source_from_path


class TestSignalDetection:
    """SourceFile.scan() detects mechanical signals from AST."""

    def test_fixture_file_triggers_expected_signal(
        self, signal_fixture_paths: list[Path]
    ) -> None:
        """Each fixture file should trigger a signal matching its filename."""
        for fixture_path in signal_fixture_paths:
            # Filename (without .py) IS the expected signal kind
            expected_kind = mirror.SignalKind(fixture_path.stem)

            source = source_from_path(fixture_path)
            signals: tuple[Any, ...] = source.scan()

            detected_kinds = {s.kind for s in signals}
            assert expected_kind in detected_kinds, (
                f"Fixture {fixture_path.name} should trigger '{expected_kind}' signal.\n"
                f"Detected: {detected_kinds}"
            )

    def test_clean_files_trigger_no_signals(
        self, clean_fixture_paths: list[Path]
    ) -> None:
        """Clean EMDCA code should not trigger any signals."""
        for fixture_path in clean_fixture_paths:
            source = source_from_path(fixture_path)
            signals: tuple[Any, ...] = source.scan()

            assert signals == (), (
                f"Clean fixture {fixture_path.name} should trigger no signals.\n"
                f"Got: {[s.kind for s in signals]}"
            )

    def test_syntax_error_returns_empty_signals(self) -> None:
        """Invalid Python syntax should return empty, not crash."""
        source = mirror.SourceFile(
            path=Path("broken.py"),
            content="def broken(\n    this is not valid python",
        )
        signals: tuple[Any, ...] = source.scan()

        assert signals == ()


class TestSignalContent:
    """Signals contain accurate metadata about what was detected."""

    def test_signal_has_positive_line_number(
        self, signal_fixture_paths: list[Path]
    ) -> None:
        """All signals should have positive line numbers."""
        for fixture_path in signal_fixture_paths:
            source = source_from_path(fixture_path)
            signals: tuple[Any, ...] = source.scan()

            for signal in signals:
                assert signal.line > 0, f"Signal line must be positive: {signal}"

    def test_signal_content_is_from_source(
        self, signal_fixture_paths: list[Path]
    ) -> None:
        """Signal content should come from the actual source file."""
        for fixture_path in signal_fixture_paths:
            source = source_from_path(fixture_path)
            source_lines = source.content.splitlines()
            signals: tuple[Any, ...] = source.scan()

            for signal in signals:
                # Content should be a substring of the actual line (possibly truncated)
                actual_line = source_lines[signal.line - 1].strip()
                # Either exact match or truncated with "..."
                content_without_ellipsis = signal.content.removesuffix("...")
                assert signal.content in actual_line or actual_line.startswith(
                    content_without_ellipsis
                ), f"Signal content '{signal.content}' not in line '{actual_line}'"
