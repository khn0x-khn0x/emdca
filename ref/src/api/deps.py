"""
SHARED DEPENDENCIES (Runtime Providers)

Role: Service Classes that provide cross-cutting dependencies.
Mandate: Mandate V (Injection).
Structure: ref/structure.md

Constraint:
- Providers are Regular Python Classes (Not Pydantic Models).
- Injected via `__init__` or passed as arguments.
- Clock is a Service Class.

Example Implementation:
```python
from datetime import datetime

class Clock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)

class AuthProvider:
    def __init__(self, secret_key: SecretKey):
        self.secret_key = secret_key

    def validate_token(self, token: AuthToken) -> "AuthResult":
        # Returns Sum Type: Authenticated | InvalidToken | Expired
        ...
```
"""
