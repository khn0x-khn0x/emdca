"""
THE STORE (Database Executor)

Role: Frozen Pydantic model that handles DB I/O and returns Sum Types.
Mandate: Mandate VI (Storage) & VII (Translation).
Pattern: ref/patterns/06-storage-foreign-reality.md

Constraint:
- Store is a frozen Pydantic model with DB connection as field.
- Methods return Sum Types (Found | NotFound, Saved | SaveFailed).
- Uses Foreign Models for raw DB shapes.
- Owns translation: raw -> foreign -> domain.

Example Implementation:
```python
from pydantic import BaseModel
from typing import Literal

# Foreign Model (mirrors DB shape)
class DbConversation(BaseModel):
    model_config = {"frozen": True}
    id: str
    status: str

    def to_domain(self) -> "Conversation":
        match self.status:
            case "active":
                return Active(kind="active", conversation_id=self.id)
            case "archived":
                return Archived(kind="archived", conversation_id=self.id, reason="")

# Result Sum Types
class ConversationFound(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["found"]
    conversation: Conversation

class ConversationNotFound(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["not_found"]
    conversation_id: str

type FetchResult = ConversationFound | ConversationNotFound

# Store Executor (dependencies as fields)
class ConversationStore(BaseModel):
    model_config = {"frozen": True}
    db: DatabaseConnection  # Injected dependency

    async def fetch(self, conversation_id: str) -> FetchResult:
        row = await self.db.fetchone("SELECT ...", conversation_id)
        if row is None:
            return ConversationNotFound(kind="not_found", conversation_id=conversation_id)
        foreign = DbConversation.model_validate(row)
        return ConversationFound(kind="found", conversation=foreign.to_domain())
```
"""
