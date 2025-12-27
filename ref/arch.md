## **Architecture Specification: Explicitly Modeled Data-Centric Architecture (EMDCA)**

This document contains the non-negotiable engineering standards for the system. It is written as a strict set of directives for developers to follow without ambiguity.

**For implementation details, see the [Patterns Library](patterns/).**

---

### **I. The Construction Mandate: The Pure Factory**

**The Principle:** Validation is not a check; it is a construction process. Logic is a calculation, not an action. Therefore, the code that makes decisions must be separated from the code that executes them.

#### **MUST USE:**

* **Factory Methods on Models:** All domain logic and decision-making must live as methods on frozen Pydantic models.
* **Value Objects:** Primitive Obsession is forbidden. Use Pydantic built-ins (`EmailStr`, `PositiveInt`) over hand-rolled validators.
* **Correctness by Construction:** If data does not fit the type (e.g. negative age), the system **CRASHES** (`ValidationError`). Do not try to "handle" invalid structure.
* **Constraint by Type:** Encode rules in Types (`Field(ge=18)`), not in `if` statements.

#### **MUST NOT USE:**

* **Defensive Coding:** Never write `if` statements to check structural validity. Let the Type System do it.
* **Side Effects in Factories:** The factory must **never** perform I/O.
* **Standalone Functions:** Logic lives on Models (Domain) or in Service Classes (Shell).

→ **[Pattern 01: Factory Construction](patterns/01-factory-construction.md)**

---

### **II. The State Mandate: Sum Types Over Product Types**

**The Principle:** Software complexity grows with the number of possible states. We must minimize the state space by making invalid combinations of state unrepresentable.

#### **MUST USE:**

* **Behavioral Types (Smart Enums):** `StrEnum` defines the lifecycle graph. It is the "Brain" of the state machine.
* **Discriminated Unions (Sum Types):** Mutually exclusive realities must be modeled as Unions of distinct Types.
* **Structural Proofs:** Each variant must contain the specific data required for that reality.
* **Pure Transitions:** State transitions are methods on the source state returning the target state.
* **Explicit Context:** Pass **Values** (`timestamp: datetime`) into transitions, never **Services** (`clock: Clock`).

#### **MUST NOT USE:**

* **The God Model (Product Types):** Never use a single class with optional fields to represent conflicting states.
* **Boolean Flags for State:** Never use boolean flags to determine state. The **Type** determines the state.
* **Implicit Context:** Never access global state or injected services inside a Domain Model.

→ **[Pattern 02: State Sum Types](patterns/02-state-sum-types.md)**

---

### **III. The Control Flow Mandate: Railway Oriented Programming**

**The Principle:** Logic is a flow of data. We distinguish between **Structural Failures** (Crash) and **Business Failures** (Result).

#### **MUST USE:**

* **Railway for Logic:** Expected business failures (insufficient funds) return explicit `Success | Failure` Sum Types.
* **Crash for Structure:** Impossible inputs (negative money) crash the system.
* **Logic on Value Objects:** Value Objects own the rules (`Money.subtract`). Entities delegate.

#### **MUST NOT USE:**

* **Exceptions for Business Logic:** Never use `try/except` to handle domain rules (e.g. "User Banned").
* **Defensive Ifs in Entities:** Do not write `if amount > balance` in the Entity. Call the Value Object.
* **Implicit Returns:** Never allow a function to return `None` implicitly.

→ **[Pattern 03: Railway Control Flow](patterns/03-railway-control-flow.md)**

---

### **IV. The Execution Mandate: Intent as Contract**

**The Principle:** Deciding to do something and doing it are separate concerns. The Domain decides; the Shell executes. Infrastructure returns Sum Types; models parse.

#### **MUST USE:**

* **Intents:** The domain model returns inert, serializable specification objects (`SendEmailIntent`).
* **Logic Ownership:** The Intent defines how to interpret success/failure (`on_success`, `on_failure`).
* **Service Classes:** Executors are **Plain Python Classes** (not Models) that execute Intents.
* **Infrastructure as Sum Type:** Infrastructure captures raw results as Sum Types—never exceptions.

#### **MUST NOT USE:**

* **Service Models:** Executors must NOT inherit `BaseModel`. They are Behavior.
* **Service Injection:** Never inject a "Service" into a domain model.
* **Closures/Callbacks:** Intents must be pure data (JSON serializable).

→ **[Pattern 04: Execution Intent](patterns/04-execution-intent.md)**

---

### **V. The Configuration Mandate: Foreign Reality vs Internal Truth**

**The Principle:** Configuration is the **Schema of the Environment**. It is Domain Knowledge.

#### **MUST USE:**

