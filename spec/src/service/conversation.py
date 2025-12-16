"""
THE ORCHESTRATOR (Service Layer)

Role: The "Roadie". Connects the pipes between IO and Logic.
Mandate: Mandate VIII (Coordination).
Pattern: spec/patterns/08-orchestrator-loop.md
Pattern: spec/patterns/04-execution-intent.md (Generic Executor)

Constraint:
- Fetch -> Translate -> Decide -> Dispatch -> Execute -> Persist.
- No Business Rules (if statements on domain data).
- No Result Construction (Intents own on_success/on_failure).
- Uses generic executor for Intent fulfillment.
- Manages Transactions.

Example Implementation:
```python
async def process_message(db, bus, msg_id):
    # 1. Fetch (IO)
    row = await db.fetchone(...)

    # 2. Translate (Foreign -> Domain)
    message = DbMessage.model_validate(row).to_domain()

    # 3. Decide (Pure)
    new_state, outcome = step_conversation(state, message)

    # 4. Dispatch + Execute (Shell)
    match outcome:
        case NoOp():
            pass
        case PublishIntent() as intent:
            result = await execute(
                operation=lambda: bus.publish(...),
                catch_names=intent.catch_exceptions,
                on_success=intent.on_success,
                on_failure=intent.on_failure,
            )

    # 5. Persist (IO)
    await db.execute(...)
```
"""
