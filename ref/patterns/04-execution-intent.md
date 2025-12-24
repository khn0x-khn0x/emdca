# Pattern 04: Execution (Intent as Contract)

## The Principle
Deciding to do something, doing it, and interpreting the result are three separate concerns. The Domain decides and specifies interpretation. Infrastructure captures raw reality. The Shell composes models—never catching exceptions.

## The Mechanism
1. **The Domain** returns inert, serializable **Intents** specifying what to do AND how to interpret outcomes
2. **Infrastructure** captures raw results as **Sum Types** (success or failure variants)—no exceptions escape
3. **Foreign Models** translate raw infrastructure data through a `.to_foreign().to_domain()` chain
4. **The Shell** composes these models: Intent + RawResult → DomainOutcome

The Domain never sees exceptions. It only sees data.

---

## ❌ Anti-Pattern: Mixed Concerns

Decision-making mixed with execution makes the system impossible to test without mocking.

```python
def process_signup(user: User):
    if user.is_vip:
        smtp_client.send(to=user.email, subject="Welcome VIP", body="...")  # ❌ Side effect!
```

---

## Supporting Types

These types form the outcome chain. Showing shape, not exhaustive fields.

```python
# Failures are explicit domain types (Smart Enum)
class SmtpFailure(StrEnum):
    CONNECTION_FAILED = "connection_failed"
    TIMEOUT = "timeout"
    RECIPIENT_REJECTED = "recipient_rejected"
    # ...

# Client-level outcomes (Sum Type)
class SmtpClientSuccess(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["client_success"]
    message_id: str

class SmtpClientError(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["client_error"]
    failure: SmtpFailure
    detail: SmtpErrorDetail  # SmtpErrorWithCode | SmtpErrorNoCode

type SmtpClientOutcome = SmtpClientSuccess | SmtpClientError

# Infrastructure outcomes (what Intent interprets)
class SmtpSent(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["smtp_sent"]
    message_id: str

class SmtpFailed(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["smtp_failed"]
    failure: SmtpFailure

# Executor-level outcomes (final result)
class EmailSent(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["email_sent"]
    message_id: str
    recipient: EmailStr

class EmailFailed(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["email_failed"]
    recipient: EmailStr
    failure: SmtpFailure

class EmailUnhandled(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["email_unhandled"]
    recipient: EmailStr
    failure: SmtpFailure

type EmailResult = EmailSent | EmailFailed | EmailUnhandled
```

---

## ✅ Pattern: The Self-Interpreting Intent

The Intent carries execution parameters AND outcome interpretation. The Domain decides what failures it handles gracefully.

```python
class SendEmailIntent(BaseModel):
    """Complete specification: what to do AND how to interpret results."""
    model_config = {"frozen": True}
    kind: Literal["send_email"]
    
    to: EmailStr
    subject: str
    body: str
    handled_failures: tuple[SmtpFailure, ...]  # NO DEFAULT—explicit
    
    def on_sent(self, outcome: SmtpSent) -> EmailSent:
        return EmailSent(kind="email_sent", message_id=outcome.message_id, recipient=self.to)
    
    def on_failed(self, outcome: SmtpFailed) -> EmailFailed:
        return EmailFailed(kind="email_failed", recipient=self.to, failure=outcome.failure)
    
    def is_handled(self, failure: SmtpFailure) -> bool:
        return failure in self.handled_failures


class NoOp(BaseModel):
    """Domain decided no action needed."""
    model_config = {"frozen": True}
    kind: Literal["no_op"]
    reason: str  # NO DEFAULT—must be explicit


type SignupDecision = SendEmailIntent | NoOp
```

The Aggregate returns the Intent:

```python
class User(BaseModel):
    model_config = {"frozen": True}
    id: str
    email: EmailStr
    is_vip: bool
    
    def decide_signup_action(self) -> SignupDecision:
        if self.is_vip:
            return SendEmailIntent(
                kind="send_email",
                to=self.email,
                subject="Welcome VIP",
                body="...",
                handled_failures=(SmtpFailure.CONNECTION_FAILED, SmtpFailure.TIMEOUT),
            )
        return NoOp(kind="no_op", reason="Non-VIP user")
```

