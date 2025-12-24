---
description: "Pattern 05: Configuration — EnvVars as Foreign Reality, AppConfig as Internal Truth."
globs: ["**/config.py", "**/env.py", "**/main.py", "**/system/**/*.py"]
alwaysApply: false
---

# Pattern 05: Config Injection

## Valid Code Structure

```python
# Foreign Reality: Models the OS environment
class EnvVars(BaseModel):
    model_config = {"frozen": True}
    
    db_url: str = Field(alias="DATABASE_URL")  # NO DEFAULT
    debug_mode: str = Field(alias="DEBUG")  # NO DEFAULT
    api_key: str = Field(alias="STRIPE_API_KEY")  # NO DEFAULT
    
    def to_domain(self) -> "AppConfig":
        return AppConfig(
            database=DatabaseConfig(connection_string=self.db_url),
            is_debug=self.debug_mode.lower() == "true",
            stripe_key=self.api_key,
        )

# Internal Truth: Pure domain config
class AppConfig(BaseModel):
    model_config = {"frozen": True}
    
    database: DatabaseConfig  # NO DEFAULT
    is_debug: bool  # NO DEFAULT
    stripe_key: str  # NO DEFAULT

# Config Result: Sum Type
class ConfigLoaded(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["loaded"]
    config: AppConfig

class ConfigInvalid(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["invalid"]
    errors: tuple[str, ...]

type ConfigResult = ConfigLoaded | ConfigInvalid

# Composition Root: The ONE place try/except is allowed
def load_config(raw_env: dict) -> ConfigResult:
    try:
        config = EnvVars.model_validate(raw_env).to_domain()
        return ConfigLoaded(kind="loaded", config=config)
    except ValidationError as e:
        return ConfigInvalid(kind="invalid", errors=tuple(str(err) for err in e.errors()))
```

## Constraints

| Required | Forbidden |
|----------|-----------|
| Separate `EnvVars` (Foreign) and `AppConfig` (Domain) | `BaseSettings` magic binding |
| `Field(alias=...)` for env var names | `os.environ` access in domain |
| `.to_domain()` translation method | Default values in config |
| `ConfigLoaded \| ConfigInvalid` Sum Type | Implicit config failures |
| `try/except` ONLY in composition root | `try/except` anywhere else |

