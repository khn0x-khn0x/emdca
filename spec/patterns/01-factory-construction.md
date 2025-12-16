# Pattern 01: Construction (The Pure Factory)

## The Principle
Validation is not a check; it is a construction process. Logic is a calculation, not an action. Therefore, the code that makes decisions must be separated from the code that executes them.

## The Mechanism
All data enters the domain through **Pure Factory Functions**. These functions accept raw, unstructured data and "parse" it into a valid Domain Type. If the data is invalid, the factory returns a Failure Type. The factory handles every possible input state (Total Function).

---

## 1. The Foundation: Value Objects
Before constructing entities, we must parse primitives into **Value Objects** that carry structural proofs of validity. Primitive Obsession (passing raw strings) is forbidden.

### ❌ Anti-Pattern: Primitive Obsession with Runtime Checks
```python
# BAD: Data is just a string; validity is a transient runtime check
class User(BaseModel):
    email: str
    
    def validate(self):
        if "@" not in self.email:
            raise ValueError("Invalid email")
```

### ✅ Pattern: Valid-By-Construction Types
Use `Annotated` with `AfterValidator` (Pydantic V2) or custom `__init__` logic to ensure the type *cannot exist* in an invalid state.

```python
from typing import Annotated
from pydantic import BaseModel, Field, AfterValidator

# 1. Define the parsing logic
def parse_email(v: str) -> str:
    if "@" not in v:
        raise ValueError("Invalid email format")
    return v.lower()

# 2. Define the Type
type EmailAddress = Annotated[str, AfterValidator(parse_email)]

# 3. Use it in a frozen model
class User(BaseModel):
    model_config = {"frozen": True}
    
    id: int
    email: EmailAddress  # This field GUARANTEES validity
```

---

## 2. The Pure Factory: Handling Failure
When constructing complex aggregates, we never raise exceptions. We return a **Result** that explicitly models success or failure.

### ❌ Anti-Pattern: Raising Exceptions
```python
# BAD: Control flow is invisible (exceptions)
def create_user(data: dict) -> User:
    if data['age'] < 18:
        raise ValueError("Too young")  # Implicit failure path
    return User(**data)
```

### ✅ Pattern: Explicit Result Types
Use a Discriminated Union to force the caller to handle the failure case.

```python
from typing import Literal

# 1. Define the Success and Failure Contexts
class UserCreated(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["created"] = "created"
    user: User

class UserRejected(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["rejected"] = "rejected"
    reason: str

# 2. Define the Union (The Result)
type CreateUserResult = UserCreated | UserRejected

# 3. The Pure Factory (Total Function)
def create_user(data: dict) -> CreateUserResult:
    # A. Apply Domain Rules (Logic First)
    if data.get('age', 0) < 18:
        return UserRejected(reason="User must be 18+")

    # B. Attempt Construction (Parsing Second)
    try:
        # We only build the object if the business rules passed.
        # If this succeeds, 'user' is the proof of a valid, adult user.
        user = User(id=data['id'], email=data['email'])
        return UserCreated(user=user)
        
    except ValueError as e:
        # Parsing errors (e.g. invalid email format)
        return UserRejected(reason=str(e))
```

## 3. Explicit Construction (No Defaults)
Domain Models must describe the *Shape* of data, not the *Rules* of data. Default values are hidden business rules.

### ❌ Anti-Pattern: Implicit Defaults
```python
class Order(BaseModel):
    # ❌ The rule "New orders are pending" is buried in the schema.
    # If we change the rule, we have to change the Type definition.
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.now)
```

### ✅ Pattern: Explicit Factory
The Schema is dumb. The Factory is smart.

```python
class Order(BaseModel):
    # Pure Shape. No defaults.
    status: OrderStatus
    created_at: datetime

def create_order(user: User) -> Order:
    # ✅ The rule lives in the Logic, where it belongs.
    return Order(
        status=OrderStatus.PENDING,
        created_at=clock.now()
    )
```

## 4. Cognitive Checks
*   [ ] **No Defaults:** Did I remove all `= "default"` assignments in my Domain Models?
*   [ ] **No Side Effects:** Does this factory just return data? (It should not save to DB).
*   [ ] **Total Function:** Does it handle *all* inputs (including malformed ones) without crashing?
*   [ ] **Immutable Output:** Is `model_config = {"frozen": True}` set on the output models?
