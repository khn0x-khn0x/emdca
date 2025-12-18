"""
The Architect's Mirror.

This script acts as a static analysis engine to enforce 'Explicitly Modeled Data-Centric Architecture' (EMDCA).
It runs as a Cursor Hook, analyzing code structure (AST) against a set of architectural rules defined in
`extensions/arch_patterns.json`.

Architecture:
    The script itself adheres to EMDCA principles:
    - **Pure Core**: All validation logic resides in pure functions and immutable Pydantic models.
    - **Shell**: The `main` function handles I/O, configuration loading, and orchestration.
    - **Capability as Data**: Validation rules are defined as external data, not hardcoded conditional logic.
    - **Parse, Don't Validate**: Inputs are parsed into strong types (`HookInput`, `ValidationConfig`) at the boundary.
"""

import ast
import json
import re
import sys
from collections.abc import Iterator
from enum import Enum
from itertools import chain, islice
from pathlib import Path
from typing import NewType

from pydantic import BaseModel, Field, ValidationError, field_validator

# --- 0. Primitives (Value Objects) ---
# We use NewType to create distinct types for string primitives, ensuring semantic clarity
# and preventing accidental swapping of arguments (Pattern 01: Explicit Construction).

RuleId = NewType("RuleId", str)
RuleName = NewType("RuleName", str)
ValidationMessage = NewType("ValidationMessage", str)
SourceLine = NewType("SourceLine", str)


# --- 1. Domain Models (Internal Truth) ---


class RuleKind(str, Enum):
    """Categorizes the type of AST pattern to match."""

    IMPORT = "import"
    NODE_USAGE = "node_usage"
    CLASS_NAME = "class_name"
    FUNCTION_NAME = "function_name"
    TYPE_ANNOTATION = "type_annotation"
    ATTRIBUTE_NAME = "attribute_name"
    ATTRIBUTE_DEFAULT = "attribute_default"
    RESTRICTED_IMPORT = "restricted_import"


class SourceFile(BaseModel):
    """
    Represents a snapshot of a source file's content.

    This is an immutable Value Object. It decouples the analysis logic from the filesystem.
    """

    model_config = {"frozen": True}
    path: Path
    content: str

    def get_line(self, line_no: int) -> SourceLine:
        """Safely extracts a specific line from the source content."""
        lines = self.content.splitlines()
        if 1 <= line_no <= len(lines):
            line = lines[line_no - 1].strip()
            # Truncate long lines for display
            return SourceLine(line[:77] + "..." if len(line) > 80 else line)
        return SourceLine("...")


class Violation(BaseModel):
    """
    Represents a detected architectural violation.

    This is a Specification Object (Pattern 04) that contains all data required
    to report the issue to the user.
    """

    model_config = {"frozen": True}
    rule_id: RuleId
    rule_name: RuleName
    file_path: Path
    line_number: int
    content: SourceLine
    context_message: ValidationMessage


