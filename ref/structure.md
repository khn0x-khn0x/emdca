# Structure Guide: Contextual Co-location

**The Principle:** The location of a file dictates its capabilities. We organize by **Context** (Vertical Slice), not by **Layer** (Horizontal Slice).

Traditional architectures separate "Adapters" from "Entities" into distant folders. EMDCA rejects this. Knowledge of an external system (e.g., a specific Vendor API) is **Domain Knowledge** and must live inside the Domain Context that uses it.

---

## 🏗️ The File Hierarchy

```text
src/
├── main.py                  # THE TRUE ROOT / LAUNCHER (Composition Root)
├── domain/                  # THE CORE (Pure, Vertical Slices)
│   ├── context_1/           # Context: Primary Business Feature
│   │   ├── entity.py        # Internal Truth (Domain Models)
│   │   ├── api.py           # Foreign Reality (Our HTTP API Schema)
│   │   ├── vendor.py        # Foreign Reality (External Vendor Schema)
│   │   ├── store.py         # Foreign Reality (Database Schema)
│   │   └── workflow.py      # Aggregates with decision methods
│   │
│   └── system/              # Context: System Capabilities
│       ├── config.py        # Internal Truth (AppConfig, ConfigResult)
│       └── env.py           # Foreign Reality (EnvVars)
│
├── service/                 # THE SHELL (Orchestration & Execution)
│   ├── context_1.py         # Orchestrator/Executor models for Context 1
│   └── app.py               # Composition Root Helpers
│
└── api/                     # THE INTERFACE (Impure, Horizontal)
    ├── app.py               # The App Definition (Builds FastAPI instance)
    ├── deps.py              # Shared Dependencies (Auth, DB)
    └── context_1.py         # Interface Adapter (Router for Context 1)
```

---

## 📐 The Dependency Rule

Imports must strictly flow **inward** toward the Domain.

*   ✅ `service/` imports `domain/`
*   ✅ `api/` imports `service/` and `domain/`
*   ❌ `domain/` **NEVER** imports `service/` or `api/`

### The Composition Rule (Cross-Domain Imports)
Contexts are not islands. They share a "Ubiquitous Language."

*   ✅ **Allowed:** Contexts may import **Domain Models** (Entities, Value Objects) from other contexts. (e.g., `Trade` imports `User` from `Identity`). This is "Using the Real Thing."
*   ❌ **Forbidden:** Contexts must never import **Services** or **APIs** from other contexts.
*   **Guideline:** If `Trade` needs to know if a `User` is active, pass the `User` object, not just a `user_id`.

---

## 📂 `src/domain/` (The Core)

This directory is grouped by **Context** (Business Area).

**All domain models MUST have `model_config = {"frozen": True}`.**

**Allowed File Types per Context:**

1.  **Internal Truth (`entity.py`, `user.py`, `order.py`):**
    *   Frozen Pydantic models with `model_config = {"frozen": True}`.
    *   Defines the language of the business.
    *   **Banned Names:** `model.py` (Too generic. Name the file after the concept).

2.  **Atoms (`types.py`, `values.py`):**
    *   Context-specific Value Objects (`OrderId`) and Smart Enums (`OrderStatus`).
    *   Use Pydantic built-ins (`EmailStr`, `PositiveInt`) over hand-rolled validators.

3.  **Foreign Reality (`api.py`, `vendor.py`, `store.py`):**
    *   **`api.py`:** The schema of our own API (Request/Response models).
    *   **`vendor.py`:** The schema of external APIs we consume.
    *   **`store.py`:** The schema of our Database Tables (e.g., `DbOrder`).
    *   All Foreign Models own a `.to_domain()` method.

4.  **Aggregates & Workflows (`workflow.py`, `order.py`):**
    *   Frozen Pydantic models with **decision methods**.
    *   Methods return `Result`, `Intent`, or new state—never standalone functions.
    *   **Banned Names:** `logic.py`, `utils.py`, `helpers.py`, `process.py`.

---

## 📂 `src/domain/shared/` (The Ubiquitous Language)

This is a special Context that contains universal primitives used across multiple contexts. Other contexts may import from here.

*   **`primitives.py`:** Value Objects like `Money`, `Email`, `Currency`.
*   **`ids.py`:** Base classes for strongly-typed IDs.
*   **Constraint:** Strictly frozen Pydantic models and Smart Enums. No side effects.

---

## 📂 `src/service/` (The Shell)

The Service Layer is the **Imperative Shell**. It handles Orchestration and Execution.

*   **Responsibility:** Fetch Data → Call Logic → Save Data.
*   **Contains:**
    *   **Stores:** Frozen Pydantic models that handle DB I/O.
    *   **Orchestrators:** Frozen Pydantic models with **dependencies as fields** (stores, gateways, executors).
    *   **Executors:** Frozen Pydantic models that compose Intent + RawResult → DomainOutcome.
*   **Philosophy:** Dumb code. No business rules. Just wiring and execution.
*   **No standalone functions.** All logic is methods on models.
*   **Dependencies are fields.** Orchestrators declare what they need; composition root injects it.

---

## 📂 `src/api/` (The Interface)

The entry point for external traffic (HTTP/GRPC). It mirrors the Domain Contexts with flat files.

*   **`app.py`:** Defines the `FastAPI` instance.
*   **`deps.py`:** Defines shared runtime dependencies (Auth, DB).
*   **`context_1.py`:** Defines the Router for Context 1. Imports contracts from `domain/context_1/api.py`.

API route handlers are the composition root equivalent—standalone functions are acceptable here.

---

## ⚡ The Composition Root (`src/main.py`)

This is the **Big Bang**. It is the only place in the system where imports cross every boundary. Its job is to turn **Foreign Reality** (Env) into **Internal Truth** (Config) and wire the **Services** together.

**The composition root is the ONE exception where standalone wiring code exists.**

**The Template:**

```python
# src/main.py
import os
import sys
import uvicorn
from pydantic import ValidationError
from domain.system.env import EnvVars
from domain.system.config import ConfigLoaded, ConfigInvalid, ConfigResult
from api.app import create_api

def load_config(raw_env: dict) -> ConfigResult:
    """Parse environment into config. Returns Sum Type, no exceptions escape."""
    try:
        config = EnvVars.model_validate(raw_env).to_domain()
        return ConfigLoaded(kind="loaded", config=config)
    except ValidationError as e:
        errors = tuple(str(err) for err in e.errors())
        return ConfigInvalid(kind="invalid", errors=errors)


def main():
    """
    The Launcher.
    1. Validate Reality (Env)
    2. Translate to Truth (Config)
    3. Wire Infrastructure (DI)
    4. Launch Interface (App)
    """
    
    # 1. Load Config (returns Sum Type)
    result = load_config(dict(os.environ))
    
    match result:
        case ConfigInvalid(errors=errs):
            print(f"FATAL: Invalid Environment Configuration\n{errs}")
            sys.exit(1)
        
        case ConfigLoaded(config=config):
            # 2. Wire Dependencies (inject as fields)
            store = OrderStore()
            gateway = PaymentGateway(api_key=config.stripe_key)
            orchestrator = OrderOrchestrator(store=store, gateway=gateway)
            
            # 3. Launch Interface (pass wired orchestrators)
            app = create_api(config, orchestrator=orchestrator)
            uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
```