* **Pydantic Settings:** Define `AppConfig(BaseSettings)` in the Domain. This is the contract.
* **Declarative Mapping:** Use `Field(alias=...)` to map OS names to Domain names.
* **Crash on Start:** If config is missing, the app crashes immediately at the Composition Root.

#### **MUST NOT USE:**

* **Magic Binding:** Never use libraries that implicitly inject config into deep code.
* **Global Variables:** Never access `os.environ` from within domain logic.
* **Railway for Config:** Missing config is not a "Result"; it is a broken system.

→ **[Pattern 05: Config Injection](patterns/05-config-injection.md)**

---

### **VI. The Storage Mandate: DB as Foreign Reality**

**The Principle:** The Domain Core must be agnostic to the mechanism of data storage. The Database is just another **Foreign Reality**.

#### **MUST USE:**

* **Foreign Models for Storage:** Define Pydantic models (`DbOrder`) that represent the exact shape of the database table.
* **Stores as Executors:** Storage is handled by **Service Classes** (Executors) that run `LoadIntents`.
* **Query Results as Sum Types:** Model results as `OrderFound | OrderNotFound`.

#### **MUST NOT USE:**

* **Repository Pattern:** No abstract repository interfaces. Use Executors.
* **Active Record:** Domain Models never call `.save()`.
* **Implied I/O:** The Domain never knows I/O is happening.

→ **[Pattern 06: Storage Foreign Reality](patterns/06-storage-foreign-reality.md)**

---

### **VII. The Translation Mandate: Foreign Reality vs. Internal Truth**

**The Principle:** The outside world speaks a chaotic language; the Domain speaks a strict language. Translation is the act of naturalizing the foreign into the internal.

#### **MUST USE:**

* **Foreign Models:** Define frozen Pydantic models that mirror external schemas exactly.
* **Self-Translation:** The Foreign Model owns the `.to_domain()` method.
* **Crash on Mismatch:** If the foreign data violates the schema, the system crashes.

#### **MUST NOT USE:**

* **Imperative Mappers:** Never write standalone functions that copy fields from A to B.
* **Silencing Errors:** Never try to "fix" bad data structure. Reject it.

→ **[Pattern 07: ACL Translation](patterns/07-acl-translation.md)**

---

### **VIII. The Coordination Mandate: The Orchestrator**

**The Principle:** A system needs a "driver" that does no thinking, only moving. It coordinates the flow of data between Stores, Domain Models, and Executors.

#### **MUST USE:**

* **Orchestrators as Service Classes:** Plain Python classes that drive the loop.
* **The Main Loop:** Load → Step → Save → Execute.
* **Dumb Piping:** The Orchestrator takes output from step N and feeds it as input to step N+1.

#### **MUST NOT USE:**

* **Orchestrators as Models:** Orchestrators are Behavior, not Data.
* **Logic in the Loop:** The Orchestrator must never contain `if` statements related to business rules.
* **Implicit Steps:** Every step must be explicit in the loop code.

→ **[Pattern 08: Orchestrator Loop](patterns/08-orchestrator-loop.md)**

---

### **IX. The Workflow Mandate: Process as State Machine**

**The Principle:** The sequence of business steps is Business Logic, not plumbing. Workflows must be modeled as State Machines in the Domain.

#### **MUST USE:**

* **Smart Enums:** `StrEnum` defines the state graph.
* **Workflow States as Sum Types:** Explicit types for each state node.
* **Transitions as Methods:** State transitions are pure functions on the source state.
* **Runtime:** A generic driver (Service Class) that manages persistence.

#### **MUST NOT USE:**

* **Procedural Orchestration:** Never write `if/else` chains in the Service layer to determine operation order.
* **Hidden Chains:** Do not chain side effects implicitly.
* **Stringly Typed IDs:** Use `WorkflowId`, `UserId`.

→ **[Pattern 09: Workflow State Machine](patterns/09-workflow-state-machine.md)**

---

### **X. The Infrastructure Mandate: Capability as Data**

**The Principle:** Infrastructure has a shape. Model it. Domain contexts define abstract capabilities they need as **Data Config**, not Interfaces.

#### **MUST USE:**

* **Capability as Data:** Domain defines `EventCapability` (Config Model).
* **Executor Binds:** Service `EventExecutor` binds Config to Technology.
* **Intents:** Domain outputs Intents; Service executes them.

#### **MUST NOT USE:**

* **Interfaces/Protocols:** Never define `IEventBus` in the Domain.
* **Active Clients in Domain:** Never import `boto3` in the Domain.

→ **[Pattern 10: Infrastructure Capability](patterns/10-infrastructure-capability-as-data.md)**
