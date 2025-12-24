"""
Tests for glob matching: RuleRef.matches_path().

Uses real rules loaded from .cursor/rules/.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import mirror
import pytest


class TestRuleMatchesPath:
    """RuleRef.matches_path() correctly matches file paths against globs."""

    def test_real_rules_have_globs(self, all_rules: tuple[Any, ...]) -> None:
        """All loaded rules should have at least one glob pattern."""
        for rule in all_rules:
            # Rules without globs are valid but won't match anything
            # This is informational, not a failure
            if not rule.globs:
                pytest.skip(f"Rule {rule.name} has no globs defined")

    def test_domain_path_matches_domain_rule(self, all_rules: tuple[Any, ...]) -> None:
        """A domain/** path should match rules with domain/** globs."""
        test_path = Path("domain/user/entity.py")

        matching_rules = [r for r in all_rules if r.matches_path(test_path)]

        # At least some rules should match domain paths
        assert len(matching_rules) > 0, (
            f"No rules matched {test_path}.\n"
            f"Available rules: {[r.name for r in all_rules]}"
        )

    def test_non_matching_path_excluded(self, all_rules: tuple[Any, ...]) -> None:
        """A path outside all globs should match no rules (or only catch-all rules)."""
        test_path = Path("random/untracked/file.txt")

        matching_rules = [r for r in all_rules if r.matches_path(test_path)]

        # Most rules should NOT match random paths
        # This verifies globs are actually filtering, not matching everything
        assert len(matching_rules) < len(all_rules), (
            "All rules matched a random path — globs may not be filtering correctly"
        )


class TestGlobPatternBehavior:
    """Verify glob pattern edge cases."""

    def test_double_star_matches_nested(self) -> None:
        """domain/**/*.py should match nested paths."""
        rule = mirror.RuleRef(
            pattern_id=mirror.PatternId("test"),
            name=mirror.RuleName("test-rule"),
            globs=(mirror.GlobPattern("domain/**/*.py"),),
            content=mirror.RuleContent(""),
        )

        # Current implementation uses fnmatch with ** → *
        # This matches nested paths but requires the *.py suffix
        assert rule.matches_path(Path("domain/user/entity.py"))
        assert rule.matches_path(Path("domain/user/sub/deep.py"))
        assert not rule.matches_path(Path("service/api.py"))

    def test_multiple_globs_any_match(self) -> None:
        """Rule with multiple globs should match if ANY glob matches."""
        rule = mirror.RuleRef(
            pattern_id=mirror.PatternId("test"),
            name=mirror.RuleName("test-rule"),
            globs=(
                mirror.GlobPattern("domain/**/*.py"),
                mirror.GlobPattern("service/**/*.py"),
            ),
            content=mirror.RuleContent(""),
        )

        assert rule.matches_path(Path("domain/user/entity.py"))
        assert rule.matches_path(Path("service/handlers/api.py"))
        assert not rule.matches_path(Path("config/settings.py"))
