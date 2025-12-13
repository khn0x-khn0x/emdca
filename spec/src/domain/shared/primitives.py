"""
THE UBIQUITOUS LANGUAGE (Primitives)

Role: Universal Value Objects used across multiple contexts.
Mandate: Mandate I (Construction) - "Primitive Obsession is Forbidden".
Pattern: spec/patterns/01-factory-construction.md

Constraint:
- Pure Data + Validation Logic.
- No side effects.

Example Implementation:
```python
from typing import Annotated
from pydantic import AfterValidator

type Email = Annotated[str, AfterValidator(validate_email)]
```
"""
