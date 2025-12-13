"""
THE INTERNAL TRUTH (AppConfig)

Role: Defines the structured, type-safe configuration for the application.
Mandate: Mandate V (Configuration).
Pattern: spec/patterns/05-config-injection.md

Constraint:
- Must be frozen (immutable).
- No default values (defaults belong in Env/Shell).
- No knowledge of os.environ.

Example Implementation:
```python
from pydantic import BaseModel

class AppConfig(BaseModel):
    model_config = {"frozen": True}
    # ... defined fields ...
```
"""
