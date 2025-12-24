---
description: "Pattern 07: Translation — Foreign Models with declarative mapping and .to_domain()."
globs: ["**/vendor.py", "**/foreign.py", "**/api/**/*.py", "**/domain/**/*.py"]
alwaysApply: false
---

# Pattern 07: ACL Translation

## Valid Code Structure

```python
# Foreign Model: Mirrors external API shape exactly
class CoinbaseCandle(BaseModel):
    model_config = {"frozen": True}
    
    # Field(alias=...) maps foreign names to readable internal names
    time: int = Field(alias="t")
    open: float = Field(alias="o")
    high: float = Field(alias="h")
    low: float = Field(alias="l")
    close: float = Field(alias="c")
    volume: float = Field(alias="v")
    
    def to_domain(self) -> Candle:
        return Candle(
            timestamp=datetime.fromtimestamp(self.time, tz=timezone.utc),
            open=Price(self.open),
            high=Price(self.high),
            low=Price(self.low),
            close=Price(self.close),
            volume=Volume(self.volume),
        )

# LLM Response as Foreign Model
class GptSentimentResponse(BaseModel):
    model_config = {"frozen": True}
    
    sentiment_label: str = Field(alias="label")
    confidence_score: float = Field(alias="probability")
    
    def to_domain(self) -> SentimentDecision:
        kind = "positive" if "pos" in self.sentiment_label.lower() else "negative"
        return SentimentDecision(kind=kind, score=self.confidence_score)

# Raw → Foreign → Domain chain
class RawSmtpConnectError(BaseModel):
    model_config = {"frozen": True}
    kind: Literal["connect_error"]
    message: str
    
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
| Frozen models | Mutable translation objects |

