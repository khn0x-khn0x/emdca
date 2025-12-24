## **Architecture Specification: Explicitly Modeled Data-Centric Architecture (EMDCA)**

This document contains the non-negotiable engineering standards for the system. It is written as a strict set of directives for developers to follow without ambiguity.

**For implementation details, see the [Patterns Library](patterns/).**

---

### **I. The Construction Mandate: The Pure Factory**

**The Principle:** Validation is not a check; it is a construction process. Logic is a calculation, not an action. Therefore, the code that makes decisions must be separated from the code that executes them.

#### **MUST USE:**

* **Factory Methods on Models:** All domain logic and decision-making must live as methods on frozen Pydantic models. These methods accept raw data and "parse" it into a valid Domain Type.
* **Value Objects:** Primitive Obsession is forbidden. Use Pydantic built-ins (`EmailStr`, `PositiveInt`) over hand-rolled validators.
* **Explicit Construction:** Never use default values in Domain Models. Defaults are hidden business rules. The Factory must set every field explicitly.
* **Parse, Don't Validate:** Instead of checking if data is valid, construct the success type. If invalid, return a distinct Failure Type.
* **Total Functions:** The factory must handle **every** possible input state and return a valid result object (Success or Failure). It must never crash or raise unhandled exceptions.

#### **MUST NOT USE:**

* **Side Effects in Factories:** The factory must **never** perform I/O. It must be a pure function of its inputs.
* **Standalone Functions:** All logic is methods on frozen Pydantic models.
* **Validation Methods:** Never write an `.is_valid()` method. If an object exists, it is valid by definition.

→ **[Pattern 01: Factory Construction](patterns/01-factory-construction.md)**

---

### **II. The State Mandate: Sum Types Over Product Types**

**The Principle:** Software complexity grows with the number of possible states. We must minimize the state space by making invalid combinations of state unrepresentable.

#### **MUST USE:**

* **Discriminated Unions (Sum Types):** Mutually exclusive realities must be modeled as Unions of distinct Types.
* **Structural Proofs:** Each variant must contain the specific data required for that reality.
* **Smart Enums (`StrEnum`):** Simple state machines should use Smart Enums with `@property` methods for behavior.
* **Pattern Matching:** Use `match/case` to handle the different realities.
* **Transitions as Methods:** State transitions are methods on the source state returning the target state.

#### **MUST NOT USE:**

* **The God Model (Product Types):** Never use a single class with optional fields to represent conflicting states.
* **Boolean Flags for State:** Never use boolean flags to determine state. The **Type** determines the state.
* **`| None` for Optionality:** Use Sum Types for mutually exclusive states, not `None`.

→ **[Pattern 02: State Sum Types](patterns/02-state-sum-types.md)**

---

### **III. The Control Flow Mandate: Railway Oriented Programming**

**The Principle:** Logic is a flow of data. Branching should be handled as a topology of tracks, not as a series of exceptions or jumps.

#### **MUST USE:**

* **The Railway Switch:** Logic branches must happen inside methods on models. The flow must explicitly guide data onto either a "Success Track" or a "Failure Track".
* **Explicit Fall-through:** Every logical branch must terminate in a return value. "Doing nothing" must be represented by an explicit `NoOp` type, not `None`.
* **Result Types:** Return `Success | Failure` discriminated unions.

#### **MUST NOT USE:**

* **Exceptions for Control Flow:** Never use `try/except` to handle domain logic. Exceptions are strictly for system failures.
* **Implicit Returns:** Never allow a function to return `None` implicitly. The return type must always be explicit.
* **`raise` for Domain Logic:** Models parse data into Sum Types. They don't raise.

→ **[Pattern 03: Railway Control Flow](patterns/03-railway-control-flow.md)**

---

### **IV. The Execution Mandate: Intent as Contract**

**The Principle:** Deciding to do something and doing it are separate concerns. The Domain decides; the Shell executes. Infrastructure returns Sum Types; models parse.

#### **MUST USE:**

* **Intents:** The domain model must return inert, serializable specification objects describing the side effect AND its outcome interpretation.
* **Complete Instructions:** The Intent must contain:
    1. **Execution Parameters:** All data required to perform the operation.
    2. **Success Mapping (`on_success`):** How to transform the raw result into a Domain Success type.
    3. **Failure Mapping (`on_failure`):** How to transform the failure into a Domain Failure type.
    4. **Handled Failures:** Which failures the domain handles gracefully vs. treats as unhandled.
* **Infrastructure as Sum Type:** Infrastructure captures raw results as Sum Types—never exceptions.
* **Foreign Model Chain:** `raw.to_foreign().to_domain()` for parsing infrastructure results.

#### **MUST NOT USE:**

* **`try/except` in Domain:** Models parse Sum Types. The Shell never catches exceptions to build domain Results.
* **Service Injection:** Never inject a "Service" or "Client" into a domain model.
* **Closures/Callbacks:** Intents must be pure data (JSON serializable), not functions.

→ **[Pattern 04: Execution Intent](patterns/04-execution-intent.md)**

---

### **V. The Configuration Mandate: Foreign Reality vs Internal Truth**

**The Principle:** Configuration comes from the chaotic outside world (Environment Variables). It is a **Foreign Reality** that must be explicitly translated into a structured **Internal Truth** (Domain Config) before entering the system.

