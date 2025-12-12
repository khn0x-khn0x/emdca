# Pattern 04: Execution (Intent as Data)

## The Principle
Deciding to do something and doing it are separate concerns. The "Core" decides; the "Shell" executes.

## The Mechanism
The domain model returns inert, serializable **Command Objects (Intents)** describing side effects. These intents contain all parameters required for execution. The Shell executes these intents without needing to query the Context.

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

## 2. Intent as Data
Instead of *calling* the function, we return a *description* of the call.

### ✅ Pattern: The Intent Model
```python
from typing import Literal
from pydantic import BaseModel

class SendEmailIntent(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["send_email"] = "send_email"
    to: str
    subject: str
    body: str

class NoOpIntent(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["no_op"] = "no_op"

# AI-Native Intent Example
class AnalyzeSentimentIntent(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["analyze_sentiment"] = "analyze_sentiment"
    user_text: str
    # We treat the prompt template as configuration, not code
    system_prompt_id: str = "sentiment_v1"

# The Intent Union
type ActionIntent = SendEmailIntent | AnalyzeSentimentIntent | NoOpIntent
```

---

## 3. The Pure Decision
The domain logic becomes a pure function that maps `Input -> Intent`.

### ✅ Pattern: Deciding the Intent
```python
def decide_signup_action(user: User) -> ActionIntent:
    # Pure Logic: No mocking required.
    # We just assert that the returned object matches our expectation.
    
    if user.is_vip:
        return SendEmailIntent(
            to=user.email,
            subject="Welcome VIP",
            body="Here is your gold status..."
        )
        
    return NoOpIntent()
```

---

## 4. The Shell Executor (The Roadie)
The shell (Service Layer) is the only place where side effects happen. It blindly follows instructions.

### ✅ Pattern: The Interpreter Loop
```python
async def handle_request(data: dict):
    # ... construction & decision ...
    
    match intent:
        case SendEmailIntent(to=t, subject=s, body=b):
            smtp_client.send_message(t, s, b)
            
        case AnalyzeSentimentIntent(user_text=text, system_prompt_id=pid):
            # The Shell calls the AI Agent (See Pattern 07 & 10)
            result = await sentiment_agent.run(text, prompt_id=pid)
            
        case NoOpIntent():
            pass
```

## 5. Cognitive Checks
*   [ ] **Serializable:** Is the Intent just data? (No functions, no closures).
*   [ ] **Complete:** Does the Intent contain *everything* needed to execute? (The Shell shouldn't have to look up the user's email; it should be *in* the Intent).
*   [ ] **Testable:** Can I test `decide_signup_action` without `unittest.mock`?
