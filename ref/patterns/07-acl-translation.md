# Pattern 07: Translation (The Anti-Corruption Layer)

## The Principle
The outside world speaks a chaotic language; the Domain speaks a strict language. We must explicitly model both the **Foreign Reality** (external systems) and the **Internal Truth** (business concepts). Translation is the act of naturalizing the foreign into the internal.

## The Mechanism
**Foreign Models** are frozen Pydantic models that mirror external schemas using declarative mapping. They live in the Domain (`domain/trade/coinbase.py`) because knowing the external shape is domain knowledge. They own the method `.to_domain()` to convert themselves into the Internal Truth.

---

## 1. The Raw Data Infection (Anti-Pattern)
Allowing external data structures (JSON dicts, API payloads) to permeate business logic creates a dependency on external naming conventions.

### ❌ Anti-Pattern: Dict Passing
```python
def calculate_tax(order_data: dict):
    return order_data['price'] * 0.2  # ❌ Breaks if API changes 'price' to 'unit_amount'
```

---

## 2. The Foreign Model (Reality)
We model the external system's reality explicitly. This is a precise definition of the foreign schema. We use Pydantic's aliasing to handle the friction declaratively.

### ✅ Pattern: Declarative Mapping (REST API)
```python
from pydantic import BaseModel, Field

class CoinbaseCandle(BaseModel):
    """Foreign Model: Coinbase API response shape."""
    model_config = {"frozen": True}
    
    # Field(alias=...) maps foreign reality to readable internal names
    time: int = Field(alias="t")
    open: float = Field(alias="o")
    high: float = Field(alias="h")
    low: float = Field(alias="l")
    close: float = Field(alias="c")
    volume: float = Field(alias="v")
```

### ✅ Pattern: Declarative Mapping (LLM API)
The LLM is just another foreign system. We model its output as a Foreign Model.

```python
from typing import Literal

class GptSentimentResponse(BaseModel):
    """Foreign Model: LLM response shape."""
    model_config = {"frozen": True}
    
    sentiment_label: str = Field(alias="label") 
    confidence_score: float = Field(alias="probability")

    def to_domain(self) -> "SentimentDecision":
        kind = "positive" if "pos" in self.sentiment_label.lower() else "negative"
        return SentimentDecision(kind=kind, score=self.confidence_score)
```

---

## 3. Declarative Translation (Self-Naturalization)
The Foreign Model knows how to naturalize itself into the Internal Truth. Translation logic is co-located with the schema definition.

### ✅ Pattern: The `.to_domain()` Method
```python
from datetime import datetime, timezone

# Internal Truth
class SentimentDecision(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["positive", "negative"]
    score: float


class CoinbaseCandle(BaseModel):
    """Foreign Model with translation."""
    model_config = {"frozen": True}
    
    time: int = Field(alias="t")
    # ... other fields ...

    def to_domain(self) -> Candle:
        return Candle(
            timestamp=datetime.fromtimestamp(self.time, tz=timezone.utc),
            open=Price(self.open),
            high=Price(self.high),
            low=Price(self.low),
            close=Price(self.close),
            volume=Volume(self.volume),
        )
```

### 💡 The Inverse: Intent Outcome Mapping

The `.to_domain()` pattern handles **inbound** translation (Foreign → Internal).

For **outbound** translation (Execution Result → Domain Result), the same principle applies but lives on the **Intent**:

```python
class PublishIntent(BaseModel):
    """Intent owns outbound translation."""
    model_config = {"frozen": True}
    
    stream: str
    payload: bytes
    
    def on_success(self, ack: NatsAck) -> EventPublished:
        """Outbound translation: Foreign Result → Internal Truth."""
        return EventPublished(sequence=ack.seq, stream=self.stream)
```

---

## 4. The Border (Where Translation Happens)
The Shell receives data, validates against the Foreign Model, and immediately converts to Domain.

### ✅ Pattern: Validate then Naturalize
```python
# api/market.py (The Border—composition root equivalent)
@router.post("/candles")
def ingest_candles(payload: list[CandleRequest]):
    # 1. Reality Check (FastAPI validates automatically)
    # 2. Naturalize
    domain_candles = [fc.to_domain() for fc in payload]
    # 3. Pass Truth to Logic
    market_strategy.analyze(domain_candles)
```

---

## Cognitive Checks
- [ ] **Frozen:** Does every model have `model_config = {"frozen": True}`?
- [ ] **Co-location:** Does the Foreign Model live in the same Context as the Domain Model?
- [ ] **Declarative Mapping:** Do I use `Field(alias=...)` instead of manual assignment?
- [ ] **One-Way Dependency:** Does Foreign Model import Internal Truth, never the reverse?
