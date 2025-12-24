---
description: "Pattern 01: Construction — Parse, don't validate. Factory methods on frozen models."
globs: ["**/domain/**/*.py", "**/entity.py"]
alwaysApply: false
---

# Pattern 01: Factory Construction

## Valid Code Structure

```python
# Value Objects: Use Pydantic built-ins
class User(BaseModel):
    model_config = {"frozen": True}
    email: EmailStr  # NOT str
    age: PositiveInt  # NOT int

# Result Types: Explicit success/failure
class UserCreated(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["created"]  # NO DEFAULT
    user: User

class UserRejected(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["rejected"]  # NO DEFAULT
    reason: str

type CreateUserResult = UserCreated | UserRejected

# Factory: Method on a model, returns Result
class UserFactory(BaseModel):
    model_config = {"frozen": True}
    
    def create(self, raw: RawUserData) -> CreateUserResult:
        if raw.age < 18:
            return UserRejected(kind="rejected", reason="Must be 18+")
        return UserCreated(kind="created", user=User(email=raw.email, age=raw.age))
```

## Constraints

| Required | Forbidden |
|----------|-----------|
| `model_config = {"frozen": True}` | Default values on fields |
| `EmailStr`, `PositiveInt` (Pydantic built-ins) | `str`, `int` for domain concepts |
| Factory as method on model | Standalone `def create_user()` functions |
| Return `Success \| Failure` Sum Type | `raise ValueError()` |
| `kind: Literal["..."]` explicit | `kind: Literal["..."] = "..."` |

