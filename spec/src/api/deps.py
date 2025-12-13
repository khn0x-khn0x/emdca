"""
SHARED DEPENDENCIES (Runtime)

Role: Common dependencies for Route Handlers (e.g. Auth, DB Session).
Mandate: Mandate V (Injection).
Structure: spec/structure.md

Constraint:
- Only for cross-cutting concerns.
- Specific context logic belongs in the Context Router.

Example Implementation:
```python
from fastapi import Depends

def get_current_user(...): ...
```
"""
