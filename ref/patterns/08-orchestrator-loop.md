# Pattern 08: Coordination (The Orchestrator)

## The Principle
A system needs a "driver" that does no thinking, only moving. It coordinates the flow of data between models and execution shell.

## The Mechanism
The **Orchestrator** is a frozen Pydantic model with a coordination method. It runs a "dumb" procedural loop: Fetch → Translate → Decide → Act → Persist. It contains no business rules, only flow control.

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

## 2. The Orchestrator Model
The Orchestrator is a frozen Pydantic model with **dependencies as fields**. Application-scoped dependencies (stores, gateways) are injected; request-scoped resources (sessions) are passed as arguments.

### ✅ Pattern: Dependencies as Fields
```python
from typing import Literal
from pydantic import BaseModel

class PaymentNotFound(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["not_found"]
    payment_id: str

class PaymentProcessed(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["processed"]
    payment_id: str

class VerificationRequired(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["verification_required"]
    reason: str

type ProcessPaymentResult = PaymentNotFound | PaymentProcessed | VerificationRequired


class PaymentOrchestrator(BaseModel):
    """Dumb orchestrator—coordinates but does not decide."""
    model_config = {"frozen": True}
    
    store: PaymentStore      # Injected: handles DB I/O
    gateway: PaymentGateway  # Injected: handles external payment API
    
    def process(self, payment_id: str, db: Session) -> ProcessPaymentResult:
        # 1. Fetch (via injected store)
        fetch_result = self.store.fetch(payment_id, db)
        
        match fetch_result:
            case PaymentNotFound():
                return fetch_result
            
            case PaymentFound(payment=payment):
                # 2. Decide (Pure Domain—method on Payment)
                intent = payment.decide_action()
                
                # 3. Act (via injected dependencies)
                match intent:
                    case ProcessIntent(new_state=s):
                        self.gateway.charge(s.amount)
                        self.store.save(s, db)
                        return PaymentProcessed(kind="processed", payment_id=payment_id)
                    
                    case RequireVerificationIntent(reason=r):
                        return VerificationRequired(kind="verification_required", reason=r)
```

---

## 3. Transaction Boundaries
The Orchestrator is responsible for the **Unit of Work**. Wrap in transaction context.

### ✅ Pattern: Explicit Transactions
```python
class TransactionalOrchestrator(BaseModel):
    """Orchestrator with transaction boundary."""
    model_config = {"frozen": True}
    
    orchestrator: PaymentOrchestrator
    
    def process_safely(self, payment_id: str, db: Session) -> ProcessPaymentResult:
        with db.begin():
            return self.orchestrator.process(payment_id, db)
```

---

## Cognitive Checks
- [ ] **Dependencies as Fields:** Are stores, gateways, executors declared as fields?
- [ ] **No If Statements:** Does the orchestrator contain `if payment.amount > X`? (Move to Domain)
- [ ] **No Object Creation:** Does the orchestrator call `Payment(...)`? (Use a Factory)
- [ ] **Orchestrator is Model:** Is it a `BaseModel` with methods, not a standalone function?
- [ ] **Explicit Results:** Does it return Sum Types, not `None` or raise?
- [ ] **Dumb Piping:** Does it just pass data between models without modification?
