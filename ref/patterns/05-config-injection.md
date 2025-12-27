# Pattern 05: Configuration (Dependency Injection)

## The Principle
Configuration is the **Schema of the Environment**. Just as we define schemas for API requests, we define a schema for the process environment.

We use `pydantic-settings` to define this schema directly. The `AppConfig` model **IS** the Domain's definition of what it needs from the outside world.

## The Mechanism
1.  **AppConfig (`BaseSettings`):** A single Pydantic model that defines all configuration.
2.  **Declarative Mapping:** We use `Field(alias=...)` to map external names (`DB_URL`) to internal names (`db_url`).
3.  **Automatic Loading:** Pydantic handles the I/O (env vars, .env files) at instantiation.

---

## 1. The Magic Injection (Anti-Pattern)
Using `os.environ` directly couples every file to the global state.

### ❌ Anti-Pattern: Scattered Truth
```python
def connect_db():
    # ❌ Logic pulls from global environment secretly
    url = os.environ["DATABASE_URL"] 
```

---

## 2. The Config Model (AppConfig)
We define the configuration explicitly in the Domain. This acts as the **Foreign Model** for the Environment. Note the use of specialized types like `PostgresDsn` and `ApiKey` instead of raw strings.

### ✅ Pattern: Single Source of Truth
```python
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppConfig(BaseSettings):
    """
    Defines the contract: The Environment MUST provide these values.
    """
    model_config = SettingsConfigDict(env_file=".env", frozen=True)
    
    # External Name (alias) -> Internal Name (field)
    database_url: PostgresDsn = Field(alias="DATABASE_URL")
    api_key: ApiKey = Field(alias="STRIPE_API_KEY")
    environment: EnvName = Field(alias="ENV", default=EnvName.PROD)
```

---

## 3. Composition Root (Crash on Failure)
We load config **once** at startup. If the environment does not satisfy the schema (missing vars), the application **CRASHES**. This is "Correctness by Construction" applied to the runtime environment.

### ✅ Pattern: Explicit Loading
```python
def main():
    # 1. Load & Validate
    # If DATABASE_URL is missing, this raises ValidationError and crashes. Good.
    config = AppConfig()
    
    # 2. Inject into Service Layer
    db = Database(url=config.database_url)
    
    # 3. Inject into Domain (if needed, though Domain usually takes args)
    # logic.do_thing(config.api_key)
```

---

## Cognitive Checks
- [ ] **One Model:** Is there one `AppConfig` inheriting `BaseSettings`?
- [ ] **Aliases:** Are `Field(alias=...)` used to map external names?
- [ ] **Frozen:** Is `frozen=True` set?
- [ ] **Typed Config:** Do I use `PostgresDsn`, `RedisDsn`, `ApiKey` instead of `str`?
- [ ] **Crash Early:** Does `main()` instantiate it immediately?
