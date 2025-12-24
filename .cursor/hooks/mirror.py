"""
The Architect's Mirror

A hook script that combines deterministic signals (AST) with non-deterministic judgment (LLM).
Pure EMDCA: All logic is methods on frozen Pydantic models. I/O only at shell edges.

Architecture:
    1. Shell: Read stdin, read files, write stdout
    2. Domain: Frozen models with methods that transform data
    3. Sum Types: Explicit states for all results
"""

from __future__ import annotations

import ast
import fnmatch
import json
import re
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Literal, NewType

from pydantic import BaseModel, PositiveInt

# =============================================================================
# 0. PRIMITIVES (Value Objects via NewType)
# =============================================================================

PatternId = NewType("PatternId", str)
SignalKind = NewType("SignalKind", str)
RuleName = NewType("RuleName", str)
SourceLine = NewType("SourceLine", str)
SignalHint = NewType("SignalHint", str)
GlobPattern = NewType("GlobPattern", str)
RuleContent = NewType("RuleContent", str)


# =============================================================================
# 1. DOMAIN MODELS — Sum Types for Input
# =============================================================================


class FileEditInput(BaseModel):
    """Hook input when a file was edited."""

    model_config = {"frozen": True}
    kind: Literal["file_edit"]
    file_path: Path


class StopInput(BaseModel):
    """Hook input when agent loop stopped."""

    model_config = {"frozen": True}
    kind: Literal["stop"]
    status: Literal["completed", "aborted", "error"]


class EmptyInput(BaseModel):
    """Hook input with no actionable data."""

    model_config = {"frozen": True}
    kind: Literal["empty"]


type HookInput = FileEditInput | StopInput | EmptyInput


# =============================================================================
# 2. DOMAIN MODELS — Sum Types for Output
# =============================================================================


class MessageOutput(BaseModel):
    """Hook output with agent message."""

    model_config = {"frozen": True}
    kind: Literal["message"]
    agent_message: str

    def to_json(self) -> str:
        return json.dumps({"agent_message": self.agent_message})


class NoOutput(BaseModel):
    """Hook output with nothing to emit."""

    model_config = {"frozen": True}
    kind: Literal["no_output"]

    def to_json(self) -> str:
        return json.dumps({})


type HookOutput = MessageOutput | NoOutput


# =============================================================================
# 3. DOMAIN MODELS — Sum Types for Internal Results
# =============================================================================


class GlobsParsed(BaseModel):
    """Successfully parsed globs from rule frontmatter."""

    model_config = {"frozen": True}
    kind: Literal["parsed"]
    globs: tuple[GlobPattern, ...]


class GlobsNotFound(BaseModel):
    """Could not parse globs from rule."""

    model_config = {"frozen": True}
    kind: Literal["not_found"]


type GlobsResult = GlobsParsed | GlobsNotFound


class ContentLoaded(BaseModel):
    """Successfully loaded content."""

    model_config = {"frozen": True}
    kind: Literal["loaded"]
    content: str


class ContentUnreadable(BaseModel):
    """Could not read content."""

    model_config = {"frozen": True}
    kind: Literal["unreadable"]
    path: Path


type ContentResult = ContentLoaded | ContentUnreadable


# =============================================================================
# 4. DOMAIN MODELS — Configuration (Capability as Data)
# =============================================================================


class SignalPattern(BaseModel):
    """Definition of what AST pattern to detect and which rule it maps to."""

    model_config = {"frozen": True}
    kind: SignalKind
    pattern_id: PatternId
    hint: SignalHint


# All signal patterns we detect
SIGNAL_PATTERNS: tuple[SignalPattern, ...] = (
    # Pattern 01: Factory Construction
    SignalPattern(
        kind=SignalKind("validate_function"),
        pattern_id=PatternId("01"),
        hint=SignalHint("validate_* functions — use Factory pattern"),
    ),
    SignalPattern(
        kind=SignalKind("primitive_type"),
        pattern_id=PatternId("01"),
        hint=SignalHint("Primitive type — consider Value Object"),
    ),
    SignalPattern(
        kind=SignalKind("field_default"),
        pattern_id=PatternId("01"),
        hint=SignalHint("Default value — explicit construction required"),
    ),
    # Pattern 02: State Sum Types
    SignalPattern(
        kind=SignalKind("boolean_flag"),
        pattern_id=PatternId("02"),
        hint=SignalHint("is_* boolean flag — use Sum Types instead"),
    ),
    # Pattern 03: Railway Control Flow
    SignalPattern(
        kind=SignalKind("try_block"),
        pattern_id=PatternId("03"),
        hint=SignalHint("try/except — use Result types instead"),
    ),
    SignalPattern(
        kind=SignalKind("raise_stmt"),
        pattern_id=PatternId("03"),
        hint=SignalHint("raise — return Failure types instead"),
    ),
    # Pattern 04: Execution Intent
    SignalPattern(
        kind=SignalKind("await_expr"),
        pattern_id=PatternId("04"),
        hint=SignalHint("await in domain — async belongs in Shell"),
    ),
    SignalPattern(
        kind=SignalKind("service_class"),
        pattern_id=PatternId("04"),
        hint=SignalHint("*Service/*Manager class — use Intent objects"),
    ),
)


