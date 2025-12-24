---
description: "Pattern 06: Storage — Database as Foreign Reality with explicit translation."
globs: ["**/store.py", "**/domain/**/*.py"]
alwaysApply: false
---

# Pattern 06: Storage Foreign Reality

## Valid Code Structure

```python
# Foreign Model: Represents the database row shape
class DbOrder(BaseModel):
    model_config = {"frozen": True}
    
    id: str
    status: str
    amount_cents: int
    
    def to_domain(self) -> Order:
        return Order(
            id=OrderId(self.id),
            status=OrderStatus(self.status),
            amount=Money.from_cents(self.amount_cents),
        )

# Query Result: Explicit Sum Type
class OrderFound(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["found"]  # NO DEFAULT
    order: Order

class OrderNotFound(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["not_found"]  # NO DEFAULT
    order_id: str

type FetchOrderResult = OrderFound | OrderNotFound

# Store: Frozen model that handles DB I/O
class OrderStore(BaseModel):
    model_config = {"frozen": True}
    
    async def fetch(self, order_id: str, db: AsyncSession) -> FetchOrderResult:
        result = await db.execute(select(orders_table).where(id=order_id))
        row = result.first()
        
        if not row:
            return OrderNotFound(kind="not_found", order_id=order_id)
        
        db_order = DbOrder.model_validate(row)
        return OrderFound(kind="found", order=db_order.to_domain())

# Orchestrator: Store injected as field
class OrderProcessor(BaseModel):
    model_config = {"frozen": True}
    
    store: OrderStore  # Injected dependency
    
    async def process(self, order_id: str, db: AsyncSession) -> ProcessResult:
        fetch_result = await self.store.fetch(order_id, db)
        # ... pattern match on result
```

## Constraints

| Required | Forbidden |
|----------|-----------|
| `DbModel` with `.to_domain()` method | Repository pattern with abstract interface |
| `Found \| NotFound` Sum Type | `return None` for not found |
| Store as frozen `BaseModel` | Standalone query functions |
| Store injected as field into orchestrator | Direct DB access in domain |
| `DbOrder.model_validate(row).to_domain()` | Raw dict passing |

