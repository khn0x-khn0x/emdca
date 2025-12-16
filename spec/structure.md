# Structure Guide: Contextual Co-location

**The Principle:** The location of a file dictates its capabilities. We organize by **Context** (Vertical Slice), not by **Layer** (Horizontal Slice).

Traditional architectures separate "Adapters" from "Entities" into distant folders. EMDCA rejects this. Knowledge of an external system (e.g., a specific Vendor API) is **Domain Knowledge** and must live inside the Domain Context that uses it.

---

## 🏗️ The File Hierarchy

```text
src/
├── main.py                  # THE TRUE ROOT / LAUNCHER (Composition Root Decision)
├── domain/                  # THE CORE (Pure, Vertical Slices)
│   ├── context_1/           # Context: Primary Business Feature
│   │   ├── entity.py        # Internal Truth (Domain Models)
│   │   ├── api.py           # Foreign Reality (Our HTTP API Schema)
│   │   ├── vendor.py        # Foreign Reality (External Vendor Schema)
│   │   ├── store.py         # Foreign Reality (Database Schema)
│   │   └── process.py       # Pure Logic (Factories / State Machines)
│   │
│   ├── system/              # Context: System Capabilities
│   │   ├── config.py        # Internal Truth (AppConfig)
│   │   └── env.py           # Foreign Reality (EnvVars)
│   │
│   └── infra/               # Context: Infrastructure Intents
│       ├── nats.py          # Intents: ConnectIntent, PublishIntent
│       └── redis.py         # Intents: GetIntent, SetIntent
│
├── service/                 # THE SHELL (Orchestration & Execution)
│   ├── context_1.py         # Procedural Loops / Consumers
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

**Allowed File Types per Context:**

1.  **Internal Truth (`entity.py`, `user.py`, `order.py`):**
    *   Pure Pydantic models.
    *   Defines the language of the business.
    *   **Banned Names:** `model.py` (Too generic. Name the file after the concept).

2.  **Atoms (`types.py`, `values.py`):**
    *   Context-specific Value Objects (`OrderId`) and Enums (`OrderStatus`).

3.  **Foreign Reality (`api.py`, `vendor.py`, `store.py`):**
    *   **`api.py`:** The schema of our own API (Request/Response models).
    *   **`vendor.py`:** The schema of external APIs we consume.
    *   **`store.py`:** The schema of our Database Tables (e.g., `DbOrder`).
    *   This is where "Adapters" live. Knowing the shape of data is Domain Knowledge.

4.  **Pure Logic (`process.py`, `calculation.py`, `workflow.py`):**
    *   Pure functions.
    *   Input: `ForeignModel` or `DomainModel`.
    *   Output: `Result`, `Intent`, or `NewState`.
    *   **Banned Names:** `logic.py`, `utils.py`, `helpers.py`. (Name the file after the Process).

---

## 📂 `src/domain/shared/` (The Ubiquitous Language)

This is a special Context that contains universal primitives used across multiple contexts. Other contexts may import from here.

*   **`primitives.py`:** Value Objects like `Money`, `Email`, `Currency`.
*   **`ids.py`:** Base classes for strongly-typed IDs.
*   **Constraint:** strictly pure types. No side effects.

---

## 📂 `src/service/` (The Shell)

The Service Layer is the **Imperative Shell**. It handles Orchestration (Workflow) and Execution (I/O).

*   **Responsibility:** Fetch Data -> Call Logic -> Save Data.
*   **Contains:**
    *   **Orchestrators:** Procedural loops (`process_order_flow`).
    *   **Execution:** Generic Executor for Intent fulfillment.
*   **Philosophy:** Dumb code. No business rules. Just wiring and execution.

---

## 📂 `src/api/` (The Interface)

The entry point for external traffic (HTTP/GRPC). It mirrors the Domain Contexts with flat files.

*   **`app.py`:** Defines the `FastAPI` instance.
*   **`deps.py`:** Defines shared runtime dependencies (Auth, DB).
*   **`context_1.py`:** Defines the Router for Context 1. Imports contracts from `domain/context_1/api.py`.

---

## ⚡ The Composition Root (`src/main.py`)

This is the **Big Bang**. It is the only place in the system where imports cross every boundary. Its job is to turn **Foreign Reality** (Env) into **Internal Truth** (Config) and wire the **Services** together.

**The Template:**

```python
# src/main.py
import os
import sys
import uvicorn
from domain.system.env import EnvVars
from api.app import create_api  # The Interface Builder

# Import your Contexts (The Features)
from api.context_1 import router as context_1_router
from api.context_2 import router as context_2_router

def main():
    """
    The Launcher.
    1. Validate Reality (Env)
    2. Translate to Truth (Config)
    3. Wire Infrastructure (DI)
    4. Launch Interface (App)
    """
    
    # 1. Capture Foreign Reality (The OS)
    raw_env = os.environ
    
    try:
        # 2. Translate to Internal Truth
        # If the OS is messy, we fail here, before the app starts.
        config = EnvVars.model_validate(raw_env).to_domain()
    except Exception as e:
        print(f"FATAL: Invalid Environment Configuration\n{e}")
        sys.exit(1)

    # 3. Wiring (Infrastructure)
    # Use Intent-Based Setup (Pattern 10)
    # nats_intent = ConnectIntent(url=config.nats_url)
    # execute(nats_intent)
    
    # 4. Launch Interface
    # We pass the wired dependencies to the App Builder
    # app = create_api(config, db_client)
    
    # 5. Run Server
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
```
