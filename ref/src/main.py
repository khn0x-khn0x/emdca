"""
THE COMPOSITION ROOT (Launcher)

Role: The Big Bang. Configures and starts the application.
Mandate: Mandate V (Config) & VIII (Coordination) & X (Infrastructure).
Pattern: ref/patterns/05-config-injection.md
Pattern: ref/patterns/10-infrastructure-capability-as-data.md

Flow:
1. Load Env (Foreign) -> Config (Domain) via Sum Type result.
2. Build Infrastructure clients (raw I/O, returns Sum Types).
3. Wire Orchestrators with dependencies as fields.
4. Build Interface via AppFactory model.
5. Run (uvicorn).

Note: This is the ONE place where standalone wiring code exists.

Example Implementation:
```python
import sys
import asyncio
import uvicorn
import os
from api.app import AppFactory
from api.deps import Clock
from domain.system.env import EnvVars
from service.conversation import ConversationConnector, Connected, ConnectionFailed
from service.conversation import ConversationOrchestrator, ConversationStore

async def main():
    # 1. Translate Config (Sum Type result)
    raw = os.environ
    config_result = EnvVars.model_validate(raw).to_config()

    match config_result:
        case ConfigInvalid(errors=e):
            sys.exit(f"Config invalid: {e}")
        case ConfigValid(config=config):
            pass

    # 2. Setup Infrastructure (Executor returns Sum Type)
    connector = ConversationConnector(url=config.nats_url)
    connect_result = await connector.connect()

    match connect_result:
        case ConnectionFailed(error=e):
            sys.exit(f"Infrastructure setup failed: {e}")
        case Connected(client=nc):
            pass

    # 3. Wire Orchestrators (dependencies as fields)
    clock = Clock()
    store = ConversationStore(db=db)
    orchestrator = ConversationOrchestrator(store=store, bus=nc, clock=clock)

    # 4. Build Interface via AppFactory
    factory = AppFactory(config=config, orchestrator=orchestrator)
    app = factory.create()

    # 5. Run
    uvicorn.run(app)

if __name__ == "__main__":
    asyncio.run(main())
```
"""
