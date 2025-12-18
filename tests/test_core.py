import ast
import importlib.util
import sys
from pathlib import Path
import re

# Dynamically load the mirror module from the hidden .cursor directory
# This allows us to test the script without moving it or making it a package.
MODULE_PATH = Path(".cursor/hooks/mirror.py")
spec = importlib.util.spec_from_file_location("mirror", MODULE_PATH)
if spec and spec.loader:
    mirror = importlib.util.module_from_spec(spec)
    sys.modules["mirror"] = mirror
    spec.loader.exec_module(mirror)
else:
    raise ImportError(f"Could not load mirror from {MODULE_PATH}")

from mirror import (
    RuleKind,
    SourceFile,
    ValidationRule,
    Violation,
    RuleId,
    RuleName,
    ValidationMessage,
    scan,
)

# --- Factories (Pattern 01) ---

def create_rule(
    kind: RuleKind,
    pattern: str = ".*",
    id: str = "test_rule",
    name: str = "Test Rule",
    message: str = "Violation"
) -> ValidationRule:
    return ValidationRule(
        id=RuleId(id),
        name=RuleName(name),
        kind=kind,
        pattern=pattern,
        message=ValidationMessage(message)
    )

def create_source(content: str, path: str = "test.py") -> SourceFile:
    return SourceFile(path=Path(path), content=content)

# --- Tests ---

def test_detects_banned_import():
    # Arrange
    rule = create_rule(kind=RuleKind.RESTRICTED_IMPORT, pattern="^(pydantic|domain)")
    source = create_source("import boto3\nimport pydantic")
    
    # Act
    violations = list(scan(source, [rule]))
    
    # Assert
    assert len(violations) == 1
    assert violations[0].content == "import boto3"
    assert violations[0].line_number == 1

def test_allows_valid_import():
    # Arrange
    rule = create_rule(kind=RuleKind.RESTRICTED_IMPORT, pattern="^(pydantic|domain)")
    source = create_source("from domain.entity import Entity")
    
    # Act
    violations = list(scan(source, [rule]))
    
    # Assert
    assert len(violations) == 0

def test_detects_class_name():
    # Arrange
    rule = create_rule(kind=RuleKind.CLASS_NAME, pattern=".*Manager$")
    source = create_source("class UserManager:\n    pass")
    
    # Act
    violations = list(scan(source, [rule]))
    
    # Assert
    assert len(violations) == 1
    assert violations[0].content == "class UserManager:"

def test_detects_raise():
    # Arrange
    rule = create_rule(kind=RuleKind.NODE_USAGE, pattern="Raise")
    source = create_source("def func():\n    raise ValueError()")
    
    # Act
    violations = list(scan(source, [rule]))
    
    # Assert
    assert len(violations) == 1
    assert "raise ValueError()" in violations[0].content

def test_detects_await():
    # Arrange
    rule = create_rule(kind=RuleKind.NODE_USAGE, pattern="Await")
    source = create_source("async def func():\n    await foo()")
    
    # Act
    violations = list(scan(source, [rule]))
    
    # Assert
    assert len(violations) == 1
    assert "await foo()" in violations[0].content

def test_detects_boolean_flag():
    # Arrange
    rule = create_rule(kind=RuleKind.ATTRIBUTE_NAME, pattern="^is_.*")
    source = create_source("class User:\n    is_active: bool")
    
    # Act
    violations = list(scan(source, [rule]))
    
    # Assert
    assert len(violations) == 1
    assert "is_active: bool" in violations[0].content
