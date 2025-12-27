# Pattern 01: Construction (The Pure Factory)

## The Principle
Validation is not a check; it is a construction process. Logic is a calculation, not an action.
In EMDCA, Construction is also where **Capabilities** are injected into the Domain Model. A Model is not ready until it has both its **Data** (Identity) and its **Tools** (Capabilities).

## The Mechanism
1.  **Parse Data:** Use Pydantic to validate raw input into Value Objects.
2.  **Inject Capabilities:** Pass Infrastructure Clients (wrapped in Models) into the Domain Model.
3.  **Return Active Model:** The result is a fully empowered Agent, ready to act.

---

## 1. The Foundation: Value Objects
Before constructing entities, we must parse primitives into **Value Objects**.

### ✅ Pattern: Valid-By-Construction Types
```python
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    model_config = {"frozen": True}
    
    id: UserId
    email: EmailStr  # Pydantic built-in—guarantees validity
```

---

## 2. The Smart Constructor (Factory)
We do not just "validate data"; we **assemble the machine**.

### ❌ Anti-Pattern: Manual Validation
```python
def create_user(data: dict):
    if data['age'] < 18: raise ValueError("Too young")
    return User(**data)
```

### ✅ Pattern: Assembly
The Factory parses data and injects the Capability.

```python
from enum import StrEnum
from pydantic import BaseModel, Field, EmailStr

# 1. Define Components
class AdultAge(BaseModel):
    model_config = {"frozen": True}
    value: int = Field(ge=18)

class UserData(BaseModel):
    """Pure Data State."""
    model_config = {"frozen": True}
    email: EmailStr
    age: AdultAge

# 2. Define Active Model
class User(BaseModel):
    """Active Agent = Data + Capability."""
    model_config = {"frozen": True}
    
    data: UserData
    emailer: EmailCapability  # Injected Tool

    def signup(self):
        self.emailer.send(self.data.email, "Welcome!")

# 3. The Factory (Assembly)
class UserFactory:
    """Namespace for assembly logic."""
    
    @staticmethod
    def create(raw: dict, emailer: EmailCapability) -> User:
        # 1. Parse Data (Crash on Failure)
        data = UserData.model_validate(raw)
        
        # 2. Inject Capability
        return User(data=data, emailer=emailer)
```

---

## Cognitive Checks
- [ ] **No Validation Methods:** Did I remove `.validate()` or `.check()`?
- [ ] **Type Constraints:** Is the rule encoded in `Field(...)` or a Value Object?
- [ ] **Crash on Invalid:** Do I allow Pydantic to raise `ValidationError`?
- [ ] **Capability Injection:** Does the Factory inject the tools needed for the Model to be Active?
- [ ] **Pure Class:** Is the factory a plain class or static method?