#### **MUST USE:**

* **Foreign Models for Env:** Explicitly model the raw environment (`EnvVars`) using `Field(alias=...)` to handle OS naming conventions.
* **Explicit Translation:** Convert the raw environment model into a pure Domain Config via `.to_domain()`.
* **Config Result:** Model config loading as `ConfigLoaded | ConfigInvalid` Sum Type.
* **No Defaults:** All fields required. Defaults hide configuration requirements.

#### **MUST NOT USE:**

* **Magic Binding:** Never use libraries that automatically map `os.environ` to Domain Config.
* **Global Variables:** Never access `os.environ` from within domain logic.

→ **[Pattern 05: Config Injection](patterns/05-config-injection.md)**

---

### **VI. The Storage Mandate: DB as Foreign Reality**

**The Principle:** The Domain Core must be agnostic to the mechanism of data storage. The Database is just another **Foreign Reality** that must be explicitly modeled and translated.

#### **MUST USE:**

* **Foreign Models for Storage:** Define Pydantic models (`DbOrder`) that represent the exact shape of the database table with `.to_domain()` method.
* **Stores as Executors:** Frozen Pydantic models that handle DB I/O, injected into orchestrators as fields.
* **Query Results as Sum Types:** Model results as `OrderFound | OrderNotFound`, not `Order | None`.

#### **MUST NOT USE:**

* **Repository Pattern:** No abstract repository interfaces. Stores are concrete Pydantic models.
* **Direct I/O in Domain:** Never write SQL inside Domain Models.
* **Implicit None:** Never return `None` for "not found". Use explicit Sum Type.

→ **[Pattern 06: Storage Foreign Reality](patterns/06-storage-foreign-reality.md)**

---

### **VII. The Translation Mandate: Foreign Reality vs. Internal Truth**

**The Principle:** The outside world speaks a chaotic language; the Domain speaks a strict language. Translation is the act of naturalizing the foreign into the internal.

#### **MUST USE:**

* **Foreign Models:** Define frozen Pydantic models that mirror external schemas exactly with `model_config = {"frozen": True}`.
* **Declarative Mapping:** Use `Field(alias=...)` to handle naming friction declaratively.
* **Self-Translation:** The Foreign Model must own the `.to_domain()` method.

#### **MUST NOT USE:**

* **Imperative Mappers:** Never write standalone functions that copy fields from A to B.
* **Dict Passing:** Never pass raw dictionaries deep into the system. Validate immediately at the border.

→ **[Pattern 07: ACL Translation](patterns/07-acl-translation.md)**

---

### **VIII. The Coordination Mandate: The Orchestrator**

**The Principle:** A system needs a "driver" that does no thinking, only moving. It coordinates the flow of data between Stores, Domain Models, and Executors.

#### **MUST USE:**

* **Orchestrators as Pydantic Models:** Frozen Pydantic models with **dependencies as fields** (stores, gateways, executors).
* **The Main Loop:** Fetch → Translate → Decide → Act → Persist.
* **Dumb Piping:** The Orchestrator takes output from step N and feeds it as input to step N+1.

#### **MUST NOT USE:**

* **Logic in the Loop:** The Orchestrator must never contain `if` statements related to business rules. Its only logic is flow control.
* **Stateless Orchestrators:** If your orchestrator has no fields, you're hiding dependencies. Inject them.
* **Standalone Functions:** Orchestrators are models with methods, not functions.

→ **[Pattern 08: Orchestrator Loop](patterns/08-orchestrator-loop.md)**

---

### **IX. The Workflow Mandate: Process as State Machine**

**The Principle:** The sequence of business steps is Business Logic, not plumbing. Workflows must be modeled as State Machines in the Domain.

#### **MUST USE:**

* **Workflow States as Sum Types:** Explicit types for each state (`SignupPending`, `SignupVerified`, `SignupCompleted`).
* **Transitions as Methods:** State transitions are methods on the source state returning `(NewState, Intent)`.
* **Workflow Runner:** Frozen Pydantic model with `workflow` and `store` as fields.

#### **MUST NOT USE:**

* **Procedural Orchestration:** Never write `if/else` chains in the Service layer to determine operation order.
* **Hidden Chains:** Do not chain side effects implicitly. The flow must be visible in Domain logic.
* **Default Values on `kind`:** All discriminator fields must be explicit.

→ **[Pattern 09: Workflow State Machine](patterns/09-workflow-state-machine.md)**

---

### **X. The Infrastructure Mandate: Capability as Data**

**The Principle:** Infrastructure has a shape. Model it. Domain contexts define abstract capabilities they need. The Service layer binds those capabilities to specific technologies.

#### **MUST USE:**

* **Capability Models:** Domain contexts define abstract capabilities (event persistence, object storage). Technology-specific configurations belong in the service layer.
* **Failure Models:** Smart Enums (`StrEnum`) that enumerate how infrastructure can fail.
* **Capability in Intent:** Intents reference capability models; execution is separate.

#### **MUST NOT USE:**

* **Active Clients in Domain:** Never import or instantiate live clients (`nats.connect()`, `boto3.client()`) inside the Domain.
* **Logic in Adapters:** The Adapter must never make decisions. It executes exactly what the Intent describes.

→ **[Pattern 10: Infrastructure Capability](patterns/10-infrastructure-capability-as-data.md)**
