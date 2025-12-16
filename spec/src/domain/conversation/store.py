"""
THE FOREIGN REALITY (Database Schema)

Role: Defines the shape of the stored data (Foreign Model).
Mandate: Mandate VI (Storage) & VII (Translation).
Pattern: spec/patterns/06-storage-foreign-reality.md

Constraint:
- Represents the SQL Table or Document structure.
- Owns .to_domain() to convert to Internal Truth.
- No behavioral logic (just data and translation).

Example Implementation:
```python
from pydantic import BaseModel

class DbConversation(BaseModel):
    id: str
    status: str

    def to_domain(self) -> Conversation:
        # ... translation logic ...
        pass
```
"""
