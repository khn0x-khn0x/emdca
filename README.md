# EMDCA: Explicitly Modeled Data-Centric Architecture

[![Architecture: EMDCA](https://img.shields.io/badge/Architecture-EMDCA-blueviolet)](spec/arch.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python: 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**A rigorous architectural standard for building correct-by-construction, AI-native software systems.**

EMDCA eliminates "conceptual fragmentation" by enforcing strict co-location of logic and data, utilizing algebraic data types, and separating decision-making (Pure Core) from execution (Impure Shell).

---

## 📚 Documentation Map

| Document | Purpose | Audience |
| :--- | :--- | :--- |
| **[Manifesto](manifesto.md)** | The **Philosophy**. Explains *why* traditional architectures fail and why explicit modeling is the cure. | Architects, Leads |
| **[Architecture Spec](spec/arch.md)** | The **Laws**. The 10 non-negotiable mandates that define the standard. | Developers, AI Agents |
| **[Structure Guide](spec/structure.md)** | The **Map**. Defines the vertical slice file structure. | Developers |
| **[Patterns Library](spec/patterns/)** | The **Blueprints**. Idiomatic Python implementations of the mandates. | Everyone |
| **[Agentic Systems](spec/agentic.md)** | The **Translation**. Maps "Agent" buzzwords to standard architectural patterns. | AI Engineers |

---

## ⚖️ The 10 Mandates (Cheat Sheet)

1.  **Construction:** Use Value Objects & Pure Factories. Parse, don't validate. ([Pattern 01](spec/patterns/01-factory-construction.md))
2.  **State:** Use Sum Types (Discriminated Unions). Make invalid states unrepresentable. ([Pattern 02](spec/patterns/02-state-sum-types.md))
3.  **Control Flow:** Use Railway Oriented Programming. No Exceptions for logic. ([Pattern 03](spec/patterns/03-railway-control-flow.md))
4.  **Execution:** Return Intents as Data. The Core decides; the Shell executes. ([Pattern 04](spec/patterns/04-execution-intent.md))
5.  **Configuration:** Treat EnvVars as Foreign Reality. Translate to pure AppConfig. ([Pattern 05](spec/patterns/05-config-injection.md))
6.  **Abstraction:** Define Storage Protocols. The Domain never performs direct I/O. ([Pattern 06](spec/patterns/06-repository-abstraction.md))
7.  **Translation:** Use Foreign Models. Declarative mapping of External Reality to Internal Truth. ([Pattern 07](spec/patterns/07-acl-translation.md))
8.  **Coordination:** Use a Dumb Orchestrator. The loop only moves data; it never thinks. ([Pattern 08](spec/patterns/08-orchestrator-loop.md))
9.  **Workflow:** Model Process as a State Machine. The Domain drives the next step. ([Pattern 09](spec/patterns/09-workflow-state-machine.md))
10. **Infrastructure:** Model Capability as Data. Topology is configuration, not code. ([Pattern 10](spec/patterns/10-infrastructure-capability-as-data.md))

---

## 🚀 Usage

This repository is a **Reference Standard**.

*   **For Humans:** Read the Manifesto to align on philosophy. Use the Patterns as a style guide for your codebase.
*   **For AI Agents:** Use `spec/arch.md` as a system prompt or context to ensure generated code adheres to strict correctness guarantees.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
