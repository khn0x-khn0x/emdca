# Pattern 06: Storage (Foreign Reality)

## The Principle
The Database is just another External System. It is a **Foreign Reality** that must be explicitly modeled and translated.
In EMDCA, the **Store** is not a "Repository Service"; it is a **Smart Domain Model** (Capability) that encapsulates the database connection and the logic to use it.

## The Mechanism
1.  **Foreign Models (Schema):** `DbOrder` defines the SQL shape.
2.  **Capability (The Store):** `OrderStore` is a Domain Model that holds the DB Client.
3.  **Active Execution:** `OrderStore.load()` uses the client to fetch data and translate it.

---

## 1. The Repository Abstraction (Anti-Pattern)
Traditional "Repository Patterns" hide translation logic behind interfaces, separating the "Definition" of storage from the "Act" of storage.

### ❌ Anti-Pattern: Service-Based Repository
```python
# Service Class
class OrderRepository:
    def get(self, id): ... 
```

---

## 2. The Foreign Model (The Database Schema)
We model the database row explicitly.

### ✅ Pattern: The DB Model
```python
from pydantic import BaseModel

class DbOrder(BaseModel):
    """Foreign Model: Represents the 'orders' table."""
    model_config = {"frozen": True}
    
    id: OrderId
    status: OrderStatus
    amount_cents: int
    
    def to_domain(self) -> Order:
        return Order(
            id=self.id,
            status=self.status,
            amount=Money.from_cents(self.amount_cents),
        )
```

---

## 3. Query Result (Sum Type)
Model the query result explicitly—found or not found.

### ✅ Pattern: Explicit Result
```python
from enum import StrEnum

class StorageResultKind(StrEnum):
    FOUND = "found"
    NOT_FOUND = "not_found"

class OrderFound(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[StorageResultKind.FOUND]
    order: Order

class OrderNotFound(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[StorageResultKind.NOT_FOUND]
    order_id: OrderId

type FetchOrderResult = OrderFound | OrderNotFound
```

---

## 4. The Store Capability (Active Model)

The "Store" is an Active Domain Model. It holds the DB Client.

### ✅ Pattern: Active Store
```python
class OrderStore(BaseModel):
    """Active Domain Model. Holds Data (Config) and Capability (Client)."""
    model_config = {"frozen": True, "arbitrary_types_allowed": True}
    
    # Injected Capability
    db: Any
    table_name: TableName
    
    async def load(self, order_id: OrderId) -> FetchOrderResult:
        # 1. Raw I/O (Using Injected Capability)
        row = await self.db.fetch_one(
            select(self.table_name).where(id=order_id)
        )
        
        # 2. Pure Translation
        if not row:
            return OrderNotFound(kind=StorageResultKind.NOT_FOUND, order_id=order_id)
            
        return OrderFound(
            kind=StorageResultKind.FOUND, 
            order=DbOrder.model_validate(row).to_domain()
        )
```

---

## 5. The Usage (Orchestration)

The Orchestrator (Runtime) holds the Store Model.

### ✅ Pattern: Active Orchestration
```python
class OrderRuntime(BaseModel):
    """Active Runtime Model."""
    model_config = {"frozen": True}
    
    store: OrderStore
    
    async def process(self, order_id: OrderId) -> ProcessResult:
        # The Store is Active. We just ask it to load.
        fetch_result = await self.store.load(order_id)
        
        match fetch_result:
            case OrderFound(order=order):
                return ProcessSuccess(order=order)
            case OrderNotFound():
                return ProcessFailure("Not Found")
```

---

## 6. Why No Repository Interface?
By making the Store a Model:
1.  **Co-location:** The definition of "How to load an order" lives with the Order concept.
2.  **Explicit Context:** The DB Client is passed in `__init__`.
3.  **Unified Semantics:** Everything is a Model.

---

## Cognitive Checks
- [ ] **Store is Model:** Is `OrderStore` a Pydantic Model?
- [ ] **Capability Injected:** Does it hold `db` as a field?
- [ ] **No Service Classes:** Did I remove `OrderRepository` class?
- [ ] **Explicit Translation:** Does it read `DbOrder.model_validate(row).to_domain()`?
- [ ] **Smart Enums:** Am I using `StorageResultKind`?