class ValidationRule(BaseModel):
    """
    Defines a single architectural constraint.

    This model adheres to Pattern 10 (Infrastructure as Data): the capability to validate
    code is defined as data, and this model owns the logic (`check`) to interpret that data.
    """

    model_config = {"frozen": True}
    id: RuleId
    name: RuleName
    kind: RuleKind
    pattern: str
    message: ValidationMessage

    @field_validator("pattern")
    @classmethod
    def validate_pattern_is_regex(cls, v: str) -> str:
        """Ensures the pattern string is a valid regular expression at construction time."""
        try:
            re.compile(v)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern '{v}': {e}") from e
        return v

    def check(self, node: ast.AST, source: SourceFile) -> Violation | None:
        """
        Pure function evaluating this rule against a specific AST node.

        Returns:
            Violation: If the node violates the rule.
            None: If the node complies or is irrelevant.
        """
        if not self._matches(node):
            return None

        # Safe extraction of line number.
        # Most AST nodes of interest (stmt, expr) have a lineno attribute.
        # We default to 0 for nodes without position info (unlikely in this context).
        line = node.lineno if isinstance(node, (ast.stmt, ast.expr, ast.arg)) else 0

        return Violation(
            rule_id=self.id,
            rule_name=self.name,
            file_path=source.path,
            line_number=line,
            content=source.get_line(line),
            context_message=self.message,
        )

    def _matches(self, node: ast.AST) -> bool:
        """Internal logic to match the AST node against the rule's pattern."""
        match (self.kind, node):
            case (RuleKind.IMPORT, ast.Import(names=names)):
                return any(re.search(self.pattern, n.name) is not None for n in names)

            case (RuleKind.IMPORT, ast.ImportFrom(module=m)):
                return bool(m and re.search(self.pattern, m))

            case (RuleKind.RESTRICTED_IMPORT, ast.Import(names=names)):
                return any(self._is_restricted(n.name) for n in names)

            case (RuleKind.RESTRICTED_IMPORT, ast.ImportFrom(module=m, level=level)):
                # Relative imports (level > 0) are always internal/safe
                if level > 0:
                    return False
                return bool(m and self._is_restricted(m))

            case (RuleKind.CLASS_NAME, ast.ClassDef(name=n)):
                return re.search(self.pattern, n) is not None

            case (RuleKind.FUNCTION_NAME, ast.FunctionDef(name=n)):
                return re.search(self.pattern, n) is not None

            case (RuleKind.NODE_USAGE, node):
                # Generic check for node type usage (e.g. "Try", "Raise", "Await")
                return node.__class__.__name__ == self.pattern

            case (RuleKind.TYPE_ANNOTATION, ast.AnnAssign(annotation=ast.Name(id=t))):
                return re.search(self.pattern, t) is not None

            case (RuleKind.ATTRIBUTE_NAME, ast.AnnAssign(target=ast.Name(id=n))):
                return re.search(self.pattern, n) is not None

            case (RuleKind.ATTRIBUTE_DEFAULT, ast.AnnAssign(value=v)) if v:
                return not self._is_safe(v)

            case _:
                return False

    def _is_safe(self, node: ast.expr) -> bool:
        """Determines if a default value is architecturally safe (None or Field)."""
        match node:
            case ast.Constant(value=None) | ast.Call(func=ast.Name(id="Field")):
                return True
            case _:
                return False

    def _is_restricted(self, name: str) -> bool:
        """
        Determines if an import violates the whitelist policy.

        Returns True if the import is restricted (i.e., NOT in stdlib AND NOT in whitelist).
        """
        # Allow relative imports (e.g. 'from .entity import X')
        if name.startswith("."):
            return False

        root_module = name.split(".")[0]
        if root_module in sys.stdlib_module_names:
            return False

        # Check against allowed pattern (Whitelist) using match() for start-anchoring
        if self.pattern and re.match(self.pattern, name):
            return False

        return True


class ValidationSettings(BaseModel):
    model_config = {"frozen": True}
    # Pattern 10: Capability as Data (Flexible Globs)
    target_globs: list[str] = ["src/domain/**/*.py"]
    max_display: int = 10


class ValidationConfig(BaseModel):
    """
    Root configuration object representing the policy loaded from `arch_patterns.json`.
    """

    model_config = {"frozen": True}
    settings: ValidationSettings = Field(default_factory=ValidationSettings)
    patterns: list[ValidationRule]


class HookInput(BaseModel):
    """
    Models the raw input payload received from the IDE Hook.

    This represents the 'Foreign Reality' (Pattern 07) that must be parsed
    into our internal Domain structures.
    """

    file_path: Path | None = None
    status: str | None = None  # "completed" | "aborted" | "error"


# --- 2. Pure Logic Pipeline ---


def scan(source: SourceFile, rules: list[ValidationRule]) -> Iterator[Violation]:
    """
    Scans a single source file against all validation rules.

    This is a pure generator that yields violations lazily.
    """
    try:
        tree = ast.parse(source.content)
    except SyntaxError:
        # Syntax errors are common during editing; we ignore them here as this tool
        # focuses on architectural structure, not syntax validation.
        return

    for node in ast.walk(tree):
        for rule in rules:
            if violation := rule.check(node, source):
                yield violation


