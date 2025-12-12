# Pattern 10: Infrastructure (Capability as Data)

## The Principle
Infrastructure is a capability to be modeled as Data, not a Service to be executed. The Domain defines the *Topology* and *Intent* of the infrastructure as pure values, while the Shell handles the *Runtime Connection*.

## The Mechanism
The Domain defines **Infrastructure Models** describing the shape of resources (e.g., Streams, Buckets) and **Generic Intents** describing desired actions (e.g., Publish, Store). The Shell provides **Executor Adapters** that hold the actual client connections and blindly execute the Intents.

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
    
    def store(self, key: str, data: bytes):
        # ❌ Logic is coupled to network
        self.s3.put_object(Bucket="my-bucket", Key=key, Body=data)
```

---

## 2. Infrastructure as Data (Topology)
We describe *what* the infrastructure looks like using Pydantic models. This allows us to reason about the topology (e.g., validating retention policies) without connecting to it.

### ✅ Pattern: Pure Configuration
```python
from typing import Literal
from pydantic import BaseModel, Field

class NatsStreamConfig(BaseModel):
    model_config = {"frozen": True}
    
    name: str
    subjects: list[str]
    retention: Literal["limits", "interest", "workqueue"]
    max_msgs: int
    max_bytes: int

# Pure Logic: We can validate our topology
def validate_topology(config: NatsStreamConfig) -> bool:
    if config.retention == "workqueue" and len(config.subjects) > 1:
        # Business Rule: Workqueues should have single subjects
        return False
    return True
```

---

## 💡 Spotlight: AI Agents as Infrastructure
An "AI Agent" is often just a configuration of a Model + Tools. We model this as static data.

```python
class AgentConfig(BaseModel):
    model_config = {"frozen": True}
    
    model_name: str = "gpt-4"
    temperature: float = 0.1
    allowed_tools: list[str] = ["calculator", "search"]
    max_steps: int = 5
```

By modeling this as data, we can validate our "Agent Swarm" topology (e.g., "Ensure the Router uses a fast model") before we ever connect to a provider.

---

## 3. The Executor Adapter (The Shell)
The Adapter is the only place where the library (e.g., `nats-py`, `boto3`) is imported. It accepts the Data Definition and performs the side effect.

### ✅ Pattern: The Dumb Adapter
```python
# service/nats_adapter.py (Shell)
import nats

class NatsAdapter:
    def __init__(self, nc: nats.NATS):
        self.nc = nc

    async def ensure_stream(self, config: NatsStreamConfig):
        # 1. Translate Domain Config -> Library Call
        js = self.nc.jetstream()
        
        await js.add_stream(
            name=config.name,
            subjects=config.subjects,
            retention=config.retention, # Maps 1:1
            max_msgs=config.max_msgs,
            max_bytes=config.max_bytes
        )

    async def publish(self, intent: PublishIntent):
        # 2. Execute Intent (Pattern 04)
        await self.nc.publish(intent.subject, intent.payload)
```

---

## 4. Usage in Orchestrator
The Orchestrator loads the config (Data) and passes it to the Adapter (Executor).

```python
async def startup(config: AppConfig):
    # 1. Define Topology (Data)
    stream_conf = NatsStreamConfig(
        name="orders", 
        subjects=["orders.*"],
        retention="limits",
        max_msgs=10000,
        max_bytes=1024*1024
    )

    # 2. Initialize Adapter
    nc = await nats.connect(config.nats_url)
    adapter = NatsAdapter(nc)

    # 3. Apply Topology
    # The adapter makes the real world match the data model
    await adapter.ensure_stream(stream_conf)
```

## 5. Cognitive Checks
*   [ ] **No Libraries:** Did I remove `import boto3`, `import redis` from the `domain/` folder?
*   [ ] **Config vs Client:** Do I pass `StreamConfig` (Data) to logic, never `StreamClient` (Object)?
*   [ ] **Validation:** Can I check if my bucket name is valid without internet access?
