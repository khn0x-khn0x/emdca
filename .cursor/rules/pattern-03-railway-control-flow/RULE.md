---
description: "Pattern 03: Control Flow — Railway oriented programming. No exceptions for domain logic."
globs: ["**/domain/**/*.py"]
alwaysApply: false
---

# Pattern 03: Railway Control Flow

## Valid Code Structure

```python
# Explicit Result Types
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

# Decision method on aggregate — routes to success or failure track
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

# Explicit NoOp for "do nothing" cases
class RefundSkipped(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["skipped"]  # NO DEFAULT
    reason: str
```

## Constraints

| Required | Forbidden |
|----------|-----------|
| Return `Success \| Failure` Sum Type | `raise Exception()` for logic |
| Decision logic as method on aggregate | Standalone functions |
| Explicit `Skipped`/`NoOp` type | `return None` |
| `match/case` to handle tracks | `try/except` |
| Return type tells the whole truth | Hidden failure paths |

