import importlib.util
import sys
from pathlib import Path

# Load mirror module dynamically
MODULE_PATH = Path(".cursor/hooks/mirror.py")
spec = importlib.util.spec_from_file_location("mirror", MODULE_PATH)
if spec and spec.loader:
    mirror = importlib.util.module_from_spec(spec)
    sys.modules["mirror_shell"] = mirror
    spec.loader.exec_module(mirror)
else:
    raise ImportError(f"Could not load mirror from {MODULE_PATH}")

from mirror_shell import (
    walk_sources, 
    scan, 
    ValidationConfig
)

def test_comprehensive_repo_scan():
    # Arrange
    config_path = Path(".cursor/extensions/arch_patterns.json")
    config = ValidationConfig.model_validate_json(config_path.read_text("utf-8"))
    
    fixture_root = Path("tests/fixtures/repo/src/domain")
    globs = [str(fixture_root / "**/*.py")]
    
    # Act
    sources = list(walk_sources(globs))
    violations = []
    for s in sources:
        violations.extend(scan(s, config.patterns))
        
    # Assert
    print("\nViolations Found:")
    for v in violations:
        print(f"- {v.rule_name} in {v.file_path.name}: {v.content}")

    # Expected:
    # 1. process.py -> Async
    # 2. gateway.py -> Import
    
    assert len(violations) == 2, f"Expected 2 violations, found {len(violations)}"
    
    violation_files = [v.file_path.name for v in violations]
    assert "process.py" in violation_files
    assert "gateway.py" in violation_files
    
    await_violation = next(v for v in violations if v.file_path.name == "process.py")
    assert "Async in Domain" in await_violation.rule_name
    
    import_violation = next(v for v in violations if v.file_path.name == "gateway.py")
    assert "External Dependency" in import_violation.rule_name
