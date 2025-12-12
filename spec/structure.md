# Structure Guide: Contextual Co-location

**The Principle:** The location of a file dictates its capabilities. We organize by **Context** (Vertical Slice), not by **Layer** (Horizontal Slice).

Traditional architectures separate "Adapters" from "Entities" into distant folders. EMDCA rejects this. Knowledge of an external system (e.g., Coinbase) is **Domain Knowledge** and must live inside the Domain Context that uses it.

---

## 🏗️ The File Hierarchy

```text
src/
├── domain/                  # THE CORE (Pure, Vertical Slices)
│   ├── trade/               # Context: Trading
│   │   ├── candle.py        # Internal Truth (Domain Models)
│   │   ├── coinbase.py      # Foreign Reality (Foreign Models / Adapters)
│   │   └── logic.py         # Pure Logic (Factories)
│   │
│   └── system/              # Context: System Capabilities (formerly 'bootstrap')
│       ├── config.py        # Internal Truth (AppConfig)
│       └── env.py           # Foreign Reality (EnvVars)
│
├── service/                 # THE ORCHESTRATOR (Impure, Horizontal)
│   ├── trade_service.py     # Procedural Loops / Consumers
│   └── app_service.py       # Composition Root
│
└── api/                     # THE INTERFACE (Impure, Horizontal)
    ├── routes.py            # HTTP Entrypoints
    └── main.py              # FastAPI App Definition
```

---

## 📐 The Dependency Rule

Imports must strictly flow **inward** toward the Domain.

*   ✅ `service/` imports `domain/`
*   ✅ `api/` imports `service/` and `domain/`
*   ❌ `domain/` **NEVER** imports `service/` or `api/`
*   ❌ Contexts (e.g., `trade/`) should minimize imports from other contexts (use ID references).

---

## 📂 `src/domain/` (The Core)

This directory is grouped by **Context** (Business Area). Each folder represents a bounded context (e.g., `trade/`, `identity/`, `payment/`).

**Allowed File Types per Context:**

1.  **Internal Truth (`model.py`, `candle.py`):**
    *   Pure Pydantic models.
    *   Defines the language of the business.
    *   No external dependencies.

2.  **Foreign Reality (`foreign.py`, `coinbase.py`, `stripe.py`):**
    *   **Foreign Models** that mirror external APIs.
    *   **Infrastructure Definitions** (e.g., `NatsStreamConfig`).
    *   This is where "Adapters" live. Knowing the shape of Coinbase data is Domain Knowledge.

3.  **Pure Logic (`logic.py`, `factory.py`):**
    *   Pure functions.
    *   Input: `ForeignModel` or `DomainModel`.
    *   Output: `Result`, `Intent`, or `NewState`.

---

## 📂 `src/domain/system/` (The Foundation)

We treat the System itself (Startup, Config, Environment) as just another Domain Context.

*   **`env.py` (Foreign Reality):** Models the `os.environ` variables using Pydantic. Defines the chaotic input.
*   **`config.py` (Internal Truth):** Defines the structured `AppConfig`.
*   **Replaces:** The traditional `bootstrap/`, `settings/`, or `conf/` folders.

---

## 📂 `src/service/` (The Orchestrator)

The Service Layer acts as the "Roadie." It connects the pipes.

*   **Responsibility:** Fetch Data -> Call Logic -> Save Data.
*   **Contains:** Procedural loops, Transaction management, Event Consumers.
*   **Philosophy:** Dumb code. No business rules.

---

## 📂 `src/api/` (The Interface)

The entry point for external traffic (HTTP/GRPC).

*   **Responsibility:** Receive Request -> Delegate to Service -> Return Response.
*   **Contains:** FastAPI Routes, DTOs (if strict separation is needed), Dependencies.

---

## ⚡ The Composition Root (`src/api/main.py`)

This is the **Big Bang**. It is the only place in the system where imports cross every boundary. Its job is to turn **Foreign Reality** (Env) into **Internal Truth** (Config) and wire the **Services** together.

**The Template:**

```python
# src/api/main.py
import os
import sys
from fastapi import FastAPI
from domain.system.env import EnvVars

# Import your Contexts (The Features)
from api.trade.routes import router as trade_router
from api.identity.routes import router as identity_router

def create_app() -> FastAPI:
    """
    The Composition Root.
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
    # Instantiate adapters using the clean Config
    # db = PostgresClient(config.db_url)
    # nats = NatsClient(config.nats_url)
    
    # 4. Wiring (Services)
    # Inject adapters into services
    # svc = TradeService(repo=db, stream=nats)

    # 5. Launch Interface
    app = FastAPI(title=config.app_name, debug=config.is_debug)
    
    # Register Routes
    app.include_router(trade_router)
    app.include_router(identity_router)
    
    return app

# The Entrypoint
app = create_app()
```

---

## 🗺️ Migration Guide

| If you are looking for... | Go to... |
| :--- | :--- |
| `src/adapters/coinbase.py` | `src/domain/trade/coinbase.py` |
| `src/bootstrap/settings.py` | `src/domain/system/config.py` |
| `src/core/entities/user.py` | `src/domain/identity/user.py` |
| `src/ports/repository.py` | `src/domain/trade/repository.py` (Protocol definition) |

