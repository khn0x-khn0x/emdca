# The Reference Skeleton

The `spec/src/` directory in this repository contains a complete **Reference Implementation** of the EMDCA file structure. It uses a hypothetical `conversation` context to demonstrate the patterns in action.

## 🧭 How to Use

This skeleton serves as a living template. Every file contains a **Structural Docstring** that acts as a reverse index to the documentation.

1.  **For Humans:** Open any file in `src/` to see its Role, Mandates, and Constraints.
2.  **For Agents:** Read the file headers to understand the semantic purpose of each component before generating code.

## 🏗️ The Structure

```text
src/
├── main.py                  # The Launcher (Composition Root)
├── api/
│   ├── app.py               # The Interface Builder (FastAPI)
│   ├── deps.py              # Shared Dependencies
│   └── conversation.py      # The Router (Interface Adapter)
├── service/
│   └── conversation_svc.py  # The Orchestrator (Service Layer)
└── domain/
    ├── system/              # System Context
    │   ├── config.py        # Internal Truth (Config)
    │   └── env.py           # Foreign Reality (EnvVars)
    ├── shared/              # Shared Context
    │   └── primitives.py    # Ubiquitous Language (Value Objects)
    └── conversation/        # Feature Context
        ├── entity.py        # Internal Truth (Domain Model)
        ├── api.py           # Foreign Reality (API Contract)
        ├── vendor.py        # Foreign Reality (Vendor Schema)
        └── process.py       # Pure Logic (Factory / Workflow)
```

## 🔗 The Reverse Index

Each file header links back to specific **Mandates** in `spec/arch.md` and **Patterns** in `spec/patterns/`. This ensures that the code structure remains strictly aligned with the architectural specification.

