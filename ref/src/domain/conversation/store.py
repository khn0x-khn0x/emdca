"""
THE ACTIVE CAPABILITY (Store)

Role: Encapsulates Infrastructure Clients and Logic.
Mandate: Mandate VI (Storage) & X (Infrastructure).
Pattern: ref/patterns/06-storage-foreign-reality.md
Pattern: ref/patterns/10-infrastructure-capability-as-data.md

Constraint:
- Frozen Pydantic Model.
- Holds the Client (injected).
- Executes the Logic (load/save/publish).

Example Implementation:
```python
class ConversationStore(BaseModel):
    model_config = {"frozen": True, "arbitrary_types_allowed": True}

    # Configuration
    table_name: TableName

    # Injected Capability
    db: DatabaseClient

    async def load(self, id: ConversationId) -> Conversation:
        # Use client to fetch foreign model
        row = await self.db.fetch(self.table_name, id)
        if not row:
            return ConversationNotFound(id=id)
        # Translate to Domain
        return DbConversation.model_validate(row).to_domain()
```
"""
