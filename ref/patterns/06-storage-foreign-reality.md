# Pattern 06: Storage (Foreign Reality)

## The Principle
The Database is just another External System. It is a **Foreign Reality** that must be explicitly modeled and translated, just like a 3rd-party API. The Domain does not define "Repositories"; it defines **Foreign Models** representing the stored data shape.

## The Mechanism
1.  **Foreign Models (Schema):** The Domain defines `DbOrder` (Pydantic) representing the SQL table structure.
2.  **Self-Translation:** `DbOrder` knows how to convert itself into `Order` (Internal Truth).
3.  **Orchestrator Execution:** The Orchestrator executes the query, validates into `DbOrder`, and translates to `Order`.

---

## 1. The Repository Abstraction (Anti-Pattern)
Traditional "Repository Patterns" hide translation logic, coupling the Domain to an interface that mimics a collection.

### ❌ Anti-Pattern: The Magic Repo
```python
order = repo.get(order_id)  # ❌ Hidden translation, hidden query
```

---

## 2. The Foreign Model (The Database Schema)
We model the database row explicitly. This lives in the Domain because knowing the persistence shape is Domain Knowledge.

### ✅ Pattern: The DB Model
```python
from pydantic import BaseModel

class DbOrder(BaseModel):
    """Foreign Model: Represents the 'orders' table."""
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
```

---

## 3. Query Result (Sum Type)
Model the query result explicitly—found or not found.

### ✅ Pattern: Explicit Result
```python
from typing import Literal

class OrderFound(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["found"]
    order: Order

class OrderNotFound(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["not_found"]
    order_id: str

type FetchOrderResult = OrderFound | OrderNotFound
```

---

## 4. The Store Executor
The Store is a frozen Pydantic model that handles DB I/O. It's injected into orchestrators.

### ✅ Pattern: Store as Executor
```python
class OrderStore(BaseModel):
    """Executor for order persistence. Injected into orchestrators."""
    model_config = {"frozen": True}
    
    async def fetch(self, order_id: str, db: AsyncSession) -> FetchOrderResult:
        result = await db.execute(select(orders_table).where(id=order_id))
        row = result.first()
        
        if not row:
            return OrderNotFound(kind="not_found", order_id=order_id)
        
        db_order = DbOrder.model_validate(row)
        order = db_order.to_domain()
        return OrderFound(kind="found", order=order)
    
    async def save_status(self, order_id: str, status: OrderStatus, db: AsyncSession) -> None:
        await db.execute(
            orders_table.update()
            .where(id=order_id)
            .values(status=status.value)
        )
```

---

## 5. The Orchestrator (Pydantic Model)
The Orchestrator declares its dependencies as fields. Application-scoped dependencies are injected; request-scoped resources (like `db`) are passed as arguments.

### ✅ Pattern: Dependencies as Fields
```python
class OrderProcessor(BaseModel):
    """Orchestrator with injected store."""
    model_config = {"frozen": True}
    
    store: OrderStore  # Injected dependency
    
    async def process(self, order_id: str, db: AsyncSession) -> ProcessResult:
        fetch_result = await self.store.fetch(order_id, db)
        
        match fetch_result:
            case OrderNotFound():
                return fetch_result
            
            case OrderFound(order=order):
                intent = order.mark_shipped()
                await self.store.save_status(order_id, intent.new_status, db)
                return OrderProcessed(kind="processed", order_id=order_id)
```

---

## 6. Why No Repository Class?
By removing the Repository Class:
1.  **Visible I/O:** You see exactly what query runs.
2.  **Explicit Translation:** The `.to_domain()` proves boundary crossing.
3.  **No Mocking:** Test Logic with `Order` objects directly.

---

## Cognitive Checks
- [ ] **Schema in Domain:** Does `domain/context/store.py` exist with Pydantic models?
- [ ] **No SQL in Domain:** The Domain defines the shape, never imports `sqlalchemy`.
- [ ] **Explicit Translation:** Does it read `DbOrder.model_validate(row).to_domain()`?
- [ ] **No Implicit None:** Is "not found" an explicit `OrderNotFound` type?
- [ ] **Store as Executor:** Is the store a `BaseModel` with I/O methods?
- [ ] **Dependencies as Fields:** Does the orchestrator have `store: OrderStore` as a field?
