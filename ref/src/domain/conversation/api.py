"""
THE FOREIGN REALITY (API Contract)

Role: Defines the schema of the HTTP Interface (Requests/Responses).
Mandate: Mandate VII (Translation).
Pattern: ref/patterns/07-acl-translation.md

Constraint:
- Frozen Pydantic models defining the "Public" language.
- Owns .to_domain() to naturalize input into Internal Truth.

Example Implementation:
```python
from pydantic import BaseModel

class CreateMessageRequest(BaseModel):
    model_config = {"frozen": True}
    conversation_id: ConversationId
    content: MessageContent

    def to_domain(self) -> "Message":
        return Message(
            conversation_id=self.conversation_id,
            content=self.content,
        )
```
"""
