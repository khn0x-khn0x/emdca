# Pattern 06: Abstraction (The Repository Pattern)

## The Principle
The Domain Core must be agnostic to the mechanism of data storage. Whether data lives in a database, a file, or memory is an implementation detail that must not leak into business logic.

## The Mechanism
The Domain defines **Storage Interfaces** describing *what* data it needs. The Shell provides concrete **Repository Implementations** that handle I/O. The Domain never performs direct I/O.

---

## 1. The Leaky Abstraction (Anti-Pattern)
Importing database libraries into the domain couples your business logic to a specific vendor (SQLAlchemy, Mongo, Redis).

### ❌ Anti-Pattern: Vendor Lock-in
```python
# domain/order.py
from sqlalchemy.orm import Session
from .models import OrderModel  # ❌ Coupling to ORM Model

def get_order_total(session: Session, order_id: int) -> float:
    # ❌ Direct Dependency on SQL
    order = session.query(OrderModel).filter_by(id=order_id).first()
    return order.total
```

---

## 2. The Storage Protocol (Interface)
The Domain defines a contract using `typing.Protocol`. It says "I need a way to get an Order," but doesn't care how.

### ✅ Pattern: The Domain Protocol
```python
from typing import Protocol, Optional
from .types import Order, OrderId  # Pure Domain Objects

class OrderRepository(Protocol):
    """
    The Domain's view of storage.
    Pure definition. No implementation.
    """
    def get(self, id: OrderId) -> Optional[Order]:
        ...
    
    def save(self, order: Order) -> None:
        ...
```

---

## 3. The Concrete Implementation (The Shell)
The Shell implements the Protocol using specific technology. It is responsible for mapping between the "Dirty" DB world and the "Pure" Domain world.

### ✅ Pattern: The Adapter
```python
# service/repository.py
from sqlalchemy.orm import Session
from domain.orders import Order, OrderRepository

class SqlAlchemyOrderRepo(OrderRepository):
    def __init__(self, session: Session):
        self.session = session

    def get(self, id: OrderId) -> Optional[Order]:
        # 1. Fetch "Dirty" ORM Object
        orm_order = self.session.query(DbOrder).get(id)
        
        if not orm_order:
            return None
            
        # 2. Map to "Pure" Domain Object (Pattern 07)
        return Order(
            id=orm_order.id,
            items=orm_order.items,
            status=orm_order.status
        )

    def save(self, order: Order) -> None:
        # 1. Map Domain -> ORM
        orm_order = DbOrder(
            id=order.id,
            status=order.status
        )
        # 2. Persist
        self.session.merge(orm_order)
```

---

## 4. Usage in Application Service (The Orchestrator)
The Orchestrator (Shell) injects the concrete implementation. It fetches data **before** passing it to the Pure Domain Logic.

```python
# service/order_service.py (The Shell)

def process_order_flow(repo: OrderRepository, order_id: OrderId):
    # 1. Fetch (Side Effect)
    # The Shell uses the Repo to get the data.
    order = repo.get(order_id)
    
    if not order:
        return

    # 2. Logic (Pure)
    # The Domain Logic receives the DATA, not the REPO.
    intent = decide_next_step(order)

    # 3. Persist (Side Effect)
    repo.save(order)
```

## 5. Cognitive Checks
*   [ ] **No SQL:** Did I grep for `SELECT`, `INSERT`, or `sqlalchemy` in the `domain/` folder?
*   [ ] **Pure Returns:** Does the Repository return `Order` (Domain), not `DbOrder` (ORM)?
*   [ ] **Protocol Only:** Does the domain import `OrderRepository` (Protocol), never `SqlAlchemyOrderRepo`?
*   [ ] **Inverted Usage:** Does the Domain *define* the Protocol but the Shell *call* it? (The Domain should rarely, if ever, call the repository methods itself).
