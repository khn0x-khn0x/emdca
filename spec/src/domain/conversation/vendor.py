"""
THE FOREIGN REALITY (Vendor Schema / Adapter Model)

Role: Defines the schema of external systems (e.g. OpenAI Response, Stripe Object).
Mandate: Mandate VII (Translation) & X (Infra as Data).
Pattern: spec/patterns/07-acl-translation.md
Pattern: spec/patterns/10-infrastructure-capability-as-data.md

Constraint:
- Mirrors the external API exactly (using aliases).
- Owns .to_domain() to convert to Internal Truth.

Example Implementation:
```python
from pydantic import BaseModel, Field

class OpenAiCompletion(BaseModel): ...
```
"""
