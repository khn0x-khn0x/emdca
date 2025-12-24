---
description: "Pattern 02: State — Sum Types over Product Types. Make invalid states unrepresentable."
globs: ["**/domain/**/*.py", "**/entity.py", "**/process.py"]
alwaysApply: false
---

# Pattern 02: State Sum Types

## Valid Code Structure

```python
# Each state is its own type with only valid data for that state
class PendingOrder(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["pending"]  # NO DEFAULT
    id: UUID
    items: tuple[OrderItem, ...]
    
    def ship(self, tracking_id: str, clock: Clock) -> "ShippedOrder":
        """Transition: Pending → Shipped. Type signature guarantees validity."""
        return ShippedOrder(
            kind="shipped",
            id=self.id,
            items=self.items,
            tracking_id=tracking_id,
            shipped_at=clock.now(),
        )
    
    def cancel(self, reason: str) -> "CancelledOrder":
        """Transition: Pending → Cancelled."""
        return CancelledOrder(kind="cancelled", id=self.id, reason=reason)

class ShippedOrder(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["shipped"]  # NO DEFAULT
    id: UUID
    items: tuple[OrderItem, ...]
    tracking_id: str  # Structural proof: MUST exist in shipped state
    shipped_at: datetime

class CancelledOrder(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["cancelled"]  # NO DEFAULT
    id: UUID
    reason: str

# Sum Type
type Order = Annotated[
    PendingOrder | ShippedOrder | CancelledOrder,
    Field(discriminator="kind")
]
```

## Constraints

| Required | Forbidden |
|----------|-----------|
| Separate type per state | One class with `status: str` field |
| `kind: Literal["..."]` discriminator | `kind: Literal["..."] = "..."` default |
| Transition methods on source state | Standalone `def ship_order()` functions |
| Structural proof (data exists only in valid states) | `Optional[tracking_id]` on all states |
| `match/case` for handling | `if order.status == "shipped"` |
| Smart Enums for simple states | Boolean flags `is_shipped`, `is_cancelled` |

