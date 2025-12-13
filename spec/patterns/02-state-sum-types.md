# Pattern 02: State (Sum Types Over Product Types)

## The Principle
Software complexity grows with the number of possible states. We must minimize the state space by making invalid combinations of state unrepresentable.

## The Mechanism
Mutually exclusive realities are modeled as **Discriminated Unions (Sum Types)**. Each context type contains specific data required for that reality. Structural pattern matching is used to handle the different realities.

---

## 1. The God Model (Anti-Pattern)
Product Types (classes with many fields) allow invalid combinations of data to represent impossible states.

### ❌ Anti-Pattern: The Nullable Field Explosion
```python
class Order(BaseModel):
    id: UUID
    status: Literal["pending", "shipped", "cancelled"]
    
    # ❌ Problem: These fields are nullable to handle different states.
    # This allows impossible states: status="pending" but tracking_id is set.
    tracking_id: Optional[str] = None
    cancellation_reason: Optional[str] = None
    shipped_at: Optional[datetime] = None

    def ship(self, tracking_id: str):
        if self.status != "pending":
            raise ValueError("Can only ship pending orders")
        self.status = "shipped"
        self.tracking_id = tracking_id  # Mutation
```

---

## 2. The Discriminated Union (Sum Type)
We split the "God Model" into distinct, mutually exclusive types. Each type contains *only* the data valid for that state.

### ✅ Pattern: Explicit State Variants
```python
from typing import Literal, Annotated
from pydantic import BaseModel, Field

# 1. Define Mutually Exclusive Realities
class PendingOrder(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["pending"] = "pending"
    id: UUID
    items: list[OrderItem]

class ShippedOrder(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["shipped"] = "shipped"
    id: UUID
    items: list[OrderItem]
    # ✅ Structural Proof: A ShippedOrder MUST have a tracking_id
    tracking_id: str
    shipped_at: datetime

class CancelledOrder(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["cancelled"] = "cancelled"
    id: UUID
    reason: str

# 2. Define the Sum Type (Python 3.12+)
# This 'type' alias creates a Discriminated Union. 
# Pydantic uses the 'kind' field to determine which model to validate.
type Order = Annotated[
    PendingOrder | ShippedOrder | CancelledOrder, 
    Field(discriminator="kind")
]
```

### 💡 Understanding the Syntax
*   `type Order = ...`: This is the Python 3.12 **Type Alias** syntax. It tells the type checker "Order is exactly one of these three things."
*   `A | B | C`: This is the **Union Operator**. It means the value must be an instance of A, OR B, OR C.
*   `discriminator="kind"`: This tells Pydantic "Look at the 'kind' field in the JSON to decide which class to instantiate."

---

## 3. Transitions as Pure Functions
State transitions are not methods that mutate `self`. They are pure functions that accept a specific State Type and return a new State Type.

### ✅ Pattern: The Transition Function
```python
def ship_order(
    order: PendingOrder,  # ✅ Input Restriction: Only Pending orders can be shipped
    tracking_id: str,
    clock: ClockProtocol
) -> ShippedOrder:
    
    # No need to check "if order.status == pending"
    # The Type System guarantees it.
    
    return ShippedOrder(
        id=order.id,
        items=order.items,
        tracking_id=tracking_id,
        shipped_at=clock.now()
    )
```

---

## 4. Handling State (Pattern Matching)
To work with a Sum Type, we use structural pattern matching to unwrap the specific reality.

### ✅ Pattern: Exhaustive Matching
```python
def get_order_summary(order: Order) -> str:
    match order:
        case PendingOrder():
            return "Order is being prepared."
            
        case ShippedOrder(tracking_id=tid):
            # We can safely access tracking_id here
            return f"Order shipped! Tracking: {tid}"
            
        case CancelledOrder(reason=r):
            return f"Order cancelled because: {r}"
```

---

## 5. Alternative: The Smart Enum (For Simple States)
When states do not carry unique data (i.e., the shape of the object doesn't change, only its classification), a **Smart Enum** is the preferred lightweight alternative to a full Sum Type.

### ✅ Pattern: Behavioral Enums
Enrich the Enum with properties to co-locate logic, rather than scattering `if` statements.

```python
from enum import Enum

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"

    @property
    def is_terminal(self) -> bool:
        """Returns True if the state allows no further transitions."""
        return self in {PaymentStatus.PAID, PaymentStatus.FAILED}

    @property
    def can_retry(self) -> bool:
        return self == PaymentStatus.FAILED

# Usage
def check_payment(status: PaymentStatus):
    # Logic is on the type, not scattered in helper functions
    if status.can_retry:
        retry_payment()
```

---

## 6. Cognitive Checks
*   [ ] **No Optional Flags:** Did I remove `is_shipped`, `is_cancelled` booleans?
*   [ ] **Specific Inputs:** Do my transition functions accept `Order` (generic) or `PendingOrder` (specific)? (Prefer specific).
*   [ ] **Structural Proof:** Does `ShippedOrder` contain data that simply *cannot exist* in `PendingOrder`?
