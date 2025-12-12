# Pattern 05: Configuration (Dependency Injection)

## The Principle
A model's behavior should be determined entirely by its inputs, enabling reasoning in isolation.

## The Mechanism
Configuration (parameters, thresholds) is passed into logic functions as immutable arguments (Context Injection). Magic numbers and global variables are strictly forbidden within domain logic.

---

## 1. The Global State (Anti-Pattern)
Relying on global variables or environment lookups makes the function impure and hard to test.

### ❌ Anti-Pattern: Hidden Dependencies
```python
import os

RSI_THRESHOLD = 70  # Magic Number

def calculate_signal(price: float) -> Signal:
    # ❌ Hidden Input: Function behavior depends on outside world
    mode = os.getenv("TRADING_MODE", "conservative")
    
    if mode == "aggressive" and price > RSI_THRESHOLD:
        return Signal.BUY
    return Signal.HOLD
```

---

## 2. Context Injection
We package all "Magic Numbers" and settings into an explicit, immutable Configuration object.

### ✅ Pattern: Explicit Config Object
```python
from pydantic import BaseModel
from typing import Literal
from enum import Enum

class Signal(str, Enum):
    BUY = "BUY"
    HOLD = "HOLD"

class StrategyConfig(BaseModel):
    model_config = {"frozen": True}
    
    rsi_threshold: int
    trading_mode: Literal["aggressive", "conservative"]
    max_risk_per_trade: float

# The Pure Function takes Config as an Argument
def calculate_signal(price: float, config: StrategyConfig) -> Signal:
    # Pure: Logic depends ONLY on inputs (price, config)
    if config.trading_mode == "aggressive" and price > config.rsi_threshold:
        return Signal.BUY
    return Signal.HOLD
```

---

## 3. Benefits of Injection
1.  **Testability:** You can test "aggressive" mode without setting environment variables.
2.  **Simulation:** You can run thousands of simulations with different configs in parallel (impossible with globals).
3.  **Clarity:** The function signature reveals *exactly* what controls the behavior.

### ✅ Pattern: Testing Multiple Realities
```python
def test_strategies():
    price = 100.0
    
    # Reality A: Conservative
    cfg_safe = StrategyConfig(rsi_threshold=80, trading_mode="conservative", ...)
    assert calculate_signal(price, cfg_safe) == Signal.HOLD
    
    # Reality B: Aggressive
    cfg_risky = StrategyConfig(rsi_threshold=60, trading_mode="aggressive", ...)
    assert calculate_signal(price, cfg_risky) == Signal.BUY
```

## 4. Cognitive Checks
*   [ ] **No os.environ:** Did I remove all `os.getenv` calls from the domain?
*   [ ] **No Global Constants:** Are `MAX_RETRIES = 3` constants moved into the Config object?
*   [ ] **Argument Explicit:** Is `config` passed as an argument, not imported?
