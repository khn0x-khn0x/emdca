# Pattern 07: Translation (The Anti-Corruption Layer)

## The Principle
The outside world speaks a chaotic language; the Domain speaks a strict language. We must explicitly model both the **Foreign Reality** (external systems) and the **Internal Truth** (business concepts). Translation is the act of naturalizing the foreign into the internal.

## The Mechanism
**Foreign Models** are Domain Objects that mirror external schemas using declarative mapping. They live in the Domain (`domain/trade/coinbase.py`) because knowing the external shape is domain knowledge. They own the method `.to_domain()` to convert themselves into the Internal Truth.

---

## 1. The Raw Data Infection (Anti-Pattern)
Allowing external data structures (JSON dicts, API payloads) to permeate business logic creates a dependency on external naming conventions.

### ❌ Anti-Pattern: Dict Passing
```python
# BAD: Logic depends on the structure of the API Payload
def calculate_tax(order_data: dict):
    # What if the API changes 'price' to 'unit_amount'?
    # The domain logic breaks.
    return order_data['price'] * 0.2
```

---

## 2. The Foreign Model (Reality)
We model the external system's reality explicitly. This is not a "dumb DTO"; it is a precise definition of the foreign schema. We use Pydantic's aliasing to handle the friction declaratively.

### ✅ Pattern: Declarative Mapping
```python
from pydantic import BaseModel, Field

# domain/market/coinbase.py
class CoinbaseCandle(BaseModel):
    model_config = {"frozen": True}
    
    # We use Field(alias=...) to map the foreign reality ("o")
    # to our readable internal name ("open").
    time: int = Field(alias="t")
    open: float = Field(alias="o")
    high: float = Field(alias="h")
    low: float = Field(alias="l")
    close: float = Field(alias="c")
    volume: float = Field(alias="v")
```

---

## 3. Declarative Translation (Self-Naturalization)
The Foreign Model knows how to naturalize itself into the Internal Truth. The translation logic is co-located with the schema definition, keeping the knowledge self-contained.

### ✅ Pattern: The `.to_domain()` Method
```python
from datetime import datetime, timezone
from domain.market.model import Candle, Price, Volume

class CoinbaseCandle(BaseModel):
    # ... fields ...

    def to_domain(self) -> Candle:
        # Pure Transformation Logic
        return Candle(
            timestamp=datetime.fromtimestamp(self.time, tz=timezone.utc),
            open=Price(self.open),
            high=Price(self.high),
            low=Price(self.low),
            close=Price(self.close),
            volume=Volume(self.volume)
        )
```

---

## 💡 Spotlight: The LLM as a Foreign Reality
The LLM is just another foreign system with a specific schema. We model its output as a Foreign Model that translates to our Domain Decision.

```python
from typing import Literal
from pydantic import BaseModel

# Internal Truth
class SentimentDecision(BaseModel):
    kind: Literal["positive", "negative"]
    score: float

# Foreign Reality (The LLM's Schema)
class GptSentimentResponse(BaseModel):
    # The LLM might return weird keys or structures
    sentiment_label: str = Field(alias="label") 
    confidence_score: float = Field(alias="probability")

    def to_domain(self) -> SentimentDecision:
        # Normalize the foreign labels
        kind = "positive" if "pos" in self.sentiment_label.lower() else "negative"
        return SentimentDecision(kind=kind, score=self.confidence_score)
```

---

## 4. The Border (Where Translation Happens)
The Shell receives the data, validates it against the Foreign Model (Reality check), and then immediately converts it to Domain (Truth).

### ✅ Pattern: Validate then Naturalize
```python
# api/routes.py (The Border)

@router.post("/candles")
def ingest_candles(payload: list[dict]):
    # 1. Reality Check (Validate against Foreign Schema)
    foreign_candles = [CoinbaseCandle.model_validate(p) for p in payload]
    
    # 2. Naturalize (Convert to Truth)
    domain_candles = [fc.to_domain() for fc in foreign_candles]
    
    # 3. Pass Truth to Logic
    market_strategy.analyze(domain_candles)
```

## 5. Cognitive Checks
*   [ ] **Co-location:** Does the Foreign Model live in the same Context as the Domain Model (e.g., `domain/trade/coinbase.py`)?
*   [ ] **Declarative Mapping:** Do I use `Field(alias=...)` instead of manual assignment?
*   [ ] **One-Way Street:** Does the Foreign Model depend on the Domain, but the Domain Core never imports the Foreign Model?