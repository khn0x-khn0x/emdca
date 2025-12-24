# Pattern 01: Construction (The Pure Factory)

## The Principle
Validation is not a check; it is a construction process. Logic is a calculation, not an action. Therefore, the code that makes decisions must be separated from the code that executes them.

## The Mechanism
All data enters the domain through **Pure Factory Methods** on frozen Pydantic models. These methods accept raw, unstructured data and "parse" it into a valid Domain Type. If the data is invalid, the factory returns a Failure Type. The factory handles every possible input state (Total Function).

---

## 1. The Foundation: Value Objects
Before constructing entities, we must parse primitives into **Value Objects** that carry structural proofs of validity. Primitive Obsession (passing raw strings) is forbidden.

### ❌ Anti-Pattern: Primitive Obsession with Runtime Checks
```python
class User(BaseModel):
    email: str
    
    def validate(self):
        if "@" not in self.email:
            raise ValueError("Invalid email")  # ❌ Runtime check, not construction
```

### ✅ Pattern: Valid-By-Construction Types
Use Pydantic's built-in types. No hand-rolled validators.

```python
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    model_config = {"frozen": True}
    
    id: int
    email: EmailStr  # Pydantic built-in—guarantees validity
```

---

## 2. The Pure Factory: Handling Failure
When constructing complex aggregates, we never raise exceptions. We return a **Result** that explicitly models success or failure.

### ❌ Anti-Pattern: Raising Exceptions
```python
def create_user(data: dict) -> User:
    if data['age'] < 18:
        raise ValueError("Too young")  # ❌ Implicit failure path
    return User(**data)
```

### ✅ Pattern: Explicit Result Types
Use a Discriminated Union to force the caller to handle the failure case. Factory is a method on a model.

```python
from typing import Literal
from pydantic import BaseModel, EmailStr

# 1. Define the Success and Failure Contexts
class UserCreated(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["created"]  # NO DEFAULT
    user: User

class UserRejected(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["rejected"]  # NO DEFAULT
    reason: str

type CreateUserResult = UserCreated | UserRejected


# 2. Raw input as Foreign Model (validates at edge)
class RawUserData(BaseModel):
    """Foreign Model: Raw input from external source."""
    model_config = {"frozen": True}
    
    id: int
    email: EmailStr  # Validated at infrastructure edge
    age: int


# 3. Factory as method on a model
class UserFactory(BaseModel):
    """Factory model with creation method."""
    model_config = {"frozen": True}
    
    def create(self, raw: RawUserData) -> CreateUserResult:
        # Domain Rules only—email already valid by construction
        if raw.age < 18:
            return UserRejected(kind="rejected", reason="User must be 18+")
        
        # Pure construction—no validation needed, types guarantee it
        user = User(id=raw.id, email=raw.email)
        return UserCreated(kind="created", user=user)
```

---

## 3. Explicit Construction (No Defaults)
Domain Models must describe the *Shape* of data, not the *Rules* of data. Default values are hidden business rules.

### ❌ Anti-Pattern: Implicit Defaults
```python
class Order(BaseModel):
    status: str = "pending"  # ❌ Rule buried in schema
    created_at: datetime = Field(default_factory=datetime.now)  # ❌ Side effect
```

### ✅ Pattern: Explicit Factory
The Schema is dumb. The Factory is smart.

```python
class Order(BaseModel):
    model_config = {"frozen": True}
    status: OrderStatus  # No default
    created_at: datetime  # No default


class OrderFactory(BaseModel):
    model_config = {"frozen": True}
    clock: Clock  # Injected dependency
    
    def create(self, user: User) -> Order:
        return Order(
            status=OrderStatus.PENDING,
            created_at=self.clock.now(),
        )
```

---

## Cognitive Checks
- [ ] **No Defaults:** Did I remove all `= "default"` assignments in my Domain Models?
- [ ] **No Hand-Rolled Validators:** Am I using `EmailStr`, `PositiveInt`, etc. instead of `AfterValidator`?
- [ ] **Factory is a Model:** Is my factory a method on a `BaseModel`, not a standalone function?
- [ ] **No try/except:** Does the factory return Result types without catching exceptions?
- [ ] **Immutable Output:** Is `model_config = {"frozen": True}` set on all models?
