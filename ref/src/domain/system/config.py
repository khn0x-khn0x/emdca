"""
THE DOMAIN CONFIGURATION (Schema of Environment)

Role: Defines the contract with the environment.
Mandate: Mandate V (Configuration).
Pattern: ref/patterns/05-config-injection.md

Constraint:
- Inherit `BaseSettings` (pydantic-settings).
- Lives in Domain because schema is Domain Knowledge.
- Use `Field(alias=...)` for mapping.
- Crash on instantiation if invalid.

Example Implementation:
```python
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", frozen=True)

    database_url: PostgresDsn = Field(alias="DATABASE_URL")
    api_key: ApiKey = Field(alias="STRIPE_API_KEY")
```
"""
