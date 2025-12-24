"""
THE INTERNAL TRUTH (AppConfig)

Role: Defines the structured, type-safe configuration for the application.
Mandate: Mandate V (Configuration).
Pattern: ref/patterns/05-config-injection.md

Constraint:
- Must be frozen (immutable).
- No default values (defaults belong in Env/Shell).
- No knowledge of os.environ.

Example Implementation:
```python
from pydantic import BaseModel, HttpUrl

class AppConfig(BaseModel):
    model_config = {"frozen": True}
    nats_url: HttpUrl
    redis_url: HttpUrl
    debug_mode: bool
    # No defaults — caller must provide all values
```
"""
