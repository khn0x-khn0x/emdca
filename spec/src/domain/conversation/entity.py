"""
THE INTERNAL TRUTH (Entity / Aggregate)

Role: Defines the core business concepts and their valid states.
Mandate: Mandate II (State) & I (Construction).
Pattern: spec/patterns/02-state-sum-types.md

Constraint:
- Use Sum Types (Union) for states with different data.
- Use Smart Enums for states with behavior but same data.
- Pure Properties (no I/O).

Example Implementation:
```python
from typing import Literal, Annotated
from pydantic import BaseModel, Field

type Conversation = Annotated[Active | Archived, Field(discriminator='kind')]
```
"""
