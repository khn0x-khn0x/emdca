---
description: "Pattern 07: Translation — Foreign Models with declarative mapping and .to_domain()."
globs: ["**/domain/**/*.py", "**/api/**/*.py"]
alwaysApply: false
---

# Pattern 07: ACL Translation

## Valid Code Structure

```python
# Foreign Model: Mirrors external API shape exactly
class CoinbaseCandle(BaseModel):
    model_config = {"frozen": True}
    
    # Field(alias=...) maps foreign names to readable internal names
    time: UnixTimestamp = Field(alias="t")
    open: Price = Field(alias="o")
    high: Price = Field(alias="h")
    
    def to_domain(self) -> Candle:
        # Pure Translation Logic
        # Structural mismatches (e.g. missing fields) cause Pydantic to CRASH before this runs.
        return Candle(
            timestamp=datetime.fromtimestamp(self.time, tz=timezone.utc),
            open=self.open,
            high=self.high,
        )

# LLM Response as Foreign Model
class GptSentimentResponse(BaseModel):
    model_config = {"frozen": True}
    
    sentiment_label: RawLabel = Field(alias="label")
    confidence_score: Probability = Field(alias="probability")
    
    def to_domain(self) -> SentimentDecision:
        # Translation Logic: Mapping string to literal
        if "pos" in self.sentiment_label.lower():
            kind = SentimentKind.POSITIVE
        elif "neg" in self.sentiment_label.lower():
            kind = SentimentKind.NEGATIVE
        else:
            # If input is unexpected, CRASH. Do not silently default.
            raise ValueError(f"Unknown sentiment: {self.sentiment_label}")
            
        return SentimentDecision(kind=kind, score=self.confidence_score)

# Raw → Foreign → Domain chain
class RawSmtpConnectError(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["connect_error"]
    message: ErrorMessage
    
    def to_foreign(self) -> SmtpConnectErrorForeign:
        return SmtpConnectErrorForeign(message=self.message)

# Usage: raw.to_foreign().to_domain()
```

## Constraints

| Required | Forbidden |
|----------|-----------|
| Foreign Model mirrors external schema exactly | Raw dict passing into domain |
| `Field(alias=...)` for name mapping | Manual field copying |
| `.to_domain()` method on Foreign Model | Standalone mapper functions |
| `raw.to_foreign().to_domain()` chain | Direct external data in domain |
| Foreign Model imports Internal Truth | Internal Truth imports Foreign Model |
| **Translation Failures -> Crash (Structure)** | **Translation Failures -> Result (Logic)** |
| **Typed Fields (Price, UnixTimestamp)** | **Primitive Fields (float, int)** |
