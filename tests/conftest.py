"""
Test configuration — loads real objects from the actual codebase.

No mocks. No hardcoding. Single source of truth.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

# =============================================================================
# Load mirror module from .cursor/hooks/
# =============================================================================

REPO_ROOT = Path(__file__).parent.parent
MODULE_PATH = REPO_ROOT / ".cursor" / "hooks" / "mirror.py"

spec = importlib.util.spec_from_file_location("mirror", MODULE_PATH)
if not spec or not spec.loader:
    raise ImportError(f"Could not load mirror from {MODULE_PATH}")

mirror = importlib.util.module_from_spec(spec)
sys.modules["mirror"] = mirror
spec.loader.exec_module(mirror)

# Re-export for type checking and tests
if TYPE_CHECKING:
    from mirror import SourceFile


# =============================================================================
# Fixtures — Real objects from actual codebase
# =============================================================================


@pytest.fixture(scope="session")
def repo_root() -> Path:
    """Root of the repository."""
    return REPO_ROOT


@pytest.fixture(scope="session")
def rules_dir(repo_root: Path) -> Path:
    """Path to .cursor/rules/."""
    return repo_root / ".cursor" / "rules"


@pytest.fixture(scope="session")
def all_rules() -> tuple[Any, ...]:
    """All rules loaded from .cursor/rules/ — the real ones."""
    result: tuple[Any, ...] = mirror.discover_rules()
    return result


@pytest.fixture(scope="session")
def signal_fixtures_dir(repo_root: Path) -> Path:
    """Directory containing signal fixture files."""
    return repo_root / "tests" / "fixtures" / "signals"


@pytest.fixture(scope="session")
def clean_fixtures_dir(repo_root: Path) -> Path:
    """Directory containing clean fixture files."""
    return repo_root / "tests" / "fixtures" / "clean"


@pytest.fixture(scope="session")
def signal_fixture_paths(signal_fixtures_dir: Path) -> list[Path]:
    """All .py files in fixtures/signals/."""
    return sorted(signal_fixtures_dir.glob("*.py"))


@pytest.fixture(scope="session")
def clean_fixture_paths(clean_fixtures_dir: Path) -> list[Path]:
    """All .py files in fixtures/clean/."""
    return sorted(clean_fixtures_dir.glob("*.py"))


# =============================================================================
# Factory functions — Create real domain objects
# =============================================================================


def source_from_path(path: Path) -> SourceFile:
    """Create a SourceFile from a real file."""
    return mirror.SourceFile(path=path, content=path.read_text("utf-8"))


def source_from_content(content: str, path: str = "test.py") -> SourceFile:
    """Create a SourceFile from inline content."""
    return mirror.SourceFile(path=Path(path), content=content)
