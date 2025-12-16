"""
THE INFRASTRUCTURE CAPABILITY (Intents & Topology)

Role: Defines the Intents and Configuration for NATS.
Mandate: Mandate X (Infra as Data) & IV (Intent).
Pattern: spec/patterns/10-infrastructure-capability-as-data.md
Pattern: spec/patterns/04-execution-intent.md

Constraint:
- Intents are Complete Specifications (parameters + on_success/on_failure + catch_exceptions).
- Defines Topology as pure Config models (StreamConfig).
- No client libraries (no `nats-py`). Pure Data.

Example Implementation:
```python
from pydantic import BaseModel

class ConnectIntent(BaseModel):
    url: str
    catch_exceptions: tuple[str, ...] = ("NoServersError", "TimeoutError")

    def on_success(self, client_id: str) -> "Connected": ...
    def on_failure(self, error: str) -> "ConnectionFailed": ...
```
"""
