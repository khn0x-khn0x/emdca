# Pattern 10: Infrastructure (Capability as Data)

## The Principle
Infrastructure has a shape. In EMDCA, we model that shape as an **Active Domain Model** (Capability).
We do not define Interfaces (`IEventBus`); we define **Configured Models** (`EventStore`) that hold the actual client and know how to use it.

## The Mechanism
1.  **Capability Model:** A Pydantic Model that wraps the Infrastructure Client.
2.  **Injection:** The Client is passed to the Model at construction.
3.  **Active Execution:** The Model uses the Client to perform work.

---

## ❌ Anti-Pattern: Interfaces (Ports & Adapters)
Defining abstract interfaces for the Service to implement forces the Domain to be passive and ignorant.

```python
# ❌ Abstract Interface
class IEventBus(Protocol):
    def publish(self, event): ...

# ❌ Service Implementation
class NatsBus(IEventBus): ...
```

---

## ❌ Anti-Pattern: Anemic Model
Separating Config (Domain) from Execution (Service) creates fragmentation.

```python
# ❌ Passive Config
class EventConfig(BaseModel):
    topic: str

# ❌ Active Service
class EventService:
    def publish(self, config, event): ...
```

---

## ✅ Pattern: Active Capability Model
The `EventStore` *is* the store. It holds the connection. It does the work.

```python
class EventStore(BaseModel):
    """
    Active Domain Model.
    Holds the Tool (Client) and the Instruction (Logic).
    """
    model_config = {"frozen": True, "arbitrary_types_allowed": True}
    
    # Configuration (Data)
    topic_name: TopicName
    
    # Capability (Tool)
    client: NatsClient
    
    async def publish(self, event: DomainEvent) -> EventResult:
        # 1. Direct Execution
        # No manual mapping logic. Pass data to client.
        try:
            await self.client.publish(
                self.topic_name,
                event.model_dump_json()
            )
            return EventStored(kind=EventResultKind.STORED)
        except NatsError:
            return EventFailed(kind=EventResultKind.FAILED)
```

---

## Cognitive Checks

- [ ] **Model is Active:** Does `EventStore` have methods that *do* things?
- [ ] **Client Injected:** Does it hold `client` as a field?
- [ ] **No Interfaces:** Did I avoid `class IStore(Protocol)`?
- [ ] **No Mappers:** Do I use direct construction/casting?
- [ ] **Real Types:** Am I using `TopicName`, not `str`?
