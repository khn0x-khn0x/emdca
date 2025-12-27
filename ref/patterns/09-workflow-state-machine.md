# Pattern 09: Workflow (State Machine)

## The Principle
Complex business processes are State Machines. We model them as explicit state transitions. The Workflow is a sequence of `(State, Event) -> (NewState, Intent)` transitions.

## The Mechanism
1.  **States:** Sum Types representing every step, discriminated by a **Smart Enum**.
2.  **Events:** Sum Types representing what happened.
3.  **Transition:** A pure function `step(state, event)` returning the next state and side effects (Intents).
4.  **Runtime:** An **Active Domain Model** that loads state, calls transition, saves state, and returns output.

---

## 1. The Procedural Workflow (Anti-Pattern)
Implicit state in variables or database columns leads to spaghetti code.

### ❌ Anti-Pattern: Status Checks
```python
if order.status == "pending" and event == "pay":
    order.status = "paid"
    send_email()
elif order.status == "paid":
    ...
```

---

## 2. The State Machine
The Type System defines the graph. Note the use of **Value Objects** (`UserId`, `Email`) instead of primitives.

### ✅ Pattern: Explicit Transitions with Smart Enums
```python
from enum import StrEnum

# 1. Behavioral Type (The Graph Definition)
class SignupKind(StrEnum):
    PENDING = "pending"
    VERIFIED = "verified"
    COMPLETED = "completed"

# 2. State Models (The Nodes)
class SignupPending(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[SignupKind.PENDING]
    email: Email
    
    def verify(self, user_id: UserId) -> tuple["SignupVerified", "SendEmailIntent"]:
        # Pure Transition: New State + Intent
        new_state = SignupVerified(kind=SignupKind.VERIFIED, user_id=user_id)
        intent = SendEmailIntent(to=self.email, template=TemplateName.WELCOME)
        return new_state, intent

class SignupVerified(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[SignupKind.VERIFIED]
    user_id: UserId
    
    def complete(self) -> tuple["SignupCompleted", "NotifyAdminIntent"]:
        new_state = SignupCompleted(kind=SignupKind.COMPLETED, user_id=self.user_id)
        intent = NotifyAdminIntent(user_id=self.user_id)
        return new_state, intent

class SignupCompleted(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[SignupKind.COMPLETED]
    user_id: UserId

# 3. Sum Type (The Machine)
type SignupState = Annotated[
    SignupPending | SignupVerified | SignupCompleted,
    Field(discriminator="kind")
]
```

---

## 3. The Runtime (Active Model)
The runtime manages the persistence lifecycle. It is a **Smart Domain Model** holding the Store Capability.

### ✅ Pattern: The Active Loop
```python
class WorkflowRuntime(BaseModel):
    """Active Domain Model. Drives the State Machine."""
    model_config = {"frozen": True, "arbitrary_types_allowed": True}
    
    # Injected Capability
    store: WorkflowStore
    
    async def run_step(self, id: WorkflowId, event: WorkflowEvent) -> RunResult:
        # 1. Load (Generic I/O)
        state = await self.store.load(id)
        if not state:
            return WorkflowNotFound(id=id)
        
        # 2. Step (Pure Logic)
        # Delegate to the Domain Model
        new_state, intent = state.handle(event)
        
        # 3. Save (Generic I/O)
        await self.store.save(id, new_state)
        
        # 4. Return Intent for Execution
        return RunResult(kind=RunKind.STEPPED, intent=intent)
```

---

## Cognitive Checks
- [ ] **State Types:** Is every state a distinct model?
- [ ] **Smart Enums:** Are state kinds defined by `StrEnum`?
- [ ] **Value Objects:** Are IDs and fields typed (`UserId`), not strings?
- [ ] **Pure Transitions:** Do transitions return `(State, Intent)`, doing no I/O?
- [ ] **Runtime is Model:** Is the runner a `BaseModel` holding the Store?
