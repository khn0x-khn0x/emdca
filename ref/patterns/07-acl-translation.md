# Pattern 07: Translation (ACL / Foreign Models)

## The Principle
The system interacts with many "Foreign Realities" (Database, External APIs, User Input). We never allow these foreign shapes to leak into our Domain. We use an **Anti-Corruption Layer (ACL)** pattern implemented via **Foreign Models**.

## The Mechanism
1.  **Foreign Models:** Pydantic models that mirror the external schema *exactly*.
2.  **Mapping:** Fields use `Field(alias=...)` to map foreign names to internal names.
3.  **Translation:** Foreign Models own a `.to_domain()` method that constructs the "Internal Truth" (Domain Model).

---

## 1. The Dict Passing (Anti-Pattern)
Passing raw dictionaries or unstructured data deeper than the entry point couples the core to the edge.

### ❌ Anti-Pattern: Raw Data
```python
def process_webhook(payload: dict):
    if payload.get("status") == "ok":  # ❌ Coupling to string literal
        pass
```

---

## 2. The Foreign Model
We model the incoming data exactly as it is, but with strong types.

### ✅ Pattern: Declarative Mapping
```python
class CoinbaseCandle(BaseModel):
    """Mirrors the Coinbase API response."""
    model_config = {"frozen": True}
    
    # Field(alias=...) maps foreign names to readable internal names
    time: UnixTimestamp = Field(alias="t")
    open: Price = Field(alias="o")
    high: Price = Field(alias="h")
    
    def to_domain(self) -> Candle:
        return Candle(
            timestamp=datetime.fromtimestamp(self.time, tz=timezone.utc),
            open=self.open,
            high=self.high,
        )
```

---

## 3. The Translation Chain
Data flows in one direction: `Raw -> Foreign -> Domain`.

### ✅ Pattern: The Chain
```python
# 1. Parse Raw JSON into Foreign Model
# If JSON is missing fields, Pydantic raises ValidationError (Crash). Correct.
foreign = CoinbaseCandle.model_validate_json(raw_json)

# 2. Translate to Domain
candle = foreign.to_domain()
```

---

## 4. LLM Responses
LLM outputs are chaotic "Foreign Reality." We parse them into strict Foreign Models before trusting them.

### ✅ Pattern: LLM Translation
```python
class GptSentimentResponse(BaseModel):
    model_config = {"frozen": True}
    
    sentiment_label: RawLabel = Field(alias="label")
    confidence_score: Probability = Field(alias="probability")
    
    def to_domain(self) -> SentimentDecision:
        if "pos" in self.sentiment_label.lower():
            return SentimentDecision(kind=SentimentKind.POSITIVE, score=self.confidence_score)
        if "neg" in self.sentiment_label.lower():
            return SentimentDecision(kind=SentimentKind.NEGATIVE, score=self.confidence_score)
            
        # Structural Violation: The AI gave us garbage. Crash.
        raise ValueError(f"AI returned invalid label: {self.sentiment_label}")
```

---

## Cognitive Checks
- [ ] **Exact Mirror:** Does the Foreign Model match the external schema 1:1?
- [ ] **Aliases:** Are `Field(alias=...)` used for renaming, not manual code?
- [ ] **One-Way Street:** Does Foreign import Domain (allowed), but Domain never imports Foreign?
- [ ] **Method Location:** Is `.to_domain()` defined on the Foreign Model?
- [ ] **No Silencing:** Does unknown data cause a Crash/Exception?
- [ ] **Typed Fields:** Am I using `Price`, `Probability` instead of `float`?
