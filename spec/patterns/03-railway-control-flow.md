# Pattern 03: Control Flow (Railway Oriented Programming)

## The Principle
Logic is a flow of data. Branching should be handled as a topology of tracks, not as a series of exceptions or jumps.

## The Mechanism
Logic branches happen inside the Factory, explicitly guiding data onto a "Success Track" (Success Context) or a "Failure Track" (Wait/Halt Context). Every logical branch must terminate in a return value; exceptions are strictly forbidden for domain logic.

---

## 1. Exceptions are for System Failures, Not Logic
Exceptions are "GOTO" statements that jump up the stack, bypassing type checks and breaking linearity.

### ❌ Anti-Pattern: Business Logic as Exceptions
```python
def withdraw(account: Account, amount: int) -> Account:
    if amount > account.balance:
        # ❌ Hidden Control Flow
        # The signature implies this function always returns an Account.
        # It lies. It might crash.
        raise InsufficientFundsException()
        
    return account.debit(amount)
```

### ✅ Pattern: Explicit Result Types
The return signature MUST tell the whole truth.

```python
from typing import Literal
from pydantic import BaseModel

class WithdrawalSuccess(BaseModel):
    kind: Literal["success"] = "success"
    new_account_state: Account
    amount_withdrawn: int

class InsufficientFunds(BaseModel):
    kind: Literal["insufficient_funds"] = "insufficient_funds"
    current_balance: int
    requested_amount: int

# The Truthful Signature
type WithdrawalResult = WithdrawalSuccess | InsufficientFunds
```

---

## 2. The Railway Switch (Branching)
Logic branches are decision points where data is routed onto different tracks.

```python
def withdraw(account: Account, amount: int) -> WithdrawalResult:
    # 1. The Switch
    if amount > account.balance:
        # Route to Failure Track
        return InsufficientFunds(
            current_balance=account.balance, 
            requested_amount=amount
        )
    
    # Route to Success Track
    new_state = account.debit(amount)
    return WithdrawalSuccess(
        new_account_state=new_state,
        amount_withdrawn=amount
    )
```

---

## 3. Explicit Fall-through (No Implicit None)
Sometimes a function decides "do nothing." This must be an explicit value, not `None`.

### ❌ Anti-Pattern: Returning None
```python
def process_refund(order: Order):
    if not order.is_refundable:
        return None  # ❌ Ambiguous. Did it fail? Did it finish?
    ...
```

### ✅ Pattern: The NoOp Result
```python
class RefundProcessed(BaseModel):
    kind: Literal["processed"] = "processed"
    refund_id: str

class RefundSkipped(BaseModel):
    kind: Literal["skipped"] = "skipped"
    reason: str

type RefundResult = RefundProcessed | RefundSkipped

def process_refund(order: Order) -> RefundResult:
    if not order.is_refundable:
        return RefundSkipped(reason="Order outside refund window")
    
    # ... logic ...
    return RefundProcessed(refund_id="123")
```

---

## 4. Handling the Tracks (Pattern Matching)
The caller MUST handle both tracks. The Type Checker enforces this exhaustiveness.

```python
def handle_withdrawal_request(account: Account, amount: int):
    result = withdraw(account, amount)
    
    match result:
        case WithdrawalSuccess(new_account_state=state):
            save_account(state)
            dispense_cash(amount)
            
        case InsufficientFunds(current_balance=bal):
            # We are forced to handle this case
            print(f"Error: You only have {bal}")
```

## 5. Cognitive Checks
*   [ ] **Truthful Signature:** Does the return type annotation include the failure cases?
*   [ ] **No Raises:** Did I grep for `raise`? (Only allowed for system panics like `OutOfMemory`).
*   [ ] **No None:** Did I grep for `return None`? Use a `Skipped` or `NoOp` object instead.
