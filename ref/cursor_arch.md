# Cursor Agent Architecture (The Mirror)

This document describes the **Active Enforcement System** built into this repository to guide AI agents (and humans) toward architectural purity.

---

## 🏗️ System Overview

The `.cursor/` directory contains a feedback loop that combines **Context Priming** (Rules) with **Active Verification** (Mirror).

```text
.cursor/
├── hooks.json              # Event configuration (triggers)
├── mirror-feedback.md      # ← THE SIGNAL (agent reads this)
├── hooks/
│   └── mirror.py           # AST Analyzer (Python script)
└── rules/
    ├── pattern-00-master-architecture/   # ← Instructs: "RUN mirror.py"
    └── pattern-XX-*/                     # Specific constraints
```

---

## 🔄 The Feedback Loop

This system bridges the gap between **Static Knowledge** (reading documentation) and **Runtime Correction** (seeing errors).

1.  **Prime:** The Agent reads `.cursor/rules/pattern-*/RULE.md` to understand the constraints.
2.  **Edit:** The Agent modifies a file.
3.  **Reflect:** The system (via hooks or manual command) runs `mirror.py` against the file.
4.  **Correct:** The Mirror outputs specific violations (e.g., "Found `try/except` in Domain"). The Agent fixes them immediately.

---

## 🧩 Components

### 1. Rules (Passive Context)
Each architectural pattern has a corresponding rule file (`RULE.md`).
*   **Role:** Provides "Few-Shot Examples" of correct vs. incorrect code.
*   **Mechanism:** Cursor loads these into the Agent's context based on file globs.
*   **Key File:** `pattern-00-master-architecture/RULE.md` is the **Constitution**. It is always applied and defines the high-level discriminators (Data vs Behavior).

### 2. The Mirror (Active Verification)
`hooks/mirror.py` is a Python script that parses the Abstract Syntax Tree (AST) of the codebase.
*   **Role:** Micro-Linter / Agent Context Primer. Provides high-signal, low-noise architectural feedback.
*   **Capabilities:**
    *   **Identity Checks:**
        *   Detects `BaseModel` inheritance in Service directories (Service classes must be plain classes).
        *   Detects non-Model classes in Domain directories (Domain objects must be Pydantic Models or Enums).
        *   Detects Service/Manager/Handler/Processor classes in Domain (wrong layer).
    *   **Flow Checks:**
        *   Detects `try/except` blocks in Domain (banned; use Result Types or Let It Crash).
        *   Detects `raise` statements in Domain (banned; return Failure Results).
        *   Detects `await` expressions in Domain (banned; async/IO belongs in Shell).
    *   **Naming Smells:**
        *   Detects `validate_*`, `check_*`, `verify_*` functions (banned; use Parse-Don't-Validate via Types).
*   **Output:** Writes plain English signals to `mirror-feedback.md` (hook mode) or stdout (CLI mode).

### 3. Hooks (Automation)
`hooks.json` binds the Mirror to IDE events.

| Event | Action |
| :--- | :--- |
| `afterFileEdit` | Runs `mirror.py` on the edited file. Writes results to `mirror-feedback.md`. |
| `stop` | Clears `mirror-feedback.md` (reset state). |

---

## 🤖 Agent Workflow

### Automatic Mode (Hook-Driven)
1.  Agent writes code to `src/domain/user.py`.
2.  Agent saves the file.
3.  Cursor runs `mirror.py`.
4.  Agent checks `mirror-feedback.md`.
5.  If violations exist, Agent fixes them *before* considering the task done.

### Manual Mode (CLI-Driven)
The Master Rule instructs the Agent to run the mirror manually for faster feedback.

```bash
python3 .cursor/hooks/mirror.py src/domain/user.py
```

This prints violations directly to the terminal, allowing a tight "Edit-Run-Fix" loop.

---

## 🧠 Design Philosophy

**"Hallucinations become Compilation Errors."**

AI Agents struggle with abstract constraints. They excel at fixing concrete errors. The Mirror converts "Architectural Philosophy" (Abstract) into "Linter Errors" (Concrete).

*   **Philosophy:** "Don't use exceptions for flow control."
*   **Mirror Signal:** "Line 42: Found `try/except` block in `domain/`. Remove it."

This allows the Agent to **self-correct** without human intervention.

**Micro-Linter Focus:** The Mirror is intentionally simplified to detect only the most critical structural violations. It acts as an "Agent Context Primer" rather than a comprehensive linter, providing high-signal feedback that guides the Agent toward architectural purity without overwhelming it with noise.

