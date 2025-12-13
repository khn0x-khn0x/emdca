"""
THE PURE LOGIC (Process / Factory / Workflow)

Role: Pure functions that calculate the next state or intent.
Mandate: Mandate IX (Workflow) & IV (Intent).
Pattern: spec/patterns/09-workflow-state-machine.md
Pattern: spec/patterns/04-execution-intent.md

Constraint:
- Input: Domain Models / Foreign Models.
- Output: New State / Intent.
- NO I/O. NO AWAIT.

Example Implementation:
```python
def step_conversation(state: Conversation, input: Message) -> tuple[Conversation, Intent]:
    ...
```
"""
