# Pattern 10: Infrastructure (Capability as Data)

## The Principle
Infrastructure is a capability to be modeled as **Data**, not a Service to be executed. The Domain defines the *Topology* (Config) and *Intent* (Action) as pure values. The Shell simply "plays back" these values against the real world.

## The Mechanism
1.  **Topology Models:** The Domain defines what infrastructure should exist (e.g., `NatsStreamConfig`).
2.  **Intent Models:** The Domain returns Intents describing side effects (e.g., `EnsureStreamIntent`).
3.  **Shell Execution:** The Service Layer holds the client connection and blindly executes the Intents using the generic executor.

---

## 1. The Active Client (Anti-Pattern)
Instantiating heavy clients or connections inside the domain couples the logic to the runtime environment.

### ❌ Anti-Pattern: Connection in Domain
```python
import boto3

class StorageService:
    def __init__(self):
        # ❌ Side Effect: Connects to AWS on init
        self.s3 = boto3.client("s3")
```

---

## 2. Infrastructure as Data (Topology)
We describe *what* the infrastructure looks like using Pydantic models. This allows us to reason about the topology (e.g., validating retention policies) without connecting to it.

### ✅ Pattern: Pure Configuration (Streams)
```python
# domain/system/topology.py
from typing import Literal
from pydantic import BaseModel

class NatsStreamConfig(BaseModel):
    model_config = {"frozen": True}
    
    name: str
    subjects: list[str]
    retention: Literal["limits", "interest", "workqueue"]
```

### ✅ Pattern: Pure Configuration (Agents)
An "AI Agent" is just a configuration of a Model + Tools.
```python
class AgentTopology(BaseModel):
    model_config = {"frozen": True}
    
    role_name: str = "customer_support"
    model_name: str = "gpt-4"
    temperature: float = 0.1
```

---

## 3. The Specification (Intent)
Infrastructure setup is a side effect. It succeeds or fails. The Domain must own the interpretation of those outcomes using an Intent Contract (Pattern 04).

### ✅ Pattern: The Setup Intent
```python
# domain/infra/topology.py
from typing import Any, Literal

class EnsureStreamIntent(BaseModel):
    model_config = {"frozen": True}
    
    config: NatsStreamConfig
    catch_exceptions: tuple[str, ...] = ("TimeoutError", "ConnectionClosedError")
    
    def on_success(self) -> "StreamReady":
        """No return value needed from add_stream — success is implicit."""
        return StreamReady(stream_name=self.config.name)
    
    def on_failure(self, error: str) -> "StreamSetupFailed":
        return StreamSetupFailed(stream_name=self.config.name, error=error)

class StreamReady(BaseModel):
    kind: Literal["ready"] = "ready"
    stream_name: str

class StreamSetupFailed(BaseModel):
    kind: Literal["failed"] = "failed"
    stream_name: str
    error: str

type EnsureStreamResult = StreamReady | StreamSetupFailed

class ConnectIntent(BaseModel):
    model_config = {"frozen": True}
    
    url: str
    timeout_seconds: float = 5.0
    catch_exceptions: tuple[str, ...] = ("NoServersError", "TimeoutError", "OSError")
    
    def on_success(self, client_id: str) -> "Connected":
        """Receives extracted primitive, not raw client object."""
        return Connected(url=self.url, client_id=client_id)
    
    def on_failure(self, error: str) -> "ConnectionFailed":
        return ConnectionFailed(url=self.url, error=error)

class Connected(BaseModel):
    kind: Literal["connected"] = "connected"
    url: str
    client_id: str

class ConnectionFailed(BaseModel):
    kind: Literal["connection_failed"] = "connection_failed"
    url: str
    error: str

type ConnectResult = Connected | ConnectionFailed
```

---

## 4. Usage in Startup (Composition Root)
Even `main.py` is an Orchestrator. It loads the config, defines the Intent, and executes it using the generic executor. It does **not** call library methods directly.

```python
# main.py
async def startup(config: AppConfig):
    # 1. Connect (Intent-Based)
    connect_intent = ConnectIntent(url=config.nats_url)
    
    # Shell retains raw client; Domain gets clean result
    nc = None
    
    async def do_connect():
        nonlocal nc
        nc = await nats.connect(connect_intent.url)
        return nc
    
    conn_result = await execute(
        operation=do_connect,
        catch_names=connect_intent.catch_exceptions,
        # Shell extracts client_id from raw nats client
        on_success=lambda nc: connect_intent.on_success(client_id=str(nc.client_id)),
        on_failure=connect_intent.on_failure,
    )

    match conn_result:
        case ConnectionFailed(error=e):
            sys.exit(f"Failed to connect: {e}")
        case Connected():
            pass  # nc is now set
            
    js = nc.jetstream()

    # 2. Define Intent (Pure Data)
    intent = EnsureStreamIntent(
        config=NatsStreamConfig(
            name="orders", 
            subjects=["orders.*"],
            retention="limits"
        )
    )

    # 3. Execute (Generic Shell)
    # The Shell reads the contract and applies it.
    result = await execute(
        operation=lambda: js.add_stream(
            name=intent.config.name,
            subjects=intent.config.subjects,
            retention=intent.config.retention,
        ),
        catch_names=intent.catch_exceptions,
        on_success=lambda _: intent.on_success(),  # No extraction needed
        on_failure=intent.on_failure,
    )

    # 4. Handle Outcome
    match result:
        case StreamReady():
            pass  # Continue startup
        case StreamSetupFailed(error=e):
            sys.exit(f"Infrastructure setup failed: {e}")
```

## 5. Cognitive Checks
*   [ ] **No Libraries:** Did I remove `import boto3` from the `domain/` folder?
*   [ ] **Intent-Based Setup:** Do I use `EnsureStreamIntent` instead of calling `ensure_topology()` directly?
*   [ ] **Intent-Based Connection:** Does initial connection use `ConnectIntent`, not a direct call?
*   [ ] **Outcome Ownership:** Does the Domain define what `StreamSetupFailed` looks like?
*   [ ] **Generic Execution:** Could I switch the executor implementation without changing the Intent?
