"""
THE FOREIGN REALITY (Vendor Schema)

Role: Defines the schema of external systems (e.g. OpenAI Response, Stripe Object).
Mandate: Mandate VII (Translation) & X (Infra as Data).
Pattern: ref/patterns/07-acl-translation.md
Pattern: ref/patterns/10-infrastructure-capability-as-data.md

Constraint:
- Frozen Pydantic models that mirror external API exactly (using aliases).
- Owns .to_domain() to convert to Internal Truth.
- Infrastructure returns these as Sum Types (success variant contains vendor model).

Example Implementation:
```python
from pydantic import BaseModel, Field
from typing import Literal

# Raw infrastructure result (what the executor captures)
class OpenAiSuccess(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["success"]
    payload: dict  # Raw JSON from API

class OpenAiFailure(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["failure"]
    error: str
    status_code: int

type OpenAiRawResult = OpenAiSuccess | OpenAiFailure

# Foreign Model (parsed from payload)
class OpenAiCompletion(BaseModel):
    model_config = {"frozen": True}
    id: str = Field(alias="id")
    content: str = Field(alias="choices[0].message.content")

    def to_domain(self) -> "AssistantMessage":
        return AssistantMessage(content=self.content)
```
"""
