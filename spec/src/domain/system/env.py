"""
THE FOREIGN REALITY (EnvVars)

Role: Models the chaotic OS Environment (strings, screaming snake case).
Mandate: Mandate V (Configuration) & VII (Translation).
Pattern: spec/patterns/05-config-injection.md

Constraint:
- Uses Field(alias=...) to map OS names.
- Owns .to_domain() to convert itself into AppConfig.

Example Implementation:
```python
from pydantic import BaseModel, Field
from .config import AppConfig

class EnvVars(BaseModel):
    model_config = {"frozen": True}
    
    def to_domain(self) -> AppConfig:
        return AppConfig(...)
```
"""
