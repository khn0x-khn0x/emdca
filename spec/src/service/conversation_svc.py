"""
THE ORCHESTRATOR (Service Layer)

Role: The "Roadie". Connects the pipes between IO and Logic.
Mandate: Mandate VIII (Coordination).
Pattern: spec/patterns/08-orchestrator-loop.md

Constraint:
- Fetch -> Logic -> Act -> Save.
- No Business Rules (if statements).
- Manages Transactions.

Example Implementation:
```python
async def process_message(repo, msg_id):
    # Fetch -> Logic -> Save
    pass
```
"""
