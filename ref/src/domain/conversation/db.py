"""
THE FOREIGN REALITY (Database Schema)

Role: Defines the shape of the database tables.
Mandate: Mandate VI (Storage).
Pattern: ref/patterns/06-storage-foreign-reality.md

Constraint:
- Frozen Pydantic models mirroring DB tables.
- Owns `.to_domain()` method.
- No active logic.

Example Implementation:
```python
class DbConversation(BaseModel):
    model_config = {"frozen": True}
    id: ConversationId
    status: ConversationStatus

    def to_domain(self) -> Conversation:
        return Conversation(...)
```
"""
