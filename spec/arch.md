## **Architecture Specification: Explicitly Modeled Data-Centric Architecture (EMDCA)**.

This document contains the non-negotiable engineering standards for the system. It is written as a strict set of directives for developers to follow without ambiguity.

---

### **I. The Construction Mandate: The Pure Factory**

**The Principle:** Validation is not a check; it is a construction process. Logic is a calculation, not an action. Therefore, the code that makes decisions must be separated from the code that executes them.

#### **MUST USE:**

* **Pure Factories:** All domain logic and decision-making must live exclusively in **Pure Factory Functions**. These functions accept raw, unstructured data and "parse" it into a valid Domain Type.  
* **Value Objects:** Primitive Obsession is forbidden. Use **Value Objects** (Rich Types) to wrap all primitives (e.g., `EmailAddress` instead of `str`).
* **Explicit Construction:** Never use default values in Domain Models (e.g., `status: str = 'pending'`). Defaults are hidden business rules. The Factory must set every field explicitly.
* **Parse, Don't Validate:** Instead of checking if data.is\_valid, try to construct the success type. If the data is invalid, the factory must return a distinct Failure Type.  
* **Total Functions:** The factory must handle **every** possible input state and return a valid result object (Success or Failure). It must never crash or raise unhandled exceptions on expected domain data.

#### **MUST NOT USE:**

* **Side Effects in Factories:** The factory must **never** perform I/O, database queries, API calls, or read global variables. It must be a pure function of its inputs.  
* **The "Draft" Object:** Never create an empty or partial object and populate it field-by-field. Objects must be complete and valid from the moment of instantiation.  
* **Validation Methods:** Never write an .is\_valid() method on a model. If an object exists, it is valid by definition.

---

### **II. The State Mandate: Sum Types Over Product Types**

**The Principle:** Software complexity grows with the number of possible states. We must minimize the state space by making invalid combinations of state unrepresentable.

#### **MUST USE:**

* **Discriminated Unions (Sum Types):** Mutually exclusive realities must be modeled as Unions of distinct Types (e.g., EvaluationResult \= EnterContext | WaitContext).  
* **Structural Proofs:** Each Context type must contain the specific data required for that reality (e.g., EnterContext must contain an EntryProposal).  
* **Behavioral Enums:** Simple state machines should be modeled as **Behavioral Enums** (Smart Enums) where the logic lives on the Enum member itself.
* **Pattern Matching:** Use structural pattern matching (e.g., match/case) to handle the different realities returned by the factory.

#### **MUST NOT USE:**

* **The God Model (Product Types):** Never use a single class with optional fields to represent conflicting states (e.g., a class containing both entry\_data and exit\_data where one is always None).  
* **Boolean Flags for State:** Never use boolean flags (e.g., is\_entering, is\_waiting) to determine the state of an object. The **Type** of the object determines the state.

---

### **III. The Control Flow Mandate: Railway Oriented Programming**

**The Principle:** Logic is a flow of data. Branching should be handled as a topology of tracks, not as a series of exceptions or jumps.

#### **MUST USE:**

* **The Railway Switch:** Logic branches must happen inside the Factory. The flow must explicitly guide data onto either a "Success Track" (returning a Success Context) or a "Failure Track" (returning a Wait/Halt Context).  
* **Explicit Fall-through:** Every logical branch must terminate in a return value. "Doing nothing" must be represented by an explicit WaitContext, not by returning None.

#### **MUST NOT USE:**

* **Exceptions for Control Flow:** Never use try/except to handle domain logic (e.g., InsufficientFundsException). Exceptions are strictly for system failures (Network Down, OOM).  
* **Implicit Returns:** Never allow a function to return None implicitly. The return type must always be explicit.

---

### **IV. The Execution Mandate: Intent as Data**

**The Principle:** Deciding to do something and doing it are separate concerns. The "Core" decides; the "Shell" executes.

