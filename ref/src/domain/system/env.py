"""
THE FOREIGN REALITY (EnvVars)

Role: Models the chaotic OS Environment (strings, screaming snake case).
Mandate: Mandate V (Configuration) & VII (Translation).
Pattern: ref/patterns/05-config-injection.md

Constraint:
- Uses Field(alias=...) to map OS names.
- Owns .to_config() returning a Sum Type (ConfigValid | ConfigInvalid).
- Translation failures are data, not exceptions.

Example Implementation:
```python
from pydantic import BaseModel, Field
from typing import Literal
from .config import AppConfig

class ConfigValid(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["valid"]
    config: AppConfig

class ConfigInvalid(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["invalid"]
    errors: tuple[str, ...]

type ConfigResult = ConfigValid | ConfigInvalid

class EnvVars(BaseModel):
    model_config = {"frozen": True}
    nats_url: str = Field(alias="NATS_URL")
    redis_url: str = Field(alias="REDIS_URL")
    debug_mode: str = Field(alias="DEBUG_MODE")

    def to_config(self) -> ConfigResult:
        # Parse and validate, return Sum Type
        ...
        return ConfigValid(kind="valid", config=AppConfig(...))
```
"""
