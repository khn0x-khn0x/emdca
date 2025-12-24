---
description: "Pattern 10: Infrastructure — Capability as Data. Domain declares abstract needs, Service binds to technology."
globs: ["**/service/**/*.py", "**/domain/**/store.py", "**/domain/**/failure.py"]
alwaysApply: false
---

# Pattern 10: Infrastructure Capability as Data

## Valid Code Structure

```python
# DOMAIN: Abstract capability (what we need)
# domain/event/store.py
class EventStore(BaseModel):
    """Abstract capability: I need event persistence."""
    model_config = {"frozen": True}
    
    async def append(self, event: Event) -> AppendResult: ...
    async def read(self, stream: str) -> ReadResult: ...

# DOMAIN: Abstract failure modes
# domain/event/failure.py
class EventStoreFailure(StrEnum):
    """How operations can fail (abstract, not tech-specific)."""
    TIMEOUT = "timeout"
    CONNECTION_LOST = "connection_lost"
    NOT_FOUND = "not_found"
    PERMISSION_DENIED = "permission_denied"

# SERVICE: Technology binding (how we provide it)
# service/event.py
class NatsStreamConfig(BaseModel):
    """What NATS expects. Service-layer knowledge."""
    model_config = {"frozen": True}
    
    name: str  # NO DEFAULT
    subjects: tuple[str, ...]  # NO DEFAULT
    retention: Literal["limits", "interest", "workqueue"]  # NO DEFAULT

class NatsEventExecutor(BaseModel):
    """Binds abstract EventStore to NATS."""
    model_config = {"frozen": True}
    
    config: NatsStreamConfig
    
    async def execute(self, intent: EventIntent) -> EventStoreFailure | EventResult:
        # Map NATS exceptions to abstract domain failures
        ...
```

## Constraints

| Required | Forbidden |
|----------|-----------|
| Domain declares abstract capabilities | `import boto3` / `import nats` in domain |
| Failure modes as abstract `StrEnum` | Technology-specific configs in domain |
| Service layer owns tech configs | `NatsStreamConfig` in `domain/` |
| Service layer binds abstract to concrete | `domain/infra/` directory |
| All fields explicit, no defaults | Side effects on model init |
