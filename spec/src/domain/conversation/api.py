"""
THE FOREIGN REALITY (API Contract)

Role: Defines the schema of the HTTP Interface (Requests/Responses).
Mandate: Mandate VII (Translation).
Pattern: spec/patterns/07-acl-translation.md

Constraint:
- Defines the "Public" language.
- Owns .to_domain() to naturalize input into Internal Truth.

Example Implementation:
```python
from pydantic import BaseModel

class CreateMessageRequest(BaseModel): ...
```
"""
