# Pattern 08: Coordination (The Orchestrator)

## The Principle
A system needs a "driver" that does no thinking, only moving. It coordinates the flow of data between models and execution shell. We call this the **Runtime** or **Orchestrator**.
In EMDCA, the **Runtime** is a **Smart Domain Model** that encapsulates the coordination logic and holds the necessary Capabilities.

## The Mechanism
The **Runtime** is a Domain Model (`BaseModel`). It runs a "dumb" reactive loop: Load → Step → Save → Execute. It contains no business rules, only flow control.

---

## 1. The Fat Service (Anti-Pattern)
Putting business logic ("Thinking") inside the orchestration layer ("Moving") makes the system rigid and hard to test.

### ❌ Anti-Pattern: Logic in the Loop
```python
def process_payment(payment_id: str, db: Session):  # ❌ Standalone function
    payment = fetch_payment(db, payment_id)
    
    if payment.amount > 10000 and not payment.is_verified:  # ❌ Business logic leak
        raise ValueError("Large payments need verification")  # ❌ Exception for logic
```

---

## 2. The Runtime (Smart Model)

The Runtime drives the State Machine. It does not decide; it merely executes the Domain's decisions.

### ✅ Pattern: The Reactive Loop
```python
from enum import StrEnum

class PaymentResultKind(StrEnum):
    NOT_FOUND = "not_found"
    PROCESSED = "processed"

class PaymentRuntime(BaseModel):
    """Active Domain Model. Drives the loop."""
    model_config = {"frozen": True, "arbitrary_types_allowed": True}
    
    store: PaymentStore      # Smart Capability
    gateway: PaymentGateway  # Smart Capability
    
    async def run(self, payment_id: PaymentId, event: PaymentEvent) -> ProcessPaymentResult:
        # 1. Load State (Active Store)
        state = await self.store.load(payment_id)
        
        # Handle "Not Found" as a valid result track
        if not state:
            return PaymentNotFound(kind=PaymentResultKind.NOT_FOUND, payment_id=payment_id)
        
        # 2. Pure Step (Domain Logic)
        new_state, intent = state.handle(event)
        
        # 3. Save State (Active Store)
        await self.store.save(payment_id, new_state)
        
        # 4. Execute Intent (Active Gateway)
        await self.gateway.execute(intent)
        
        return PaymentProcessed(kind=PaymentResultKind.PROCESSED, payment_id=payment_id)
```

---

## 3. Transaction Boundaries
The Runtime is responsible for the **Unit of Work**. Wrap in transaction context.

### ✅ Pattern: Explicit Transactions
```python
class TransactionalRuntime(BaseModel):
    """Runtime with transaction boundary."""
    model_config = {"frozen": True}
    
    runtime: PaymentRuntime
    
    async def run_safely(self, payment_id: PaymentId, db: Session) -> ProcessPaymentResult:
        async with db.begin():
            return await self.runtime.run(payment_id, event)
```

---

## Cognitive Checks
- [ ] **Runtime is Model:** Is it a `BaseModel`?
- [ ] **Capabilities Injected:** Does it hold `store` and `gateway` as fields?
- [ ] **No If Statements:** Does the runtime contain `if payment.amount > X`? (Move to Domain)
- [ ] **Step Delegation:** Does it call `state.handle()` or `state.step()`?
- [ ] **Active Execution:** Does it call `gateway.execute(intent)`?
