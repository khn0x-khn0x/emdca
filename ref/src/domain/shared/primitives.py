"""
THE UBIQUITOUS LANGUAGE (Primitives)

Role: Universal Value Objects used across multiple contexts.
Mandate: Mandate I (Construction) - "Primitive Obsession is Forbidden".
Pattern: ref/patterns/01-factory-construction.md

Constraint:
- Use Pydantic built-in types (EmailStr, PositiveInt, HttpUrl) over hand-rolled validators.
- Use `type` ONLY for Discriminated Unions, never for Value Objects.
- Pure Data + Validation Logic. No side effects.

Example Implementation:
```python
from pydantic import BaseModel, EmailStr, PositiveInt, HttpUrl

class UserProfile(BaseModel):
    model_config = {"frozen": True}
    email: EmailStr          # Pydantic built-in, not hand-rolled
    age: PositiveInt         # Pydantic built-in
    website: HttpUrl         # Pydantic built-in

# For domain-specific IDs, use NewType or wrapper models
class ConversationId(BaseModel):
    model_config = {"frozen": True}
    value: str
```
"""
