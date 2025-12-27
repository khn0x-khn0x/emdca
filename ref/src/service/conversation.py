"""
THE IMPERATIVE SHELL (Wiring & Provisioning)

Role: Instantiates Clients and wires them into Domain Models.
Mandate: Mandate VIII (Coordination) & X (Infrastructure).
Pattern: ref/patterns/00-master-architecture.md

Constraint:
- Regular Python Classes (or just functions).
- Dependencies injected via `__init__`.
- Creates Clients (NATS, DB).
- Does NOT contain business logic.

Example Implementation:
```python
class ConversationService:
    def __init__(self, config: AppConfig):
        self.config = config

    def create_runtime(self) -> ConversationRuntime:
        # 1. Create Clients
        db = DatabaseClient(self.config.db_url)

        # 2. Create Active Store
        store = ConversationStore(
            table_name=self.config.table_name,
            db=db
        )

        # 3. Create Active Runtime
        return ConversationRuntime(store=store)
```
"""
