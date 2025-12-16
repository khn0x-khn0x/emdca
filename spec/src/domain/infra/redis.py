"""
THE INFRASTRUCTURE CAPABILITY (Intents & Topology)

Role: Defines the Intents and Configuration for Redis.
Mandate: Mandate X (Infra as Data) & IV (Intent).
Pattern: spec/patterns/10-infrastructure-capability-as-data.md
Pattern: spec/patterns/04-execution-intent.md

Constraint:
- Intents are Complete Specifications (parameters + on_success/on_failure + catch_exceptions).
- Defines Topology as pure Config models.
- No client libraries (no `redis-py`). Pure Data.

Example Implementation:
```python
from pydantic import BaseModel

class GetIntent(BaseModel):
    key: str
    catch_exceptions: tuple[str, ...] = ("ConnectionError", "TimeoutError")

    def on_success(self, value: bytes | None) -> "ValueRetrieved": ...
    def on_failure(self, error: str) -> "GetFailed": ...
```
"""