# =============================================================================
# 5. DOMAIN MODELS — Core Entities
# =============================================================================


class Signal(BaseModel):
    """A mechanical signal detected by AST scan. A fact, not a verdict."""

    model_config = {"frozen": True}
    kind: SignalKind
    pattern_id: PatternId
    line: PositiveInt
    content: SourceLine
    hint: SignalHint


class RuleRef(BaseModel):
    """Reference to a pattern rule with its content."""

    model_config = {"frozen": True}
    pattern_id: PatternId
    name: RuleName
    globs: tuple[GlobPattern, ...]
    content: RuleContent

    def matches_path(self, file_path: Path) -> bool:
        """Check if this rule applies to a given file path."""
        path_str = str(file_path)
        for glob in self.globs:
            pattern = glob.replace("**", "*")
            if fnmatch.fnmatch(path_str, f"*{pattern}") or fnmatch.fnmatch(
                path_str, pattern
            ):
                return True
        return False


class SourceFile(BaseModel):
    """A source file with its content, capable of scanning for signals."""

    model_config = {"frozen": True}
    path: Path
    content: str

    def scan(self) -> tuple[Signal, ...]:
        """Scan for mechanical signals. Returns facts, not verdicts."""
        try:
            tree = ast.parse(self.content)
        except SyntaxError:
            return ()

        lines = self.content.splitlines()
        get_line = self._make_line_getter(lines)

        signals: list[Signal] = []
        for node in ast.walk(tree):
            signal = self._detect_signal(node, get_line)
            if signal is not None:
                signals.append(signal)

        return tuple(signals)

    def _make_line_getter(self, lines: list[str]) -> Callable[[int], SourceLine]:
        """Create a function to safely get line content."""

        def get_line(lineno: int) -> SourceLine:
            if 1 <= lineno <= len(lines):
                line = lines[lineno - 1].strip()
                return SourceLine(line[:60] + "..." if len(line) > 60 else line)
            return SourceLine("")

        return get_line

    def _detect_signal(
        self, node: ast.AST, get_line: Callable[[int], SourceLine]
    ) -> Signal | None:
        """Detect a single signal from an AST node."""
        match node:
            # Pattern 03: try/except
            case ast.Try():
                return Signal(
                    kind=SignalKind("try_block"),
                    pattern_id=PatternId("03"),
                    line=node.lineno,
                    content=get_line(node.lineno),
                    hint=SignalHint("try/except — use Result types instead"),
                )

            # Pattern 03: raise
            case ast.Raise():
                return Signal(
                    kind=SignalKind("raise_stmt"),
                    pattern_id=PatternId("03"),
                    line=node.lineno,
                    content=get_line(node.lineno),
                    hint=SignalHint("raise — return Failure types instead"),
                )

            # Pattern 04: await
            case ast.Await():
                return Signal(
                    kind=SignalKind("await_expr"),
                    pattern_id=PatternId("04"),
                    line=node.lineno,
                    content=get_line(node.lineno),
                    hint=SignalHint("await in domain — async belongs in Shell"),
                )

            # Pattern 04: *Service, *Manager, *Handler classes
            case ast.ClassDef(name=name) if re.search(
                r"(Service|Manager|Handler|Processor)$", name
            ):
                return Signal(
                    kind=SignalKind("service_class"),
                    pattern_id=PatternId("04"),
                    line=node.lineno,
                    content=get_line(node.lineno),
                    hint=SignalHint("*Service/*Manager class — use Intent objects"),
                )

            # Pattern 01: validate_*, check_*, verify_* functions
            case ast.FunctionDef(name=name) if re.match(
                r"^(validate_|check_|verify_)", name
            ):
                return Signal(
                    kind=SignalKind("validate_function"),
                    pattern_id=PatternId("01"),
                    line=node.lineno,
                    content=get_line(node.lineno),
                    hint=SignalHint("validate_* functions — use Factory pattern"),
                )

            # Pattern 02: is_* attribute names
            case ast.AnnAssign(target=ast.Name(id=name)) if name.startswith("is_"):
                return Signal(
                    kind=SignalKind("boolean_flag"),
                    pattern_id=PatternId("02"),
                    line=node.lineno,
                    content=get_line(node.lineno),
                    hint=SignalHint("is_* boolean flag — use Sum Types instead"),
                )

            # Pattern 01: primitive type annotations
            case ast.AnnAssign(annotation=ast.Name(id=t)) if t in (
                "str",
                "int",
                "bool",
                "float",
            ):
                return Signal(
                    kind=SignalKind("primitive_type"),
                    pattern_id=PatternId("01"),
                    line=node.lineno,
                    content=get_line(node.lineno),
                    hint=SignalHint(f"Primitive type '{t}' — consider Value Object"),
                )

            # Pattern 01: default values (not None, not Field())
            case ast.AnnAssign(value=v) if v is not None:
                if not self._is_safe_default(v):
                    return Signal(
                        kind=SignalKind("field_default"),
                        pattern_id=PatternId("01"),
                        line=node.lineno,
                        content=get_line(node.lineno),
                        hint=SignalHint(
                            "Default value — explicit construction required"
                        ),
                    )

            case _:
                pass

        return None

    def _is_safe_default(self, node: ast.expr) -> bool:
        """Check if a default value is architecturally safe."""
        match node:
            case ast.Constant(value=None):
                return True
            case ast.Call(func=ast.Name(id="Field")):
                return True
            case _:
                return False