def format_report(violations: list[Violation], limit: int) -> str | None:
    """
    Formats the list of violations into a human-readable message for the Agent.
    """
    if not violations:
        return None

    lines = [
        f"- [{v.rule_name}] {v.file_path}:{v.line_number} -> `{v.content}`\n  "
        f"Context: {v.context_message}"
        for v in violations[:limit]
    ]
    if len(violations) > limit:
        lines.append(f"\n...and {len(violations) - limit} more potential issues.")

    return (
        "ARCHITECTURAL REVIEW REQUIRED\n\n"
        "The following patterns were detected in the Domain Layer. "
        "These often indicate violations of the EMDCA Spec.\n\n"
        + "\n".join(lines)
        + "\n\n"
        "TASK: Review these lines. IGNORE false positives. REFACTOR violations."
    )


def walk_sources(globs: list[str]) -> Iterator[SourceFile]:
    """
    Generates SourceFile objects from the filesystem matching the provided globs.

    This is the I/O boundary for batch processing.
    """
    root = Path(".")

    # Iterate over all glob patterns
    for pattern in globs:
        # Use glob() to find files matching the pattern
        for path in root.glob(pattern):
            if not path.is_file():
                continue

            try:
                # Explicitly fail if we can't read a file we expect to read (Pattern 03)
                yield SourceFile(path=path, content=path.read_text("utf-8"))
            except (OSError, UnicodeDecodeError):
                # If we can't read it (e.g. binary), skip it.
                # Crashing the whole hook for one bad file in a batch scan is too aggressive.
                continue


# --- 3. Shell (Orchestration) ---


def main() -> None:
    """
    Entry point for the hook. Handles I/O, configuration loading, and pipeline orchestration.
    """
    # 1. IO: Input
    # We attempt to parse stdin to determine if this is a triggered hook event.
    input_data = HookInput()
    if not sys.stdin.isatty():
        content = sys.stdin.read()
        if content.strip():
            try:
                input_data = HookInput.model_validate_json(content)
            except ValidationError:
                pass

    # 2. IO: Config
    # Load the architectural policy. Fail loudly if config is broken.
    config_path = Path(__file__).parent / "../extensions/arch_patterns.json"
    json_content: str = config_path.read_text("utf-8")
    config = ValidationConfig.model_validate_json(json_content)

    # 3. Scope: Batch vs Real-time
    # Determine the scope of analysis based on the input trigger.

    # Safety Valve: If the user aborted the Agent, do not trigger a loop.
    if input_data.status == "aborted":
        print(json.dumps({}))
        return

    target_globs = config.settings.target_globs
    sources: Iterator[SourceFile]

    if input_data.file_path:
        # incremental mode (afterFileEdit): Check only the changed file
        path = input_data.file_path

        # Check if the file matches ANY of the target globs
        # We try to match relative to CWD for glob correctness
        try:
            rel_path = path.relative_to(Path.cwd())
        except ValueError:
            # Path is not relative to CWD (e.g. /tmp/...), try absolute match or skip
            rel_path = path

        # Use pathlib.match for glob checking
        is_included = any(rel_path.match(g) for g in target_globs)

        if is_included and path.exists():
            try:
                sources = iter([SourceFile(path=path, content=path.read_text("utf-8"))])
            except (OSError, UnicodeDecodeError):
                sources = iter([])
        else:
            sources = iter([])
    else:
        # batch mode (stop): Check everything matching globs
        sources = walk_sources(target_globs)

    # 4. Pipeline: Scan -> Filter -> Limit
    # Lazy evaluation ensures O(1) memory usage regardless of codebase size.
    violations = chain.from_iterable(scan(s, config.patterns) for s in sources)

    limit = config.settings.max_display
    top_violations = list(islice(violations, limit + 1))

    # 5. Output
    # Emit the report if violations are found.
    # We use agent_message to inject context into the Agent's loop without forcing a restart.
    if report := format_report(top_violations, limit):
        print(
            json.dumps(
                {
                    "agent_message": report,
                    "user_message": "Architect's Mirror: Violations Detected (See Agent Context)",
                }
            )
        )
    else:
        print(json.dumps({}))


if __name__ == "__main__":
    main()
