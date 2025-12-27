"""
THE DATA CONTRACTS (Intents & Interfaces)

Role: Defines the inputs and outputs of the Domain.
Mandate: Mandate IV (Execution).
Pattern: ref/patterns/04-execution-intent.md

Constraint:
- Frozen Pydantic Models.
- Intents describe "What to do" (Data).
- Results describe "What happened" (Data).
- Use Smart Enums for Kinds.

Example Implementation:
```python
class IntentKind(StrEnum):
    SEND_MESSAGE = "send_message"

class SendMessageIntent(BaseModel):
    kind: Literal[IntentKind.SEND_MESSAGE]
    content: MessageContent
```
"""
