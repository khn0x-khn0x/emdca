"""
THE INTERFACE BUILDER (App Definition)

Role: Constructs the FastAPI application instance.
Mandate: Mandate V (Configuration - Usage).
Structure: spec/structure.md

Constraint:
- Returns `FastAPI` object.
- Does not run the server.
- Wires dependencies via `dependency_overrides` or closure injection.

Example Implementation:
```python
from fastapi import FastAPI

def create_api(config, db) -> FastAPI:
    app = FastAPI()
    # ... wiring ...
    return app
```
"""
