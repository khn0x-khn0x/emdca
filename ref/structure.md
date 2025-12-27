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
│   │   ├── db.py            # Foreign Reality (Database Schema)
│   │   ├── contract.py      # Intents & Interfaces (Data Contracts)
│   │   └── workflow.py      # Aggregates with decision methods
│   │
│   └── system/              # Context: System Capabilities
│       └── config.py        # AppConfig (BaseSettings) - Schema of Environment
│
├── service/                 # THE SHELL (Orchestration & Execution)
│   ├── context_1.py         # Executors & Runtimes for Context 1
│   └── app.py               # Service Classes
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

## 🏷️ The Naming Mandate: Concepts over Layers

Never name a file after a generic technical pattern (`model.py`, `logic.py`, `utils.py`, `helpers.py`).
Name files after the **Business Concept** they contain.

**Why?**
Generic names create "Junk Drawers." Conceptual names create **Context Boundaries**.

*   ❌ `domain/pricing/utils.py` (Junk Drawer)
*   ✅ `domain/pricing/discounts.py` (Specific Business Rule)

*   ❌ `domain/order/model.py` (Generic)
*   ✅ `domain/order/order.py` (The Concept Itself)

*   ❌ `domain/auth/helpers.py`
*   ✅ `domain/auth/token.py` (The Concept)

**Exceptions (Foreign Reality):**
*   `api.py`, `db.py`, `vendor.py` are acceptable because they explicitly model the **Boundary** itself. Their "Concept" IS the Interface.

---

## 📂 `src/domain/` (The Core)

This directory is grouped by **Context** (Business Area).

**All domain objects MUST be frozen Pydantic models (`BaseModel`).**

**Allowed File Types per Context:**

1.  **Internal Truth (`entity.py`, `user.py`):**
    *   Frozen Pydantic models.
    *   Defines the language of the business.

2.  **Atoms (`types.py`, `values.py`):**
    *   Context-specific Value Objects (`OrderId`) and Smart Enums (`OrderStatus`).
    *   **Smart Enums:** Define the State Machine Graph and Logic.
    *   Use Pydantic built-ins (`EmailStr`, `PositiveInt`) over hand-rolled validators.

3.  **Foreign Reality (`api.py`, `vendor.py`, `db.py`):**
    *   **`api.py`:** The schema of our own API (Request/Response models).
    *   **`vendor.py`:** The schema of external APIs we consume.
    *   **`db.py`:** The schema of our Database Tables (e.g., `DbOrder`).
    *   All Foreign Models own a `.to_domain()` method.

4.  **Aggregates & Workflows (`workflow.py`, `order.py`):**
    *   Frozen Pydantic models with **decision methods**.
    *   Methods return `Result` (Railway), `Intent` (Execution), or new state.
    *   **Banned:** Side effects (I/O).

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
    *   **Executors:** Service Classes that execute Intents (I/O).
    *   **Runtimes:** Service Classes that drive State Machines (Loops).
*   **Philosophy:** Dumb code. No business rules. Just wiring and execution.
*   **Structure:** **Plain Python Classes**. Dependencies injected via `__init__`.
*   **No Pydantic Models:** Do not use `BaseModel` for Services.

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
import uvicorn
from domain.system.config import AppConfig
from service.order import OrderExecutor, OrderRuntime
from api.app import create_api

def main():
    """
    The Launcher.
    1. Load Config (Crash on Failure)
    2. Wire Services (DI)
    3. Launch Interface (App)
    """
    
    # 1. Load Config (System crashes if env is missing)
    # AppConfig inherits BaseSettings, so it loads from env/files automatically.
    config = AppConfig()
    
    # 2. Wire Dependencies (Service Classes)
    # Executors take Config
    store = OrderExecutor(table_name=config.db.table_name)
    gateway = PaymentGateway(api_key=config.stripe.key)
    
    # Runtimes take Executors
    runtime = OrderRuntime(store=store, gateway=gateway)
    
    # 3. Launch Interface (pass wired services)
    app = create_api(runtime=runtime)
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
```
