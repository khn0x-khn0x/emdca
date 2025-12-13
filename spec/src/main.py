"""
THE COMPOSITION ROOT (Launcher)

Role: The Big Bang. Configures and starts the application.
Mandate: Mandate V (Config) & VIII (Coordination).
Structure: spec/structure.md

Flow:
1. Load Env (Foreign) -> Config (Truth).
2. Wire Infrastructure (Adapters).
3. Build Interface (create_api).
4. Run (uvicorn).

Example Implementation:
```python
import uvicorn
import os
from api.app import create_api
from domain.system.env import EnvVars

def main():
    raw = os.environ
    config = EnvVars.model_validate(raw).to_domain()
    app = create_api(config, ...)
    uvicorn.run(app)

if __name__ == "__main__":
    main()
```
"""