#### **MUST USE:**

* **Command Objects (Intents):** The domain model must return inert, serializable **Specification Objects** describing the side effect AND its outcome interpretation.
* **Complete Instructions:** The Intent must contain:
    1. **Execution Parameters:** All data required to perform the operation.
    2. **Success Mapping:** How to transform **primitives extracted from** the raw infrastructure result into a Domain Success type.
    3. **Failure Mapping:** How to transform the error string into a Domain Failure type.
    4. **Exception Classification:** Which infrastructure exceptions represent expected failures (return Failure type) vs. system panics (propagate).

Note: The `on_success` method receives **primitives** (strings, ints, bools), never foreign objects. The Shell extracts values from infrastructure responses before calling Intent methods. This keeps the Domain completely decoupled from infrastructure response shapes.
* **Generic Execution:** The Shell should be able to execute ANY Intent using a single generic executor function. If adding a new Intent requires new code in the Shell beyond wiring, the Intent is incomplete.

#### **MUST NOT USE:**

* **Service Injection:** Never inject a "Service" or "Client" into a domain model. Models must never call methods like .execute() or .save().  
* **Closures/Callbacks:** Intents must be pure data (JSON serializable), not functions or code blocks.
* **Per-Operation Exception Handling:** The Shell must not contain operation-specific try/except blocks that construct domain Result types. Exception-to-Result mapping belongs in the Intent specification.
* **Result Construction in Shell:** The Shell must not directly instantiate Success or Failure types. It calls the Intent's mapping methods.

---

### **V. The Configuration Mandate: Foreign Reality vs Internal Truth**

**The Principle:** Configuration comes from the chaotic outside world (Environment Variables). It is a **Foreign Reality** that must be explicitly translated into a structured **Internal Truth** (Domain Config) before entering the system.

#### **MUST USE:**

* **Foreign Models for Env:** Explicitly model the raw environment (e.g., `EnvVars`) using declaration mapping (aliases) to handle the chaotic naming conventions of the OS.
* **Explicit Translation:** Convert the raw environment model into a pure Domain Config object at the application entry point.
* **Context Injection:** Pass the resolved Domain Config into logic functions as arguments.

#### **MUST NOT USE:**

* **Magic Binding:** Never use libraries that automatically map `os.environ` directly to Domain Config objects. The translation must be visible.
* **Global Variables:** Never access `os.environ` or global config singletons from within the domain logic.

---

### **VI. The Abstraction Mandate: Storage as Foreign Reality**

**The Principle:** The Domain Core must be agnostic to the mechanism of data storage. The Database is just another **Foreign Reality** (External System) that must be explicitly modeled and translated.

#### **MUST USE:**

*   **Foreign Models for Storage:** Define Pydantic models (e.g., `DbOrder`) that represent the exact shape of the database table.
*   **Shell Execution:** The Shell (Service Layer) executes the I/O (SQL queries), validates the result into the Foreign Model, and translates it to the Domain Object (`.to_domain()`).

#### **MUST NOT USE:**

*   **Direct I/O in Domain:** Never write SQL, file paths, or specific database import statements inside a Domain Model or Factory.
*   **Leaky Abstractions:** Do not return database-specific cursors or ORM objects (like SQLAlchemy Row Proxies) into the Domain. The Shell must naturalize the data immediately.

---

### **VII. The Translation Mandate: Foreign Reality vs. Internal Truth**

**The Principle:** The outside world speaks a chaotic language; the Domain speaks a strict language. We must explicitly model both the **Foreign Reality** (external systems) and the **Internal Truth** (business concepts). Translation is the act of naturalizing the foreign into the internal.

#### **MUST USE:**

* **Foreign Models:** Define Domain Objects that mirror external schemas exactly (e.g., `CoinbaseCandle`). These are not dumb DTOs; they represent the domain's knowledge of the external world.
* **Declarative Mapping:** Use field aliasing (e.g., `Field(alias="o")`) to handle naming friction declaratively at the type level.
* **Self-Translation:** The Foreign Model must own the method (e.g., `.to_domain()`) that converts itself into the Internal Truth.