class ScanResult(BaseModel):
    """Result of scanning a file: signals found + applicable rules."""

    model_config = {"frozen": True}
    file_path: Path
    signals: tuple[Signal, ...]
    applicable_rules: tuple[RuleRef, ...]

    def format_message(self) -> HookOutput:
        """Format the agent message with signals and rule content."""
        if not self.signals and not self.applicable_rules:
            return NoOutput(kind="no_output")

        parts: list[str] = []

        # Header
        parts.append(f"## Architect's Mirror: {self.file_path.name}\n")

        # Signals section
        if self.signals:
            parts.append("### Signals Detected\n")
            parts.append(
                "These are mechanical observations, not verdicts. Use your judgment.\n"
            )
            for sig in self.signals:
                parts.append(f"- **Line {sig.line}** [{sig.kind}]: `{sig.content}`")
                parts.append(f"  - Hint: {sig.hint}")
                parts.append(f"  - Related: Pattern {sig.pattern_id}\n")

        # Applicable rules section
        if self.applicable_rules:
            parts.append("\n### Applicable Rules\n")
            parts.append("Review your changes against these patterns:\n")
            for rule in self.applicable_rules:
                parts.append(f'<rule id="{rule.pattern_id}" name="{rule.name}">\n')
                parts.append(rule.content)
                parts.append("\n</rule>\n")

        # Judgment prompt
        parts.append("\n### Your Judgment\n")
        parts.append("Reconcile the signals against the rules. ")
        parts.append("Some signals may be false positives in context. ")
        parts.append("Fix actual violations. Ignore false alarms.\n")

        return MessageOutput(kind="message", agent_message="\n".join(parts))


class FileProcessor(BaseModel):
    """Processor that scans files against a set of rules."""

    model_config = {"frozen": True}
    rules: tuple[RuleRef, ...]

    def process(self, source: SourceFile) -> ScanResult:
        """Process a source file: scan for signals, match rules."""
        signals = source.scan()
        applicable_rules = tuple(r for r in self.rules if r.matches_path(source.path))

        return ScanResult(
            file_path=source.path,
            signals=signals,
            applicable_rules=applicable_rules,
        )


# =============================================================================
# 6. DOMAIN MODELS — Input Parsing (Foreign Reality → Domain)
# =============================================================================


class RawHookInput(BaseModel):
    """Raw input from Cursor hook — Foreign Reality."""

    model_config = {"frozen": True}
    file_path: Path | None = None
    status: Literal["completed", "aborted", "error"] | None = None

    def to_domain(self) -> HookInput:
        """Parse raw input into domain Sum Type."""
        if self.status == "aborted":
            return StopInput(kind="stop", status="aborted")
        if self.status is not None:
            return StopInput(kind="stop", status=self.status)
        if self.file_path is not None:
            return FileEditInput(kind="file_edit", file_path=self.file_path)
        return EmptyInput(kind="empty")


class RawRuleFrontmatter(BaseModel):
    """Raw frontmatter content — used to parse globs."""

    model_config = {"frozen": True}
    content: str

    def parse_globs(self) -> GlobsResult:
        """Extract globs from YAML frontmatter."""
        if not self.content.startswith("---"):
            return GlobsNotFound(kind="not_found")

        end = self.content.find("---", 3)
        if end == -1:
            return GlobsNotFound(kind="not_found")

        frontmatter = self.content[3:end]
        match = re.search(r"globs:\s*\[(.*?)\]", frontmatter)
        if not match:
            return GlobsNotFound(kind="not_found")

        globs_str = match.group(1)
        globs = tuple(
            GlobPattern(g.strip().strip("\"'"))
            for g in globs_str.split(",")
            if g.strip()
        )

        return GlobsParsed(kind="parsed", globs=globs)


