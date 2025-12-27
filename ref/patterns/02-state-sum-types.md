# Pattern 02: State (Sum Types)

## The Principle
Software complexity grows with the number of possible states. We must minimize the state space by making invalid combinations of state unrepresentable. We use **Sum Types** (Discriminated Unions) to model mutually exclusive states, rather than **Product Types** (Flags/Nullables) that allow impossible combinations.

## The Mechanism
1.  **Smart Enums:** Define the vocabulary and properties of the state graph.
2.  **Distinct Models:** Each state is a separate Pydantic model.
3.  **Union Type:** The state is the Union of these models.
4.  **Transitions:** Methods on the *Source State* return the *Target State*.

---

## 1. The Flag Hell (Anti-Pattern)
Using boolean flags or optional fields creates states that shouldn't exist (e.g., `is_shipped=True` but `tracking_id=None`).

### ❌ Anti-Pattern: Product Types
```python
class Order(BaseModel):
    status: str
    is_shipped: bool
    tracking_id: str | None  # ❌ Ambiguous: Can be None if shipped?
    
    def ship(self):
        if self.status != "pending":
            raise Exception("Invalid state")  # ❌ Implicit state check
```

---

## 2. The Sum Type (Discriminated Union)
Each state carries only the data valid for that state.

### ✅ Pattern: Explicit States
```python
from enum import StrEnum

class OrderStatus(StrEnum):
    PENDING = "pending"
    SHIPPED = "shipped"

class PendingOrder(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[OrderStatus.PENDING]
    id: OrderId
    items: tuple[OrderItem, ...]
    
    def ship(self, tracking_id: TrackingId, shipped_at: datetime) -> "ShippedOrder":
        """Transition: Pending → Shipped."""
        return ShippedOrder(
            kind=OrderStatus.SHIPPED,
            id=self.id,
            items=self.items,
            tracking_id=tracking_id,
            shipped_at=shipped_at,
        )

class ShippedOrder(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[OrderStatus.SHIPPED]
    id: OrderId
    items: tuple[OrderItem, ...]
    tracking_id: TrackingId  # Must exist!
    shipped_at: datetime

type Order = Annotated[
    PendingOrder | ShippedOrder,
    Field(discriminator="kind")
]
```

---

## 3. Handling State (Pattern Matching)
Use `match/case` to handle each state explicitly.

### ✅ Pattern: Exhaustive Matching
```python
def print_status(order: Order):
    match order:
        case PendingOrder():
            print("Order is pending")
        case ShippedOrder(tracking_id=tid):
            print(f"Shipped: {tid}")
```

---

## Cognitive Checks
- [ ] **No Optional Flags:** Did I remove `is_active`, `is_deleted`?
- [ ] **No Nullable State Fields:** Did I remove `error: str | None`?
- [ ] **Distinct Classes:** Is `Pending` a different class from `Active`?
- [ ] **Smart Enum:** Does `kind` use a `StrEnum`?
- [ ] **Transitions:** Are methods defined on the specific state class?
- [ ] **Pure Transitions:** Do transitions take Data (datetime), not Services (Clock)?
- [ ] **Value Objects:** Do I use `OrderId` instead of `str`?
