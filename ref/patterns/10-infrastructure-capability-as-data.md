# Pattern 10: Infrastructure (Capability as Data)

## The Principle
Domain contexts define abstract capabilities they need (event persistence, object storage). The Service layer binds those capabilities to specific technologies. The Domain never knows it's using NATS, S3, or Redis—it only knows it needs to persist events or store objects.

## The Mechanism
1. **Domain Capabilities:** Abstract models declaring what the domain needs (EventStore, ObjectStore)
2. **Domain Failure Models:** Smart Enums enumerating how operations can fail (abstract, not tech-specific)
3. **Service Binding:** Service layer defines technology-specific configs and executors

The Domain never imports infrastructure libraries. It declares abstract needs.

---

## ❌ Anti-Pattern: Connection in Domain

Instantiating clients inside the domain couples logic to the runtime environment.

```python
import boto3

class StorageService:
    def __init__(self):
        self.s3 = boto3.client("s3")  # ❌ Side effect on init
```

---

## ❌ Anti-Pattern: Technology Config in Domain

Technology-specific configuration is infrastructure knowledge, not domain knowledge.

```python
# ❌ WRONG: This is NATS knowledge, not domain knowledge
# domain/infra/nats.py  <-- This file should not exist
class NatsStreamConfig(BaseModel):
    name: str
    subjects: tuple[str, ...]
    retention: Literal["limits", "interest", "workqueue"]  # NATS concept
```

---

## ✅ Pattern: Abstract Domain Capability

The domain declares WHAT it needs, not HOW infrastructure provides it.

```python
# domain/event/store.py
class EventStore(BaseModel):
    """Abstract capability: I need event persistence."""
    model_config = {"frozen": True}
    
    async def append(self, event: Event) -> AppendResult:
        """Append event. Implementation injected."""
        ...

    async def read(self, stream: str) -> ReadResult:
        """Read events. Implementation injected."""
        ...
```

---

## ✅ Pattern: Abstract Failure Model

Model how operations can fail in abstract terms. The Shell maps technology exceptions to these.

```python
# domain/event/failure.py
class EventStoreFailure(StrEnum):
    """How event operations can fail (abstract)."""
    TIMEOUT = "timeout"
    CONNECTION_LOST = "connection_lost"
    NOT_FOUND = "not_found"
    PERMISSION_DENIED = "permission_denied"
```

---

## ✅ Pattern: Technology Binding in Service

The service layer owns technology knowledge. It binds abstract capabilities to concrete implementations.

```python
# service/event.py
from domain.event.store import EventStore
from domain.event.failure import EventStoreFailure

# Technology-specific config lives HERE, not in domain
class NatsStreamConfig(BaseModel):
    """What NATS expects. This is service-layer knowledge."""
    model_config = {"frozen": True}
    
    name: str
    subjects: tuple[str, ...]
    retention: Literal["limits", "interest", "workqueue"]

class NatsEventExecutor(BaseModel):
    """Binds abstract EventStore to NATS."""
    model_config = {"frozen": True}
    
    config: NatsStreamConfig
    
    async def execute(self, intent: EventIntent) -> EventStoreFailure | EventResult:
        # Map NATS exceptions to abstract failures
        ...
```

---

## Cognitive Checks

- [ ] **No Libraries in Domain:** Did I remove `import boto3` / `import nats` from `domain/`?
- [ ] **No Tech Configs in Domain:** Is `NatsStreamConfig` / `S3BucketConfig` in `service/`, not `domain/`?
- [ ] **Domain is Abstract:** Does domain only declare capabilities (EventStore), not tech bindings?
- [ ] **Failures are Abstract:** Are failure modes tech-agnostic (timeout, not NatsTimeout)?
- [ ] **Service Binds:** Does the service layer own the technology-specific configuration?
