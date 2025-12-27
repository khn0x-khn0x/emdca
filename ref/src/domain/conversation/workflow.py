"""
THE STATE MACHINE (Workflow & Runtime)

Role: Defines the business process graph and the runtime driver.
Mandate: Mandate IX (Workflow) & VIII (Coordination).
Pattern: ref/patterns/09-workflow-state-machine.md
Pattern: ref/patterns/08-orchestrator-loop.md

Constraint:
- Smart Enums define the graph.
- Sum Types define the nodes.
- Runtime is an Active Domain Model holding the Store.

Example Implementation:
```python
class ConversationKind(StrEnum):
    ACTIVE = "active"
    CLOSED = "closed"

class ActiveConversation(BaseModel):
    kind: Literal[ConversationKind.ACTIVE]
    def close(self) -> tuple[ClosedConversation, Intent]: ...

# The Active Runtime
class ConversationRuntime(BaseModel):
    model_config = {"frozen": True, "arbitrary_types_allowed": True}

    store: ConversationStore

    async def run(self, id: ConversationId, event: Event) -> Result:
        state = await self.store.load(id)
        new_state, intent = state.handle(event)
        await self.store.save(new_state)
        # execute intent...
```
"""