---

## ✅ Pattern: Infrastructure as Sum Type

Raw infrastructure results are captured as data—never as exceptions. Each outcome variant is explicit.

```python
class RawSmtpSuccess(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["raw_success"]
    message_id: str

class RawSmtpConnectError(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["connect_error"]
    message: str

# ... other failure variants: timeout, recipients_refused, response_error, unknown

type RawSmtpResult = RawSmtpSuccess | RawSmtpConnectError | ...  # Sum Type
```

---

## ✅ Pattern: Foreign Model Translation

Foreign Models mirror external reality and own the translation to domain types. The chain is: `Raw → Foreign → Domain`.

```python
class SmtpConnectErrorForeign(BaseModel):
    """Mirrors what smtplib.SMTPConnectError contains."""
    model_config = {"frozen": True}
    message: str
    
    def to_domain(self) -> SmtpClientError:
        return SmtpClientError(
            kind="client_error",
            failure=SmtpFailure.CONNECTION_FAILED,
            detail=SmtpErrorNoCode(kind="no_code", message=self.message),
        )


class RawSmtpConnectError(BaseModel):
    """Raw data from infrastructure edge."""
    model_config = {"frozen": True}
    kind: Literal["connect_error"]
    message: str
    
    def to_foreign(self) -> SmtpConnectErrorForeign:
        return SmtpConnectErrorForeign(message=self.message)
```

Usage: `raw.to_foreign().to_domain()` — pure model composition.

---

## ✅ Pattern: The Pure Executor

The Executor composes models. It receives raw data, parses through the Foreign Model chain, and interprets via the Intent. No try/except—just pattern matching.

```python
class SmtpClient(BaseModel):
    model_config = {"frozen": True}
    host: str
    port: int
    
    def parse(self, raw: RawSmtpResult) -> SmtpClientOutcome:
        match raw:
            case RawSmtpSuccess():
                return raw.to_foreign().to_domain()
            case RawSmtpConnectError():
                return raw.to_foreign().to_domain()
            # ... other variants


class EmailExecutor(BaseModel):
    model_config = {"frozen": True}
    client: SmtpClient
    
    def execute(self, intent: SendEmailIntent, raw: RawSmtpResult) -> EmailResult:
        outcome = self.client.parse(raw)
        
        match outcome:
            case SmtpClientSuccess(message_id=mid):
                return intent.on_sent(SmtpSent(kind="smtp_sent", message_id=mid))
            
            case SmtpClientError(failure=f) if intent.is_handled(f):
                return intent.on_failed(SmtpFailed(kind="smtp_failed", failure=f))
            
            case SmtpClientError(failure=f):
                return EmailUnhandled(kind="email_unhandled", recipient=intent.to, failure=f)
```

---

## ✅ Pattern: Composing the Request

No optionality. If the decision requires infrastructure, pair Intent with its result as a Sum Type.

```python
class ExecutableEmail(BaseModel):
    """Intent paired with its infrastructure result."""
    model_config = {"frozen": True}
    kind: Literal["executable_email"]
    intent: SendEmailIntent
    raw: RawSmtpResult

type DispatchRequest = ExecutableEmail | NoOp  # Not raw | None
```

---

## Composition Root

```python
client = SmtpClient(host="smtp.example.com", port=587)
executor = EmailExecutor(client=client)

# At runtime:
decision = user.decide_signup_action()

match decision:
    case NoOp() as no_op:
        result = no_op
    case SendEmailIntent() as intent:
        raw: RawSmtpResult = ...  # From infrastructure edge
        result = executor.execute(intent, raw)
```

---

## Cognitive Checks

- [ ] **Intent is Complete:** Carries parameters AND outcome mapping
- [ ] **No try/except:** Models parse, they don't catch
- [ ] **No Default Values:** `handled_failures`, `reason` explicit at construction
- [ ] **No Optionality:** Sum Types replace `| None`
- [ ] **Foreign Model Chain:** `raw.to_foreign().to_domain()`
- [ ] **Executor Pattern-Matches:** No `isinstance()`, no `raise`
