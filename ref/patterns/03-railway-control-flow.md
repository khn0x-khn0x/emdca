# Pattern 03: Control Flow (Railway Oriented)

## The Principle
We distinguish between **Structural Failures** (Invalid Data) and **Business Failures** (Valid Data, Invalid State).
*   **Structural Failures** (e.g. negative money) must **Crash** (via Type Validation).
*   **Business Failures** (e.g. insufficient funds) must **Return a Result** (via Railway Oriented Programming).

## The Mechanism
1.  **Smart Enums:** Define the possible outcomes explicitly.
2.  **Result Types:** Domain functions return a Sum Type `Success | Failure`.
3.  **No Logic Exceptions:** Domain logic never raises exceptions for business rules.
4.  **No Defensive Coding:** Entities delegate rules to Value Objects.

---

## 1. The Exception Tunnel (Anti-Pattern)
Exceptions are invisible GOTO statements. They break control flow and force the caller to read implementation details to know what to catch.

### ❌ Anti-Pattern: Throwing for Logic
```python
def withdraw(account: Account, amount: int):
    if amount > account.balance:
        raise ValueError("Insufficient funds")  # ❌ Hidden control flow
    account.balance -= amount
```

---

## 2. The Explicit Result
The return signature tells the whole truth. Note that the **Entity** (Account) does not manually check the balance. It asks the **Value Object** (Money) to perform the subtraction.

### ✅ Pattern: Explicit Outcomes with Smart Enums
```python
from enum import StrEnum

class WithdrawalResultKind(StrEnum):
    SUCCESS = "success"
    INSUFFICIENT_FUNDS = "insufficient_funds"

class Money(BaseModel):
    model_config = {"frozen": True}
    cents: PositiveInt

    def subtract(self, other: "Money") -> "Money | InsufficientFunds":
        # Rule lives here
        if other.cents > self.cents:
            return InsufficientFunds(
                kind=WithdrawalResultKind.INSUFFICIENT_FUNDS, 
                current_balance=self, 
                requested=other
            )
        return Money(cents=self.cents - other.cents)

class WithdrawalSuccess(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[WithdrawalResultKind.SUCCESS]
    new_balance: Money

class InsufficientFunds(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[WithdrawalResultKind.INSUFFICIENT_FUNDS]
    current_balance: Money
    requested: Money

type WithdrawalResult = WithdrawalSuccess | InsufficientFunds

class Account(BaseModel):
    model_config = {"frozen": True}
    balance: Money
    
    def withdraw(self, amount: Money) -> WithdrawalResult:
        # Delegate to the Type. No manual 'if' guards.
        match self.balance.subtract(amount):
            case InsufficientFunds() as f:
                return f
            case Money() as new_balance:
                return WithdrawalSuccess(kind=WithdrawalResultKind.SUCCESS, new_balance=new_balance)
```

---

## 3. The NoOp (Doing Nothing)
Sometimes the correct decision is to do nothing. Return an explicit `NoOp` or `Skipped` type, never `None`.

### ✅ Pattern: Explicit NoOp
```python
class PaymentResultKind(StrEnum):
    SKIPPED = "skipped"
    PROCESSED = "processed"

class PaymentSkipped(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[PaymentResultKind.SKIPPED]
    reason: SkippedReason

type PaymentResult = PaymentProcessed | PaymentSkipped
```

---

## Cognitive Checks
- [ ] **No Raises:** Did I remove `raise` statements?
- [ ] **Smart Enums:** Am I using `StrEnum` for `kind`?
- [ ] **Explicit Return Type:** Is the return type a Union of models?
- [ ] **No Implicit None:** Did I remove `return None`?
- [ ] **No Defensive Ifs:** Did I delegate the rule to the Value Object?
- [ ] **Method on Model:** Is the logic on the Aggregate/Value Object, not a standalone function?
- [ ] **Value Objects:** Am I using `Money`, not `int`? `SkippedReason`, not `str`?
