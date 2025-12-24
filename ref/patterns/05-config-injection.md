# Pattern 05: Configuration (Dependency Injection)

## The Principle
A model's behavior should be determined entirely by its inputs, enabling reasoning in isolation. Configuration is a "Foreign Reality" (Environment Variables) that must be translated into an "Internal Truth" (Domain Config) before entering the system.

## The Mechanism
We use the **Foreign Model Pattern** to handle configuration. `EnvVars` models the OS environment (Foreign Reality). `AppConfig` models the application settings (Internal Truth). Translation happens explicitly at the composition root.

---

## 1. The Magic Config (Anti-Pattern)
Libraries that automagically bind `os.environ` to your domain objects create hidden coupling.

### ❌ Anti-Pattern: Magic Settings
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_url: str = Field(alias="DATABASE_URL")  # ❌ Hidden coupling

def connect_db(settings: Settings = Settings()):  # ❌ Implicit global state
    pass
```

---

## 2. The Foreign Reality (EnvVars)
We explicitly model the OS environment. All fields required—no defaults.

### ✅ Pattern: The Environment Model
```python
from pydantic import BaseModel, Field

class EnvVars(BaseModel):
    """Foreign Model: The OS Environment."""
    model_config = {"frozen": True}
    
    db_url: str = Field(alias="DATABASE_URL")
    debug_mode: str = Field(alias="DEBUG")  # NO DEFAULT—required
    api_key: str = Field(alias="STRIPE_API_KEY")

    def to_domain(self) -> "AppConfig":
        return AppConfig(
            database=DatabaseConfig(connection_string=self.db_url),
            is_debug=self.debug_mode.lower() == "true",
            stripe_key=self.api_key,
        )
```

---

## 3. The Internal Truth (AppConfig)
The Domain Configuration is pure, structured, with no aliases, no defaults, and zero knowledge of `os`.

### ✅ Pattern: The Pure Config
```python
class DatabaseConfig(BaseModel):
    model_config = {"frozen": True}
    connection_string: str

class AppConfig(BaseModel):
    """Internal Truth: Pure, Typed."""
    model_config = {"frozen": True}
    
    database: DatabaseConfig
    is_debug: bool
    stripe_key: str
```

---

## 4. Config Parsing Result (Sum Type)
Model config loading success or failure explicitly.

### ✅ Pattern: Config Result
```python
from typing import Literal

class ConfigLoaded(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["loaded"]
    config: AppConfig

class ConfigInvalid(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["invalid"]
    errors: tuple[str, ...]

type ConfigResult = ConfigLoaded | ConfigInvalid
```

---

## 5. Translation at Entry (Composition Root)
The composition root is the **ONE place** where standalone wiring exists. It captures raw env, parses to Foreign Model, translates to domain.

### ✅ Pattern: Explicit Loading
```python
# src/main.py — Composition Root (the ONE exception)
import os
from pydantic import ValidationError

def load_config(raw_env: dict) -> ConfigResult:
    """Parse environment into config. No exceptions escape."""
    try:
        config = EnvVars.model_validate(raw_env).to_domain()
        return ConfigLoaded(kind="loaded", config=config)
    except ValidationError as e:
        errors = tuple(str(err) for err in e.errors())
        return ConfigInvalid(kind="invalid", errors=errors)


# Composition root wiring
raw_env = dict(os.environ)
result = load_config(raw_env)

match result:
    case ConfigInvalid(errors=errs):
        print(f"Invalid config: {errs}")
        exit(1)
    case ConfigLoaded(config=cfg):
        app = create_app(cfg)
```

---

## Cognitive Checks
- [ ] **Separation:** Do I have separate `EnvVars` (Foreign) and `AppConfig` (Domain)?
- [ ] **No Defaults in Domain:** Does `AppConfig` have zero default values?
- [ ] **No Defaults in Foreign:** Does `EnvVars` require all fields explicitly?
- [ ] **Result Type:** Is config parsing modeled as `ConfigLoaded | ConfigInvalid`?
- [ ] **Composition Root:** Is try/except ONLY in the composition root?
