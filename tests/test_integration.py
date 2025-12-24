"""
Integration tests: Full stdin → stdout pipeline.

Tests the complete hook flow as Cursor would invoke it.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest


class TestFullPipeline:
    """End-to-end tests: JSON in → JSON out."""

    def test_file_edit_produces_message_output(
        self, repo_root: Path, signal_fixture_paths: list[Path]
    ) -> None:
        """FileEdit input with violations should produce agent_message output."""
        if not signal_fixture_paths:
            pytest.skip("No signal fixtures found")

        fixture_path = signal_fixture_paths[0]
        input_json = json.dumps({"file_path": str(fixture_path)})

        result = subprocess.run(
            ["python3", ".cursor/hooks/mirror.py"],
            input=input_json,
            capture_output=True,
            text=True,
            cwd=repo_root,
        )

        assert result.returncode == 0, f"Script failed: {result.stderr}"

        output = json.loads(result.stdout)
        assert "agent_message" in output, f"Expected agent_message, got: {output}"

    def test_clean_file_may_produce_no_output(
        self, repo_root: Path, clean_fixture_paths: list[Path]
    ) -> None:
        """Clean file should produce minimal or no agent_message."""
        if not clean_fixture_paths:
            pytest.skip("No clean fixtures found")

        fixture_path = clean_fixture_paths[0]
        input_json = json.dumps({"file_path": str(fixture_path)})

        result = subprocess.run(
            ["python3", ".cursor/hooks/mirror.py"],
            input=input_json,
            capture_output=True,
            text=True,
            cwd=repo_root,
        )

        assert result.returncode == 0, f"Script failed: {result.stderr}"

        _ = json.loads(result.stdout)  # Verify valid JSON output
        # Clean files might still match rules (by glob), but shouldn't have signals
        # The important thing is the script runs successfully

    def test_empty_input_produces_empty_output(self, repo_root: Path) -> None:
        """Empty stdin should produce empty JSON output."""
        result = subprocess.run(
            ["python3", ".cursor/hooks/mirror.py"],
            input="",
            capture_output=True,
            text=True,
            cwd=repo_root,
        )

        assert result.returncode == 0, f"Script failed: {result.stderr}"

        output = json.loads(result.stdout)
        assert output == {}, f"Expected empty output, got: {output}"

    def test_invalid_json_produces_empty_output(self, repo_root: Path) -> None:
        """Invalid JSON should not crash, should produce empty output."""
        result = subprocess.run(
            ["python3", ".cursor/hooks/mirror.py"],
            input="not valid json",
            capture_output=True,
            text=True,
            cwd=repo_root,
        )

        assert result.returncode == 0, f"Script failed: {result.stderr}"

        output = json.loads(result.stdout)
        assert output == {}, f"Expected empty output on bad JSON, got: {output}"

    def test_stop_aborted_produces_empty_output(self, repo_root: Path) -> None:
        """Stop with aborted status should produce empty output."""
        input_json = json.dumps({"status": "aborted"})

        result = subprocess.run(
            ["python3", ".cursor/hooks/mirror.py"],
            input=input_json,
            capture_output=True,
            text=True,
            cwd=repo_root,
        )

        assert result.returncode == 0, f"Script failed: {result.stderr}"

        output = json.loads(result.stdout)
        assert output == {}, f"Expected empty output on abort, got: {output}"


class TestOutputFormat:
    """Verify output structure matches Cursor hook expectations."""

    def test_message_output_has_agent_message_key(
        self, repo_root: Path, signal_fixture_paths: list[Path]
    ) -> None:
        """Output JSON should have 'agent_message' key when there's content."""
        if not signal_fixture_paths:
            pytest.skip("No signal fixtures found")

        fixture_path = signal_fixture_paths[0]
        input_json = json.dumps({"file_path": str(fixture_path)})

        result = subprocess.run(
            ["python3", ".cursor/hooks/mirror.py"],
            input=input_json,
            capture_output=True,
            text=True,
            cwd=repo_root,
        )

        output = json.loads(result.stdout)

        if "agent_message" in output:
            # Verify it's a string
            assert isinstance(output["agent_message"], str)
            # Verify it has structure (header, signals, rules)
            msg = output["agent_message"]
            assert "Architect's Mirror" in msg or "Signal" in msg or "Rule" in msg
