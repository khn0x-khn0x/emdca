"""
THE INTERNAL TRUTH (Entity / Aggregate)

Role: Defines the core business concepts and their valid states.
Mandate: Mandate II (State) & I (Construction).
Pattern: ref/patterns/02-state-sum-types.md

Constraint:
- All models MUST have model_config = {"frozen": True}.
- Use Sum Types (Union) for states with different data.
- Use Smart Enums for states with behavior but same data.
- State transitions are methods on the source state.
- Pure Properties (no I/O).

Example Implementation:
```python
from typing import Literal, Annotated
from pydantic import BaseModel, Field

class ConversationKind(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"

class Active(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[ConversationKind.ACTIVE]
    id: ConversationId

    def archive(self, reason: ArchiveReason) -> "Archived":
        return Archived(kind=ConversationKind.ARCHIVED, id=self.id, reason=reason)

class Archived(BaseModel):
    model_config = {"frozen": True}
    kind: Literal[ConversationKind.ARCHIVED]
    id: ConversationId
    reason: ArchiveReason

type Conversation = Annotated[Active | Archived, Field(discriminator='kind')]
```
"""
