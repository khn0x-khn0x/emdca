"""
THE ORCHESTRATOR (Service Layer)

Role: Frozen Pydantic model that coordinates I/O and Logic.
Mandate: Mandate VIII (Coordination).
Pattern: ref/patterns/08-orchestrator-loop.md
Pattern: ref/patterns/04-execution-intent.md

Constraint:
- Orchestrator is a frozen Pydantic model with dependencies as FIELDS.
- Flow: Fetch -> Translate -> Decide -> Execute -> Persist.
- No Business Rules (decision logic belongs on domain models).
- No Result Construction (Intents own on_success/on_failure).
- Uses match/case to dispatch on Sum Types.

Example Implementation:
```python
from pydantic import BaseModel
from domain.conversation.store import ConversationStore, ConversationFound, ConversationNotFound
from domain.conversation.entity import Active
from domain.conversation.process import RespondIntent, NoOp

class ConversationOrchestrator(BaseModel):
    model_config = {"frozen": True}
    store: ConversationStore      # Dependency as field
    bus: NatsClient               # Dependency as field

    async def process_message(self, msg_id: str) -> ProcessResult:
        # 1. Fetch (via Store, returns Sum Type)
        fetch_result = await self.store.fetch(msg_id)

        match fetch_result:
            case ConversationNotFound():
                return MessageNotFound(kind="not_found", msg_id=msg_id)
            case ConversationFound(conversation=conv):
                pass

        # 2. Decide (pure method on domain model)
        match conv:
            case Active() as active:
                outcome = active.decide_response(message)
            case _:
                outcome = NoOp(kind="no_op", reason="Conversation not active")

        # 3. Execute (dispatch on Intent)
        match outcome:
            case NoOp():
                pass
            case RespondIntent() as intent:
                result = await self.bus.publish(intent)
                # Intent owns interpretation via on_success/on_failure

        # 4. Persist
        await self.store.save(conv)

        return MessageProcessed(kind="processed", msg_id=msg_id)
```
"""
