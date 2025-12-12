# Pattern 05: Configuration (Dependency Injection)

## The Principle
A model's behavior should be determined entirely by its inputs, enabling reasoning in isolation. Configuration is a "Foreign Reality" (Environment Variables) that must be translated into an "Internal Truth" (Domain Config) before entering the system.

## The Mechanism
We use the **Foreign Model Pattern** to handle configuration. `EnvVars` models the OS environment (Foreign Reality). `AppConfig` models the application settings (Internal Truth). Translation happens explicitly at the entry point.

---

## 1. The Magic Config (Anti-Pattern)
Libraries that automagically bind `os.environ` to your domain objects create a hidden coupling between your Business Logic and the Operating System.

### ❌ Anti-Pattern: Magic Settings
```python
# BAD: Domain logic depends on OS Environment structure
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Hidden coupling: "Why does my domain need underscores?"
    db_url: str = Field(alias="DATABASE_URL") 

def connect_db(settings: Settings = Settings()):
    # Implicit dependency on global state (os.environ)
    pass
```

---

## 2. The Foreign Reality (EnvVars)
We explicitly model the chaotic reality of the Operating System. This model lives in the System Domain context (`domain/system/`).

### ✅ Pattern: The Environment Model
```python
# src/domain/system/env.py
from pydantic import BaseModel, Field
from .config import AppConfig, DatabaseConfig

class EnvVars(BaseModel):
    """
    The Foreign Model representing the OS Environment.
    It deals with Strings and SCREAMING_SNAKE_CASE.
    """
    model_config = {"frozen": True}
    
    db_url: str = Field(alias="DATABASE_URL")
    debug_mode: str = Field(alias="DEBUG", default="false")
    api_key: str = Field(alias="STRIPE_API_KEY")

    def to_domain(self) -> AppConfig:
        """
        Naturalize the Foreign Reality into Internal Truth.
        """
        return AppConfig(
            database=DatabaseConfig(connection_string=self.db_url),
            # Convert "stringly typed" env vars to real booleans
            is_debug=self.debug_mode.lower() == "true",
            stripe_key=self.api_key
        )
```

---

## 3. The Internal Truth (AppConfig)
The Domain Configuration is a pure, structured object. It has no aliases, no defaults (defaults belong in the Shell/Env), and zero knowledge of `os`.

### ✅ Pattern: The Pure Config
```python
# src/domain/system/config.py
from pydantic import BaseModel

class DatabaseConfig(BaseModel):
    model_config = {"frozen": True}
    connection_string: str

class AppConfig(BaseModel):
    """
    The Internal Truth.
    Pure, Typed, Snake_Case.
    """
    model_config = {"frozen": True}
    
    database: DatabaseConfig
    is_debug: bool
    stripe_key: str
```

---

## 4. Translation at Entry (The Wiring)
Translation happens once, at the very edge of the application (the Composition Root).

### ✅ Pattern: Explicit Loading
```python
# src/main.py
import os
from domain.system.env import EnvVars

def main():
    # 1. Capture Foreign Reality
    raw_env = os.environ
    
    # 2. Translate to Internal Truth
    # This validates that the OS provides what we need
    try:
        config = EnvVars.model_validate(raw_env).to_domain()
    except ValidationError as e:
        print(f"Invalid Environment: {e}")
        exit(1)

    # 3. Inject Truth
    # The app never sees os.environ, only the clean Config
    app = create_app(config)
```

## 5. Cognitive Checks
*   [ ] **Separation:** Do I have separate classes for `EnvVars` (Infra) and `AppConfig` (Domain)?
*   [ ] **System Context:** Does configuration live in `domain/system/`, not `bootstrap/`?
*   [ ] **No Defaults:** Does `AppConfig` have zero default values? (Defaults hide required configuration).
