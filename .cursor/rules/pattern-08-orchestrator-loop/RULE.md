---
description: "Pattern 08: Coordination — Dumb Orchestrator that moves data, doesn't think."
globs: ["**/service/**/*.py", "**/orchestrator.py"]
alwaysApply: false
---

# Pattern 08: Orchestrator Loop

## Valid Code Structure

```python
# Result Types
class PaymentNotFound(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["not_found"]  # NO DEFAULT
    payment_id: str

class PaymentProcessed(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["processed"]  # NO DEFAULT
    payment_id: str

class VerificationRequired(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["verification_required"]  # NO DEFAULT
    reason: str

type ProcessPaymentResult = PaymentNotFound | PaymentProcessed | VerificationRequired

# Orchestrator: Frozen model with dependencies as fields
class PaymentOrchestrator(BaseModel):
    model_config = {"frozen": True}
    
    store: PaymentStore       # Injected dependency
    gateway: PaymentGateway   # Injected dependency
    
    def process(self, payment_id: str, db: Session) -> ProcessPaymentResult:
        # 1. Fetch (via injected store)
        fetch_result = self.store.fetch(payment_id, db)
        
        match fetch_result:
            case PaymentNotFound():
                return fetch_result
            
            case PaymentFound(payment=payment):
                # 2. Decide (Pure Domain—method on aggregate)
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

## Constraints

| Required | Forbidden |
|----------|-----------|
| Orchestrator is frozen `BaseModel` | Standalone `def process_payment()` functions |
| Dependencies as fields (stores, gateways) | Stateless orchestrator with no fields |
| Dumb piping: Fetch → Translate → Decide → Act | `if payment.amount > 10000` (business logic) |
| `match/case` for flow control | `raise` for control flow |
| Decision logic in domain aggregates | Decision logic in orchestrator |
| Return Sum Types | `return None` or implicit returns |

