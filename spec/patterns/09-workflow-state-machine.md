# Pattern 09: Workflow (Process as State Machine)

## The Principle
The sequence of business steps is Business Logic, not plumbing. Workflows must be modeled as State Machines in the Domain.

## The Mechanism
**Workflow Models** represent the lifecycle of a process. The Domain returns **Next-Step Intents** indicating the next logical action. Factories determine state transitions based on current state and input.

---

## 1. The Procedural Trap (Anti-Pattern)
Defining the sequence of events as imperative code makes the process rigid and opaque.

### ❌ Anti-Pattern: Hardcoded Sequence
```python
async def handle_signup(data):
    # ❌ The "Flow" is buried in the code structure
    user = await create_user(data)
    
    if user.score > 50:
        await send_email(user)
        await notify_admin(user)
    else:
        await send_rejection(user)
```

---

## 2. The Workflow Model (State Machine)
We model the process itself as a Sum Type.

### ✅ Pattern: Explicit States
```python
from typing import Literal, Annotated
from pydantic import BaseModel, Field

# The States
class SignupPending(BaseModel):
    kind: Literal["pending"] = "pending"
    email: str

class SignupVerified(BaseModel):
    kind: Literal["verified"] = "verified"
    user_id: str

class SignupCompleted(BaseModel):
    kind: Literal["completed"] = "completed"
    user_id: str

# The Workflow Union
type SignupState = Annotated[
    SignupPending | SignupVerified | SignupCompleted,
    Field(discriminator="kind")
]
```

---

## 3. The Transition Function (The Brain)
The Logic decides "What happens next?" based on the current state. It returns a tuple: `(NewState, Intent)`.

### ✅ Pattern: The Step Function
```python
# src/domain/onboarding/workflow.py (Specific Naming)
from domain.onboarding.api import SignupRequest # Foreign Model

def step_signup(
    state: SignupState, 
    input: SignupRequest
) -> tuple[SignupState, ActionIntent]:
    
    match state:
        case SignupPending(email=e):
            if input.is_verified:
                # Transition: Pending -> Verified
                new_state = SignupVerified(user_id="123")
                # Side Effect: Send Welcome Email
                intent = SendEmailIntent(to=e, ...)
                return new_state, intent
            
            return state, NoOpIntent()

        case SignupVerified():
            # Transition: Verified -> Completed
            return SignupCompleted(...), NotifyAdminIntent(...)
            
        case SignupCompleted():
            # Terminal State
            return state, HaltIntent()
```

### ✅ Pattern: Probabilistic Transitions (AI Agents)
An "AI Agent" is simply a State Machine where the transition logic uses probabilistic inference instead of deterministic rules.

```python
def step_agent(state: AgentState, input: UserMessage) -> tuple[AgentState, ActionIntent]:
    # The Logic is still Pure: It returns an Intent to ASK the LLM
    match state:
        case Thinking():
            # Intent: "Ask the LLM what to do next"
            return state, InferNextStepIntent(history=state.history)
            
        case Deciding(llm_response=response):
            # Deterministic Routing based on Probabilistic Output
            if response.tool_call == "calculator":
                return Calculating(), CallToolIntent(...)
            else:
                return Responding(), SendMessageIntent(...)
```

---

## 4. The Runner (The Engine)
The Service Layer becomes a generic engine that drives the state machine forward.

### ✅ Pattern: The Recursive Loop
```python
def run_workflow(repo: WorkflowRepo, workflow_id: str, input_data: dict):
    # 1. Load Current State
    state = repo.get(workflow_id)

    # 2. Compute Next Step (Pure)
    new_state, intent = step_signup(state, input_data)

    # 3. Persist State
    repo.save(new_state)

    # 4. Execute Side Effect
    match intent:
        case SendEmailIntent(...): ...
        case HaltIntent(): return
```

## 5. Cognitive Checks
*   [ ] **No Await in Step:** Is the `step()` function purely synchronous?
*   [ ] **Explicit Next Step:** Does the function return the `Intent` for the *next* action?
*   [ ] **State Persistence:** Is the entire `SignupState` serializable to JSON/DB?
