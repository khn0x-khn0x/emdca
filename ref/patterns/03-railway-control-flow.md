# Pattern 03: Control Flow (Railway Oriented Programming)

## The Principle
Logic is a flow of data. Branching should be handled as a topology of tracks, not as a series of exceptions or jumps.

## The Mechanism
Logic branches happen inside methods on models, explicitly guiding data onto a "Success Track" or a "Failure Track". Every logical branch must terminate in a return value; exceptions are strictly forbidden for domain logic.

---

## 1. Exceptions are for System Failures, Not Logic
Exceptions are "GOTO" statements that jump up the stack, bypassing type checks and breaking linearity.

### ❌ Anti-Pattern: Business Logic as Exceptions
```python
def withdraw(account: Account, amount: int) -> Account:
    if amount > account.balance:
        raise InsufficientFundsException()  # ❌ Hidden control flow
    return account.debit(amount)
```

### ✅ Pattern: Explicit Result Types
The return signature MUST tell the whole truth.

```python
from typing import Literal
from pydantic import BaseModel

class WithdrawalSuccess(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["success"]  # NO DEFAULT
    new_account_state: Account
    amount_withdrawn: int

class InsufficientFunds(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["insufficient_funds"]  # NO DEFAULT
    current_balance: int
    requested_amount: int

type WithdrawalResult = WithdrawalSuccess | InsufficientFunds
```

---

## 2. The Railway Switch (Branching)
Logic branches are decision points. Withdraw is a method on Account that routes to success or failure.

### ✅ Pattern: Decision Method on Aggregate
```python
class Account(BaseModel):
    model_config = {"frozen": True}
    id: str
    balance: int
    
    def withdraw(self, amount: int) -> WithdrawalResult:
        if amount > self.balance:
            return InsufficientFunds(
                kind="insufficient_funds",
                current_balance=self.balance,
                requested_amount=amount,
            )
        
        new_state = Account(id=self.id, balance=self.balance - amount)
        return WithdrawalSuccess(
            kind="success",
            new_account_state=new_state,
            amount_withdrawn=amount,
        )
```

---

## 3. Explicit Fall-through (No Implicit None)
"Do nothing" must be an explicit value, not `None`.

### ❌ Anti-Pattern: Returning None
```python
def process_refund(order: Order):
    if not order.is_refundable:
        return None  # ❌ Ambiguous
```

### ✅ Pattern: The NoOp Result
```python
class RefundProcessed(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["processed"]  # NO DEFAULT
    refund_id: str

class RefundSkipped(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["skipped"]  # NO DEFAULT
    reason: str

type RefundResult = RefundProcessed | RefundSkipped


class RefundableOrder(BaseModel):
    """Order that can be refunded."""
    model_config = {"frozen": True}
    id: str
    is_refundable: bool
    
    def process_refund(self) -> RefundResult:
        if not self.is_refundable:
            return RefundSkipped(kind="skipped", reason="Order outside refund window")
        
        return RefundProcessed(kind="processed", refund_id=f"refund-{self.id}")
```

---

## 4. Handling the Tracks (Pattern Matching)
The caller MUST handle both tracks. Handler is a model with coordination method.

### ✅ Pattern: Handler Model
```python
class WithdrawalHandler(BaseModel):
    """Handler for withdrawal requests."""
    model_config = {"frozen": True}
    
    def handle(self, account: Account, amount: int) -> WithdrawalResult:
        result = account.withdraw(amount)
        
        match result:
            case WithdrawalSuccess(new_account_state=state):
                # Caller handles persistence
                return result
            
            case InsufficientFunds():
                # Caller handles error display
                return result
```

---

## Cognitive Checks
- [ ] **Truthful Signature:** Does the return type include the failure cases?
- [ ] **No Raises:** Did I grep for `raise`? (Only allowed for system panics)
- [ ] **No None:** Did I grep for `return None`? Use `Skipped` or `NoOp` instead
- [ ] **No Defaults on kind:** Is every `kind: Literal[...]` explicit?
- [ ] **Methods on Models:** Is decision logic a method on an aggregate, not a standalone function?