# =============================================================================
# 7. SHELL — I/O at Edges
# =============================================================================

RULES_DIR = Path(__file__).parent.parent / "rules"
FEEDBACK_FILE = Path(__file__).parent.parent / "mirror-feedback.md"


def read_stdin() -> str:
    """Read raw input from stdin."""
    if sys.stdin.isatty():
        return ""
    return sys.stdin.read().strip()


def read_file(path: Path) -> ContentResult:
    """Read file content. I/O boundary."""
    try:
        content = path.read_text("utf-8")
        return ContentLoaded(kind="loaded", content=content)
    except (OSError, UnicodeDecodeError):
        return ContentUnreadable(kind="unreadable", path=path)


def write_feedback(content: str) -> None:
    """Write feedback to the mirror feedback file. I/O boundary."""
    FEEDBACK_FILE.write_text(content, encoding="utf-8")


def clear_feedback() -> None:
    """Clear the feedback file. I/O boundary."""
    if FEEDBACK_FILE.exists():
        FEEDBACK_FILE.write_text("", encoding="utf-8")


def discover_rules() -> tuple[RuleRef, ...]:
    """Discover all pattern rules. I/O boundary."""
    if not RULES_DIR.exists():
        return ()

    rules: list[RuleRef] = []

    for rule_dir in sorted(RULES_DIR.iterdir()):
        if not rule_dir.is_dir() or not rule_dir.name.startswith("pattern-"):
            continue

        rule_file = rule_dir / "RULE.md"
        if not rule_file.exists():
            continue

        # Extract pattern_id
        match = re.match(r"pattern-(\d+)", rule_dir.name)
        if not match:
            continue

        pattern_id = PatternId(match.group(1))

        # Read content
        content_result = read_file(rule_file)
        match content_result:
            case ContentUnreadable():
                continue
            case ContentLoaded(content=content):
                pass

        # Parse globs
        frontmatter = RawRuleFrontmatter(content=content)
        globs_result = frontmatter.parse_globs()

        globs: tuple[GlobPattern, ...] = ()
        match globs_result:
            case GlobsParsed(globs=g):
                globs = g
            case GlobsNotFound():
                pass

        rules.append(
            RuleRef(
                pattern_id=pattern_id,
                name=RuleName(rule_dir.name),
                globs=globs,
                content=RuleContent(content),
            )
        )

    return tuple(rules)


def main() -> None:
    """Entry point. Shell layer — handles all I/O.

    Supports two modes:
    1. Hook mode: receives JSON on stdin from Cursor
    2. CLI mode: python3 mirror.py <file_path>
    """
    # 1. Check for CLI argument first (determines output mode)
    cli_mode = len(sys.argv) > 1
    if cli_mode:
        file_path = Path(sys.argv[1])
        hook_input: HookInput = FileEditInput(kind="file_edit", file_path=file_path)
    else:
        # 2. Read stdin (hook mode)
        raw_input = read_stdin()

        # 3. Parse input (Foreign Reality → Domain)
        if raw_input:
            try:
                raw = RawHookInput.model_validate_json(raw_input)
            except Exception:
                raw = RawHookInput()
        else:
            raw = RawHookInput()

        hook_input = raw.to_domain()

    # 4. Handle input based on type
    match hook_input:
        case StopInput(status="aborted"):
            clear_feedback()
            if not cli_mode:
                print(NoOutput(kind="no_output").to_json())
            return

        case EmptyInput():
            if not cli_mode:
                print(NoOutput(kind="no_output").to_json())
            return

        case FileEditInput(file_path=file_path):
            # 4. Read the edited file
            content_result = read_file(file_path)
            match content_result:
                case ContentUnreadable():
                    return
                case ContentLoaded(content=content):
                    source = SourceFile(path=file_path, content=content)

            # 5. Discover and load rules
            rules = discover_rules()

            # 6. Process file
            processor = FileProcessor(rules=rules)
            result = processor.process(source)

            # 7. Format and output
            output = result.format_message()
            match output:
                case MessageOutput(agent_message=msg):
                    write_feedback(msg)
                    if cli_mode:
                        print(msg)  # Human-readable for CLI
                    else:
                        print(output.to_json())  # JSON for hook
                case NoOutput():
                    clear_feedback()
                    if cli_mode:
                        print("✅ No signals detected.")
                    else:
                        print(output.to_json())  # Empty JSON for hook

        case StopInput():
            # On stop, clear the feedback file
            clear_feedback()
            if not cli_mode:
                print(NoOutput(kind="no_output").to_json())


if __name__ == "__main__":
    main()
