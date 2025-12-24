"""
THE INTERFACE BUILDER (App Factory)

Role: Constructs the FastAPI application instance.
Mandate: Mandate V (Configuration - Usage).
Structure: ref/structure.md

Constraint:
- Factory is a method on a frozen Pydantic model.
- Returns `FastAPI` object.
- Does not run the server.
- Receives pre-wired orchestrators (dependencies already injected as fields).

Example Implementation:
```python
from pydantic import BaseModel
from fastapi import FastAPI
from service.conversation import ConversationOrchestrator

class AppFactory(BaseModel):
    model_config = {"frozen": True}
    config: AppConfig
    orchestrator: ConversationOrchestrator

    def create(self) -> FastAPI:
        app = FastAPI()

        # Orchestrator already has its dependencies wired as fields
        app.state.orchestrator = self.orchestrator

        return app
```
"""