#### **MUST NOT USE:**

* **Imperative Mappers:** Never write standalone functions that copy fields from A to B. Translation logic belongs on the Foreign Model.
* **Dict Passing:** Never pass raw dictionaries or JSON blobs deep into the system. Validate them against the Foreign Model immediately at the border.

---

### **VIII. The Coordination Mandate: The Orchestrator**

**The Principle:** A system needs a "driver" that does no thinking, only moving. It coordinates the flow of data between the Repository, the Factory, and the Execution shell.

#### **MUST USE:**

* **The Main Loop (Application Service):** A "dumb" procedural loop that performs the following cycle:
    1.  **Fetch** (Call Repository)
    2.  **Translate** (Call ACL/Mapper)
    3.  **Decide** (Call Pure Factory)
    4.  **Act** (Execute Intent)
    5.  **Persist** (Call Repository to save state)
* **Piping:** The Orchestrator treats data as a pipe. It takes the output of step 1 and feeds it as the input to step 2.

#### **MUST NOT USE:**

* **Logic in the Loop:** The Orchestrator must never contain `if` statements related to business rules (e.g., `if price > 100`). Its only logic should be flow control (start/stop/sleep).
* **Orchestrator Injection:** Never pass the Orchestrator itself into a Domain Model. The Core should not know it is being orchestrated.

---

### **IX. The Workflow Mandate: Process as State Machine**

**The Principle:** The sequence of business steps (A → B → C) is Business Logic, not plumbing. Therefore, workflows must be modeled as State Machines in the Domain, not as procedural scripts in the Service.

#### **MUST USE:**

* **Workflow Models:** Create explicit Domain Models that represent the *lifecycle* of a process (e.g., `SignupWorkflow`).
* **Next-Step Intents:** The Domain must return an Intent indicating the *next* logical step in the chain (e.g., `return SignupResult(next_step=SendEmailIntent)`).
* **State Machines:** Use the Factory to determine transitions. The Factory accepts the `CurrentState` + `Input` and returns the `NextState` + `Intent`.

#### **MUST NOT USE:**

* **Procedural Orchestration:** Never write a function in the Service layer that contains a sequence of `if/else` checks to determine the order of operations (e.g., `if user.is_vip: send_gold_email()`).
* **Hidden Chains:** Do not chain side effects implicitly (e.g., a database trigger that starts a shipping job). The flow must be visible and explicit in the Domain logic.

---

### **X. The Infrastructure Mandate: Capability as Data**

**The Principle:** Infrastructure is a capability to be modeled as Data, not a Service to be executed. The Domain defines the *Topology* and *Intent* of the infrastructure as pure values, while the Shell handles the *Runtime Connection*.

#### **MUST USE:**

* **Infrastructure Models:** Define the "Shape" of the infrastructure using pure Domain Models (e.g., `NatsStream`, `S3BucketConfig`). These models describe *what* the infrastructure looks like, not *how* to connect to it.
* **Topology as Config:** The generic constraints of the infrastructure (retention policies, subject hierarchies, queue names) must be defined in the Domain, allowing the logic to reason about the topology.
* **Shell Execution:** The Shell (Service Layer) receives Intents from the Domain and executes them using client libraries (e.g., `nats-py`, `boto3`). No "Adapter Class" wrapper is required if the client is simple.

#### **MUST NOT USE:**

* **Active Clients in Domain:** Never import or instantiate live clients (e.g., `nats.connect()`, `boto3.client()`) inside the Domain. The Domain models the *configuration* of the client, not the client instance.
* **Logic in Adapters:** The Adapter must never make decisions (e.g., "if event type is A, publish to topic B"). It must only execute exactly what the Intent describes.
