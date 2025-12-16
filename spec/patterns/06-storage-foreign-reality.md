# Pattern 06: Storage (Foreign Reality)

## The Principle
The Database is just another External System. It is a **Foreign Reality** that must be explicitly modeled and translated, just like a 3rd-party API. The Domain does not define "Repositories"; it defines **Foreign Models** representing the stored data shape.

## The Mechanism
1.  **Foreign Models (Schema):** The Domain defines `DbOrder` (Pydantic) representing the SQL table structure.
2.  **Self-Translation:** `DbOrder` knows how to convert itself into `Order` (Internal Truth).
3.  **Shell Execution:** The Service Layer executes the query, validates the result into `DbOrder`, and translates it to `Order` before passing it to the Logic.

---

## 1. The Repository Abstraction (Anti-Pattern)
Traditional "Repository Patterns" hide the translation logic inside a class, often coupling the Domain to an interface that mimics a collection. This hides the cost of serialization and creates "Magic" objects.

### ❌ Anti-Pattern: The Magic Repo
```python
# The Domain "thinks" it's getting an Order, but the conversion is hidden.
# We don't know if 'repo.get()' is efficient or what shape it returns from the DB.
order = repo.get(order_id)
```

---

## 2. The Foreign Model (The Database Schema)
We model the database row explicitly. This lives in the Domain because knowing the persistence shape is Domain Knowledge.

### ✅ Pattern: The DB Model
```python
# domain/order/store.py (Foreign Model)
from pydantic import BaseModel
from .entity import Order, OrderId, OrderStatus

class DbOrder(BaseModel):
    """
    Represents the 'orders' table in Postgres.
    This is NOT the Domain Entity. It is the Persistence Shape.
    """
    id: str
    status: str
    amount_cents: int
    
    def to_domain(self) -> Order:
        """Pure Translation Logic"""
        return Order(
            id=OrderId(self.id),
            status=OrderStatus(self.status),
            amount=Money.from_cents(self.amount_cents)
        )
```

---

## 3. The Shell Execution (No Adapter Class)
The Service Layer (Shell) is responsible for the I/O. It uses a raw database client (like SQLAlchemy Core or asyncpg) to fetch data, then immediately naturalizes it.

### ✅ Pattern: Fetch -> Validate -> Translate
```python
# service/order.py (The Shell)
from sqlalchemy import select
from domain.order.store import DbOrder

async def process_order(order_id: str, db: AsyncSession):
    # 1. Fetch (Impure I/O)
    # We execute a raw, efficient query.
    result = await db.execute(select(orders_table).where(id=order_id))
    row = result.first()
    
    if not row:
        return

    # 2. Validate Reality (Foreign Model)
    # Ensure the DB data matches our schema expectation.
    db_order = DbOrder.model_validate(row)

    # 3. Translate to Truth (Pure Domain)
    order = db_order.to_domain()

    # 4. Execute Logic (Pure)
    intent = order.mark_shipped()

    # 5. Persist Result (Impure I/O)
    await db.execute(
        orders_table.update()
        .where(id=order_id)
        .values(status=intent.new_status.value)
    )
```

---

## 4. Why No Repository Class?
By removing the Repository Class:
1.  **Visible I/O:** You can see exactly what query is running in the Service.
2.  **Explicit Translation:** The `.to_domain()` call proves that we are crossing a boundary.
3.  **No Mocking:** You test the Logic by passing `Order` objects directly. You test the Service with a real DB (integration test). You don't need to mock a "Repository Interface."

## 5. Cognitive Checks
*   [ ] **Schema in Domain:** Does `domain/context/store.py` exist with Pydantic models?
*   [ ] **No SQL in Domain:** The Domain defines the shape (`DbOrder`), but never imports `sqlalchemy`.
*   [ ] **Explicit Translation:** Does the Service line read `DbOrder.model_validate(row).to_domain()`?
*   [ ] **No Generic Repos:** Did I delete `class OrderRepository`?
