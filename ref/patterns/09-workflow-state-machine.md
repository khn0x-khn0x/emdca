# Pattern 09: Workflow (Process as State Machine)

## The Principle
The sequence of business steps is Business Logic, not plumbing. Workflows must be modeled as State Machines in the Domain.

## The Mechanism
**Workflow Models** represent the lifecycle of a process. Each state is a frozen Pydantic model with transition methods that return the next state and an Intent.

---

## 1. The Procedural Trap (Anti-Pattern)
Defining the sequence of events as imperative code makes the process rigid and opaque.

### ❌ Anti-Pattern: Hardcoded Sequence
```python
async def handle_signup(data):  # ❌ Standalone function
    user = await create_user(data)
    
    if user.score > 50:  # ❌ Business logic in orchestrator
        await send_email(user)
```

---

## 2. The Workflow Model (State Machine)
We model the process as a Sum Type. Each state has transition methods.

### ✅ Pattern: Explicit States with Transitions
```python
from typing import Literal, Annotated
from pydantic import BaseModel, Field, EmailStr


class SignupPending(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["pending"]  # NO DEFAULT
    email: EmailStr
    
    def verify(self, user_id: str) -> tuple["SignupVerified", "SendEmailIntent"]:
        """Transition: Pending → Verified."""
        new_state = SignupVerified(kind="verified", user_id=user_id)
        intent = SendEmailIntent(to=self.email, template="welcome")
        return new_state, intent


class SignupVerified(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["verified"]  # NO DEFAULT
    user_id: str
    
    def complete(self) -> tuple["SignupCompleted", "NotifyAdminIntent"]:
        """Transition: Verified → Completed."""
        new_state = SignupCompleted(kind="completed", user_id=self.user_id)
        intent = NotifyAdminIntent(user_id=self.user_id)
        return new_state, intent


class SignupCompleted(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["completed"]  # NO DEFAULT
    user_id: str
    
    def step(self) -> tuple["SignupCompleted", "HaltIntent"]:
        """Terminal state—no transition."""
        return self, HaltIntent()


type SignupState = Annotated[
    SignupPending | SignupVerified | SignupCompleted,
    Field(discriminator="kind")
]
```

---

## 3. Handling State Transitions
Pattern matching dispatches to the appropriate transition method.

### ✅ Pattern: Transition Dispatcher
```python
class SignupWorkflow(BaseModel):
    """Workflow handler with dispatch logic."""
    model_config = {"frozen": True}
    
    def step(self, state: SignupState, verified: bool) -> tuple[SignupState, ActionIntent]:
        match state:
            case SignupPending() if verified:
                return state.verify(user_id="generated-id")
            
            case SignupPending():
                return state, NoOpIntent()
            
            case SignupVerified():
                return state.complete()
            
            case SignupCompleted():
                return state.step()
```

---

## 4. The Runner (Workflow Engine)
The runner is a frozen Pydantic model with **dependencies as fields**.

### ✅ Pattern: Workflow Runner Model
```python
class WorkflowRunner(BaseModel):
    """Engine that drives the state machine."""
    model_config = {"frozen": True}
    
    workflow: SignupWorkflow    # Injected: the workflow logic
    store: WorkflowStore        # Injected: handles state persistence
    
    def run(self, workflow_id: str, verified: bool, db: Session) -> RunResult:
        # 1. Load Current State (via injected store)
        state = self.store.fetch(workflow_id, db)
        
        # 2. Compute Next Step (Pure)
        new_state, intent = self.workflow.step(state, verified)
        
        # 3. Persist State (via injected store)
        self.store.save(workflow_id, new_state, db)
        
        # 4. Return intent for execution
        return RunResult(kind="stepped", intent=intent)
```

---

## 5. AI Agents as State Machines
An "AI Agent" is a State Machine where transition logic uses inference.

### ✅ Pattern: Agent States
```python
class AgentThinking(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["thinking"]
    history: tuple[Message, ...]
    
    def infer(self) -> tuple["AgentThinking", "InferNextStepIntent"]:
        return self, InferNextStepIntent(history=self.history)


class AgentDeciding(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["deciding"]
    llm_response: LlmResponse
    
    def route(self) -> tuple[AgentState, ActionIntent]:
        if self.llm_response.tool_call == "calculator":
            return AgentCalculating(kind="calculating"), CallToolIntent()
        return AgentResponding(kind="responding"), SendMessageIntent()
```

---

## Cognitive Checks
- [ ] **Dependencies as Fields:** Does the runner have `store: WorkflowStore` as a field?
- [ ] **No Defaults on kind:** Is every `kind: Literal[...]` explicit?
- [ ] **Transitions are Methods:** Is `verify()` a method on `SignupPending`, not a standalone function?
- [ ] **Runner is a Model:** Is the runner a `BaseModel`, not a standalone function?
- [ ] **All States Frozen:** Does every state have `model_config = {"frozen": True}`?
- [ ] **State Serializable:** Is the entire state serializable to JSON/DB?
