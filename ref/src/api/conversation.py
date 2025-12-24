"""
THE ROUTER (Interface)

Role: The HTTP Entrypoint for a specific Context.
Mandate: Mandate VII (Translation).
Pattern: ref/patterns/07-acl-translation.md

Constraint:
- Receive (Foreign Model) -> Translate (.to_domain()) -> Delegate (Orchestrator) -> Return.
- No Business Logic.
- Uses frozen Pydantic models for request/response.

Example Implementation:
```python
from fastapi import APIRouter, Request
from domain.conversation.api import CreateMessageRequest

router = APIRouter()

@router.post("/messages")
async def create_message(request: CreateMessageRequest, req: Request):
    # Translate foreign -> domain
    message = request.to_domain()

    # Delegate to orchestrator (accessed from app state)
    orchestrator = req.app.state.orchestrator
    result = await orchestrator.process_message(message.id)

    # Return (match on result Sum Type for response)
    match result:
        case MessageProcessed():
            return {"status": "ok"}
        case MessageNotFound():
            return {"status": "not_found"}, 404
```
"""
