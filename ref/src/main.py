"""
THE COMPOSITION ROOT (Launcher)

Role: The Big Bang. Configures and starts the application.
Mandate: Mandate V (Config).
Pattern: ref/patterns/05-config-injection.md

Flow:
1. Load Config (Crash on Failure).
2. Wire Service (Create Runtime).
3. Launch Interface (App).

Example Implementation:
```python
import uvicorn
from domain.system.config import AppConfig
from service.conversation import ConversationService
from api.app import create_api

def main():
    # 1. Load Config
    config = AppConfig()

    # 2. Wire Service (Provisioning)
    service = ConversationService(config)
    runtime = service.create_runtime()

    # 3. Launch Interface
    app = create_api(runtime=runtime)
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
```
"""
