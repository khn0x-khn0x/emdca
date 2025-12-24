# Pattern 02: State (Sum Types Over Product Types)

## The Principle
Software complexity grows with the number of possible states. We must minimize the state space by making invalid combinations of state unrepresentable.

## The Mechanism
Mutually exclusive realities are modeled as **Discriminated Unions (Sum Types)**. Each context type contains specific data required for that reality. Transitions are methods on the source state that return the target state.

---

## 1. The God Model (Anti-Pattern)
Product Types (classes with many fields) allow invalid combinations of data to represent impossible states.

### ❌ Anti-Pattern: The Nullable Field Explosion
```python
class Order(BaseModel):
    id: UUID
    status: Literal["pending", "shipped", "cancelled"]
    
    tracking_id: Optional[str] = None  # ❌ Allows impossible states
    cancellation_reason: Optional[str] = None
    shipped_at: Optional[datetime] = None

    def ship(self, tracking_id: str):
        if self.status != "pending":
            raise ValueError("Can only ship pending orders")  # ❌ Runtime check
        self.status = "shipped"  # ❌ Mutation
```

---

## 2. The Discriminated Union (Sum Type)
We split the "God Model" into distinct, mutually exclusive types. Each type contains *only* the data valid for that state.

### ✅ Pattern: Explicit State Variants
```python
from typing import Literal, Annotated
from pydantic import BaseModel, Field

class PendingOrder(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["pending"]  # NO DEFAULT
    id: UUID
    items: tuple[OrderItem, ...]

class ShippedOrder(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["shipped"]  # NO DEFAULT
    id: UUID
    items: tuple[OrderItem, ...]
    tracking_id: str  # Structural Proof: MUST exist
    shipped_at: datetime

class CancelledOrder(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["cancelled"]  # NO DEFAULT
    id: UUID
    reason: str

# Sum Type (Python 3.12+)
type Order = Annotated[
    PendingOrder | ShippedOrder | CancelledOrder, 
    Field(discriminator="kind")
]
```

---

## 3. Transitions as Methods on Source State
Transitions are methods on the source state that return the target state. Clock is injected as a frozen Pydantic model.

### ✅ Pattern: Transition Method
```python
class Clock(BaseModel):
    """Injectable time dependency."""
    model_config = {"frozen": True}
    
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class PendingOrder(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["pending"]
    id: UUID
    items: tuple[OrderItem, ...]
    
    def ship(self, tracking_id: str, clock: Clock) -> ShippedOrder:
        """Transition: Pending → Shipped. Type signature guarantees validity."""
        return ShippedOrder(
            kind="shipped",
            id=self.id,
            items=self.items,
            tracking_id=tracking_id,
            shipped_at=clock.now(),
        )
    
    def cancel(self, reason: str) -> CancelledOrder:
        """Transition: Pending → Cancelled."""
        return CancelledOrder(
            kind="cancelled",
            id=self.id,
            reason=reason,
        )
```

---

## 4. Handling State (Pattern Matching)
To work with a Sum Type, use structural pattern matching. Logic lives in a handler model.

### ✅ Pattern: Handler with Exhaustive Matching
```python
class OrderSummaryHandler(BaseModel):
    """Handler model for order summary logic."""
    model_config = {"frozen": True}
    
    def summarize(self, order: Order) -> str:
        match order:
            case PendingOrder():
                return "Order is being prepared."
            
            case ShippedOrder(tracking_id=tid):
                return f"Order shipped! Tracking: {tid}"
            
            case CancelledOrder(reason=r):
                return f"Order cancelled because: {r}"
```

---

## 5. Alternative: The Smart Enum (For Simple States)
When states do not carry unique data, a **Smart Enum** is the preferred lightweight alternative.

### ✅ Pattern: Behavioral Enums
```python
from enum import StrEnum

class PaymentStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"

    @property
    def is_terminal(self) -> bool:
        return self in {PaymentStatus.PAID, PaymentStatus.FAILED}

    @property
    def can_retry(self) -> bool:
        return self == PaymentStatus.FAILED
```

---

## Cognitive Checks
- [ ] **No Optional Flags:** Did I remove `is_shipped`, `is_cancelled` booleans?
- [ ] **No Default on kind:** Is every `kind: Literal[...]` explicit at construction?
- [ ] **Transitions are Methods:** Is `ship()` a method on `PendingOrder`, not a standalone function?
- [ ] **Clock is a Model:** Is time injected as `Clock(BaseModel)`, not `ClockProtocol`?
- [ ] **Structural Proof:** Does `ShippedOrder` contain data that cannot exist in `PendingOrder`?
