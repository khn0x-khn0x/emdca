# EMDCA: Explicitly Modeled Data-Centric Architecture

[![Architecture: EMDCA](https://img.shields.io/badge/Architecture-EMDCA-blueviolet)](spec/arch.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python: 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**A rigorous architectural standard for building correct-by-construction, AI-native software systems.**

EMDCA eliminates "conceptual fragmentation" by enforcing strict co-location of logic and data, utilizing algebraic data types, and separating decision-making (Pure Core) from execution (Impure Shell).

---

## 🎯 Why EMDCA?

Software systems fail not from incorrect algorithms but from **scattered truth**. The rules governing a business entity become distributed across services, validators, and utilities. Understanding what an "Order" truly is requires archaeology across dozens of files.

EMDCA fixes this structurally:

- **Co-locate logic with data.** The type answers the question, not an external service.
- **Make invalid states unrepresentable.** Validation happens once, at construction.
- **Separate decisions from side effects.** The Pure Core decides; the Impure Shell executes.

---

## ⚖️ The 10 Mandates

1.  **Construction:** Use Value Objects & Pure Factories. Parse, don't validate. ([Pattern 01](spec/patterns/01-factory-construction.md))
2.  **State:** Use Sum Types (Discriminated Unions). Make invalid states unrepresentable. ([Pattern 02](spec/patterns/02-state-sum-types.md))
3.  **Control Flow:** Use Railway Oriented Programming. No Exceptions for logic. ([Pattern 03](spec/patterns/03-railway-control-flow.md))
4.  **Execution:** Return Intents as Contracts. Complete specification of side effects and outcomes. ([Pattern 04](spec/patterns/04-execution-intent.md))
5.  **Configuration:** Treat EnvVars as Foreign Reality. Translate to pure AppConfig. ([Pattern 05](spec/patterns/05-config-injection.md))
6.  **Storage:** Treat DB as Foreign Reality. Translate to pure Domain Objects. ([Pattern 06](spec/patterns/06-repository-abstraction.md))
7.  **Translation:** Use Foreign Models. Declarative mapping of External Reality to Internal Truth. ([Pattern 07](spec/patterns/07-acl-translation.md))
8.  **Coordination:** Use a Dumb Orchestrator. The loop only moves data; it never thinks. ([Pattern 08](spec/patterns/08-orchestrator-loop.md))
9.  **Workflow:** Model Process as a State Machine. The Domain drives the next step. ([Pattern 09](spec/patterns/09-workflow-state-machine.md))
10. **Infrastructure:** Model Capability as Data. Topology is configuration, not code. ([Pattern 10](spec/patterns/10-infrastructure-capability-as-data.md))

---

## 🛡️ Automated Enforcement: "The Architect's Mirror"

EMDCA is not just a document; it is an active constraint system. This repository includes **The Architect's Mirror** (`.cursor/hooks/mirror.py`), a pure-Python AST analyzer that enforces the mandates in real-time.

It acts as a "Synthetic Supervisor" for both Human Developers and AI Agents, instantly flagging:
- **Structural Violations**: Using `raise` or `await` in the Domain.
- **Architectural Drift**: Importing external libraries (`boto3`) into the Pure Core.
- **Procedural Habits**: Writing `Manager` classes instead of Aggregates.

The Mirror runs:
1.  **Locally**: Inside Cursor via Hooks (`afterFileEdit`).
2.  **Remotely**: In GitHub Actions (`.github/workflows/ci.yml`).

---

## 📚 Documentation

| Document | What It Is |
| :--- | :--- |
| **[Manifesto](manifesto.md)** | The **Philosophy**. Why explicit modeling matters. |
| **[Architecture Spec](spec/arch.md)** | The **Laws**. The 10 mandates in detail. |
| **[Structure Guide](spec/structure.md)** | The **Map**. Vertical slice file organization. |
| **[Patterns Library](spec/patterns/)** | The **Blueprints**. Idiomatic Python implementations. |
| **[Agentic Systems](spec/agentic.md)** | The **Translation**. "Agent" buzzwords → real patterns. |
| **[Reference Skeleton](spec/skeleton.md)** | The **Template**. A working starter structure. |

---

## 🚀 Getting Started

**To Learn:** Read the [Manifesto](manifesto.md), then the [Architecture Spec](spec/arch.md).

**To Reference:** Copy `spec/` into your project. Use the patterns as a style guide.

**To Build:** Start from the [Reference Skeleton](spec/skeleton.md). Every file in `spec/src/` contains structural docstrings linking back to the mandates.

**For AI Agents:** This repo is designed for you. The `.cursor/rules/` prime your context, and the Mirror hooks correct your output. The constraints act as guardrails—hallucinations become compilation errors.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
