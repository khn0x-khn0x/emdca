# Pattern 04: Execution (Intent as Contract)

## The Principle
Deciding to do something and doing it are separate concerns. The "Core" decides; the "Shell" executes.

## The Mechanism
The domain model returns inert, serializable **Specification Objects (Intents)** describing side effects AND their outcome interpretation. These intents contain all parameters required for execution and outcome mapping. The Shell executes these intents using a generic executor without needing to query the Context or make interpretation decisions.

---

## 1. The Hidden Side Effect (Anti-Pattern)
Mixing decision-making with execution makes the system impossible to test without mocking.

### ❌ Anti-Pattern: Mixed Concerns
```python
def process_signup(user: User):
    if user.is_vip:
        # ❌ Side Effect!
        # Requires mocking SMTP server just to test the logic.
        smtp_client.send(
            to=user.email, 
            subject="Welcome VIP",
            body="..."
        )
```

---

## 2. Intent as Contract (Complete Specification)

Instead of *calling* the function, we return a *complete specification* of the call—including how to interpret outcomes.

### ✅ Pattern: The Self-Interpreting Intent
```python
from typing import Literal, Any
from pydantic import BaseModel

class SendEmailIntent(BaseModel):
    """
    A Complete Specification.
    
    The Intent carries:
    1. Execution parameters (to, subject, body)
    2. Exception classification (what errors are "expected")
    3. Outcome mapping (how to interpret success/failure)
    """
    model_config = {"frozen": True}
    kind: Literal["send_email"] = "send_email"
    
    # Execution Parameters
    to: str
    subject: str
    body: str
    
    # Exception Classification (Domain decides what's "expected failure" vs "panic")
    catch_exceptions: tuple[str, ...] = ("SmtpConnectionError", "RecipientRejectedError")
    
    # Outcome Mapping (Domain logic—lives on the Intent, not in Shell)
    def on_success(self, message_id: str) -> "EmailSent":
        """Receives primitives extracted by Shell, not raw infrastructure response."""
        return EmailSent(
            message_id=message_id,
            recipient=self.to,
        )
    
    def on_failure(self, error: str) -> "EmailFailed":
        return EmailFailed(
            recipient=self.to,
            error=error,
        )

# Result Types (The Intent's vocabulary)
class EmailSent(BaseModel):
    kind: Literal["sent"] = "sent"
    message_id: str
    recipient: str

class EmailFailed(BaseModel):
    kind: Literal["failed"] = "failed"
    recipient: str
    error: str

type SendEmailResult = EmailSent | EmailFailed

class NoOp(BaseModel):
    """Domain decided no action is needed."""
    model_config = {"frozen": True}
    kind: Literal["no_op"] = "no_op"
    reason: str | None = None

# The Intent Union
# Note: NoOp is NOT an Intent (not executable), it's a decision outcome.
type DecisionOutcome = SendEmailIntent | NoOp
```

### 💡 Why Methods on the Intent?

The same principle as Pattern 07 (Foreign Reality → Internal Truth), but inverted:

| Direction | Owner | Method |
|-----------|-------|--------|
| **Inbound** (API → Domain) | Foreign Model | `.to_domain()` |
| **Outbound** (Execution → Result) | Intent | `.on_success()` / `.on_failure()` |

The Intent knows what success means for THIS operation. The Shell doesn't.

---

## 3. The Pure Decision
The domain logic becomes a pure function that maps `Input -> Intent`.

### ✅ Pattern: Deciding the Intent
```python
def decide_signup_action(user: User) -> DecisionOutcome:
    # Pure Logic: No mocking required.
    # We just assert that the returned object matches our expectation.
    
    if user.is_vip:
        return SendEmailIntent(
            to=user.email,
            subject="Welcome VIP",
            body="Here is your gold status..."
        )
        
    return NoOp()
```

---

## 4. The Generic Executor (The Dumb Interpreter)

The Shell provides ONE generic function that can execute ANY Intent. It reads the specification and applies it—nothing more.

### ✅ Pattern: The Spec Executor
```python
from typing import Any, Awaitable, Callable

# Exception registry maps string names → actual exception classes
# (Strings in Intent keep it serializable; registry lives in Shell)
EXCEPTION_REGISTRY: dict[str, type[Exception]] = {
    "SmtpConnectionError": SmtpConnectionError,
    "RecipientRejectedError": RecipientRejectedError,
    # ... infrastructure exceptions ...
}

async def execute[TSuccess, TFailure](
    operation: Callable[[], Awaitable[Any]],
    catch_names: tuple[str, ...],
    on_success: Callable[[Any], TSuccess],
    on_failure: Callable[[str], TFailure],
) -> TSuccess | TFailure:
    """
    The Generic Executor.
    
    Zero business logic. Reads the spec. Applies it.
    Works for ANY Intent without modification.
    """
    catch_types = tuple(EXCEPTION_REGISTRY[name] for name in catch_names)
    
    try:
        result = await operation()
        return on_success(result)
    except catch_types as e:
        return on_failure(str(e))
```

### ✅ Pattern: The Interpreter Loop (Dispatcher)
```python
async def handle_request(user: User):
    # 1. Decide (Pure)
    outcome = decide_signup_action(user)
    
    # 2. Dispatch (Shell)
    match outcome:
        case NoOp():
            # Explicitly do nothing. No executor needed.
            pass

        case SendEmailIntent() as intent:
            # Intents go to the Executor via the Adapter
            # The Adapter just provides the 'operation' lambda
            await execute(
                operation=lambda: smtp_client.send(...),
                catch_names=intent.catch_exceptions,
                # Shell extracts primitives from infrastructure response
                on_success=lambda result: intent.on_success(message_id=result.message_id),
                on_failure=intent.on_failure,
            )
```

### 💡 The Test: Can You Add a New Intent Without Shell Changes?

If adding `SendSmsIntent` requires writing new exception handling or result construction in the Shell, the pattern is broken. The generic executor should handle it automatically.

## 5. Cognitive Checks
*   [ ] **Serializable:** Is the Intent just data? (No functions stored—methods are fine, closures are not).
*   [ ] **Complete Specification:** Does the Intent define `on_success()`, `on_failure()`, and `catch_exceptions`?
*   [ ] **Generic Executor:** Can the Shell execute this Intent using the same generic `execute()` function as all other Intents?
*   [ ] **Primitive Parameters:** Do `on_success`/`on_failure` receive only primitives (str, int, bool), never `Any` or foreign objects?
*   [ ] **Delegated Construction:** Does the Shell delegate Result construction to the Intent's `on_success` / `on_failure` methods?
*   [ ] **Testable Mapping:** Can I test `intent.on_success(mock_result)` as a pure function without infrastructure?
