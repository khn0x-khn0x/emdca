---
description: "Pattern 09: Workflow — Process as explicit State Machine with transition methods."
globs: ["**/process.py", "**/workflow.py", "**/domain/**/*.py"]
alwaysApply: false
---

# Pattern 09: Workflow State Machine

## Valid Code Structure

```python
# Each workflow state is its own type
class SignupPending(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["pending"]  # NO DEFAULT
    email: EmailStr
    
    def verify(self, user_id: str) -> tuple["SignupVerified", "SendEmailIntent"]:
        new_state = SignupVerified(kind="verified", user_id=user_id)
        intent = SendEmailIntent(to=self.email, template="welcome")
        return new_state, intent

class SignupVerified(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["verified"]  # NO DEFAULT
    user_id: str
    
    def complete(self) -> tuple["SignupCompleted", "NotifyAdminIntent"]:
        new_state = SignupCompleted(kind="completed", user_id=self.user_id)
        intent = NotifyAdminIntent(user_id=self.user_id)
        return new_state, intent

class SignupCompleted(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["completed"]  # NO DEFAULT
    user_id: str

# Sum Type for all states
type SignupState = Annotated[
    SignupPending | SignupVerified | SignupCompleted,
    Field(discriminator="kind")
]

# Workflow Runner: Frozen model with dependencies as fields
class WorkflowRunner(BaseModel):
    model_config = {"frozen": True}
    
    workflow: SignupWorkflow  # Injected
    store: WorkflowStore      # Injected
    
    def run(self, workflow_id: str, event: WorkflowEvent, db: Session) -> RunResult:
        state = self.store.fetch(workflow_id, db)
        new_state, intent = self.workflow.step(state, event)
        self.store.save(workflow_id, new_state, db)
        return RunResult(kind="stepped", intent=intent)
```

## Constraints

| Required | Forbidden |
|----------|-----------|
| Each state is its own frozen type | One class with `status` field |
| Transition methods on source state | Standalone `def verify_signup()` functions |
| Returns `(NewState, Intent)` tuple | Side effects in transition |
| `kind: Literal["..."]` discriminator | `kind: Literal["..."] = "..."` default |
| Runner is frozen model with dependency fields | Procedural `if/else` chains |
| State serializable to JSON/DB | Closures or callbacks in state |

