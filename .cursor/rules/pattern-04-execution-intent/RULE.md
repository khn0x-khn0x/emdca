---
description: "Pattern 04: Execution — Intent as Contract. Domain decides, Shell executes, models parse."
globs: ["**/domain/**/*.py", "**/service/**/*.py"]
alwaysApply: false
---

# Pattern 04: Execution Intent

## Valid Code Structure

```python
# Intent: Complete specification of what to do AND how to interpret results
class SendEmailIntent(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["send_email"]  # NO DEFAULT
    
    to: EmailStr
    subject: str
    body: str
    handled_failures: tuple[SmtpFailure, ...]  # NO DEFAULT
    
    def is_handled(self, failure: SmtpFailure) -> bool:
        """Check if a failure type is in the handled set."""
        return failure in self.handled_failures
    
    def on_sent(self, outcome: SmtpSent) -> EmailSent:
        return EmailSent(kind="email_sent", message_id=outcome.message_id, recipient=self.to)
    
    def on_failed(self, outcome: SmtpFailed) -> EmailFailed:
        return EmailFailed(kind="email_failed", recipient=self.to, failure=outcome.failure)

# NoOp: Explicit "do nothing" decision
class NoOp(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["no_op"]  # NO DEFAULT
    reason: str

type SignupDecision = SendEmailIntent | NoOp

# Aggregate returns Intent
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

# Executor: Composes Intent + RawResult → DomainOutcome (no try/except)
class EmailExecutor(BaseModel):
    model_config = {"frozen": True}
    client: SmtpClient
    
    def execute(self, intent: SendEmailIntent, raw: RawSmtpResult) -> EmailResult:
        outcome = self.client.parse(raw)  # raw.to_foreign().to_domain()
        
        match outcome:
            case SmtpClientSuccess(message_id=mid):
                return intent.on_sent(SmtpSent(kind="smtp_sent", message_id=mid))
            case SmtpClientError(failure=f) if intent.is_handled(f):
                return intent.on_failed(SmtpFailed(kind="smtp_failed", failure=f))
            case SmtpClientError(failure=f):
                return EmailUnhandled(kind="email_unhandled", recipient=intent.to, failure=f)
```

## Constraints

| Required | Forbidden |
|----------|-----------|
| Intent carries parameters + outcome mapping | Side effects in domain |
| `on_success`/`on_failure` methods on Intent | `try/except` in executor |
| `raw.to_foreign().to_domain()` chain | Exceptions for control flow |
| Infrastructure returns Sum Type | Service/Client injection into domain |
| `handled_failures` explicit | Default values on Intent fields |

