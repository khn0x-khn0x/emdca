"""
THE COMPOSITION ROOT (Launcher)

Role: The Big Bang. Configures and starts the application.
Mandate: Mandate V (Config) & VIII (Coordination) & X (Infrastructure).
Pattern: spec/patterns/05-config-injection.md
Pattern: spec/patterns/10-infrastructure-capability-as-data.md
Pattern: spec/patterns/04-execution-intent.md (Generic Executor)

Flow:
1. Load Env (Foreign) -> Config (Truth).
2. Setup Infrastructure (via Intents + Generic Executor).
3. Build Interface (create_api).
4. Run (uvicorn).

Example Implementation:
```python
import sys
import uvicorn
import os
from api.app import create_api
from domain.system.env import EnvVars
from domain.infra.connection import ConnectIntent, ConnectionFailed

async def main():
    # 1. Translate Config
    raw = os.environ
    config = EnvVars.model_validate(raw).to_domain()

    # 2. Setup Infrastructure (Intent-Based)
    connect_intent = ConnectIntent(url=config.nats_url)
    nc = None

    async def do_connect():
        nonlocal nc
        nc = await nats.connect(connect_intent.url)
        return nc

    result = await execute(
        operation=do_connect,
        catch_names=connect_intent.catch_exceptions,
        on_success=connect_intent.on_success,
        on_failure=connect_intent.on_failure,
    )

    match result:
        case ConnectionFailed(error=e):
            sys.exit(f"Infrastructure setup failed: {e}")
        case Connected():
            pass

    # 3. Build Interface
    app = create_api(config, nc)

    # 4. Run
    uvicorn.run(app)

if __name__ == "__main__":
    asyncio.run(main())
```
"""
