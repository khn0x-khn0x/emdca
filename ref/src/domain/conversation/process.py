"""
THE PURE LOGIC (Workflow / State Transitions)

Role: Pure methods on frozen models that calculate next state or decision.
Mandate: Mandate IX (Workflow) & IV (Intent).
Pattern: ref/patterns/09-workflow-state-machine.md
Pattern: ref/patterns/04-execution-intent.md

Constraint:
- State transitions are methods on the SOURCE state model.
- Decision methods return Intent or NoOp.
- NO I/O. NO AWAIT. Pure computation only.

Example Implementation:
```python
from pydantic import BaseModel
from typing import Literal

class Active(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["active"]
    conversation_id: str

    def archive(self, reason: str) -> "Archived":
        \"\"\"State transition: Active -> Archived\"\"\"
        return Archived(
            kind="archived",
            conversation_id=self.conversation_id,
            reason=reason,
        )

    def decide_response(self, message: "Message") -> "RespondIntent | NoOp":
        \"\"\"Decision method: returns Intent or NoOp\"\"\"
        if message.requires_response:
            return RespondIntent(
                conversation_id=self.conversation_id,
                content=self._generate_content(message),
            )
        return NoOp(kind="no_op", reason="No response required")
```
"""
