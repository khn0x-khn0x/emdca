"""
THE INTERFACE ADAPTER (Router)

Role: The HTTP Entrypoint for a specific Context.
Mandate: Mandate VII (Translation).
Pattern: spec/patterns/07-acl-translation.md

Constraint:
- Receive (Contract) -> Delegate (Service) -> Return (Contract/Result).
- No Business Logic.

Example Implementation:
```python
from fastapi import APIRouter

router = APIRouter()
```
"""
