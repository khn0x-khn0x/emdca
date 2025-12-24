"""
SHARED DEPENDENCIES (Runtime Providers)

Role: Frozen Pydantic models that provide cross-cutting dependencies.
Mandate: Mandate V (Injection).
Structure: ref/structure.md

Constraint:
- Providers are frozen Pydantic models with methods.
- Clock is a frozen Pydantic model, not a Protocol.
- Specific context logic belongs in the Context Router.

Example Implementation:
```python
from pydantic import BaseModel
from datetime import datetime

class Clock(BaseModel):
    model_config = {"frozen": True}

    def now(self) -> datetime:
        return datetime.utcnow()

class AuthProvider(BaseModel):
    model_config = {"frozen": True}
    secret_key: str

    def validate_token(self, token: str) -> "AuthResult":
        # Returns Sum Type: Authenticated | InvalidToken | Expired
        ...

# In composition root (main.py), wire these as fields on orchestrators
# or attach to app.state for route access
```
"""
