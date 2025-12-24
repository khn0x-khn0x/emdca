# Agentic Systems: The EMDCA Blueprint

**How to build reliable, production-grade AI Agents using Explicit Architecture.**

"Agentic" is not a new architecture; it is a set of capabilities that require extreme architectural rigor. EMDCA provides the structural guarantees necessary to tame the probabilistic nature of LLMs.

---

## 🥋 The Translation Guide

If you are building an "Agent," you are building a system with **Probabilistic State Transitions**. Here is how to map Agent concepts to EMDCA patterns.

| The Agent Concept | The EMDCA Pattern | Why? |
| :--- | :--- | :--- |
| **"The Agent"** | **[Pattern 09: State Machine](patterns/09-workflow-state-machine.md)** | An Agent is a state machine where transitions use an LLM instead of `if/else`. States are Sum Types. |
| **"Tools"** | **[Pattern 04: Intent as Contract](patterns/04-execution-intent.md)** | Tools are side effects. Return `ToolCallIntent` with `on_success`/`on_failure`. The Shell executes generically. |
| **"LLM Call"** | **Pattern 04 + Pattern 07** | Calling is an Intent. The response is Foreign Reality. Infrastructure returns Sum Type (success/failure variants). |
| **"Prompting"** | **[Pattern 07: Foreign Reality](patterns/07-acl-translation.md)** | The prompt is the request. The output is chaotic text parsed via `.to_domain()` into a strict Domain Model. |
| **"Memory"** | **[Pattern 02: Sum Types](patterns/02-state-sum-types.md)** | Memory is State. Use Discriminated Unions: `Thinking`, `Deciding`, `Acting`. |
| **"Configuration"** | **[Pattern 10: Capability as Data](patterns/10-infrastructure-capability-as-data.md)** | System Prompt, Model Name, Temperature are capability models. |

---

## 🔄 The Agent Cycle

1. **Decide:** Agent state method returns `InferIntent` (specification to call LLM)
2. **Execute:** Shell executes, infrastructure returns `RawLlmResult` Sum Type (no exceptions)
3. **Parse:** `raw.to_foreign().to_domain()` → `LlmResponse`
4. **Interpret:** Intent's `on_success`/`on_failure` maps to domain outcome
5. **Transition:** Outcome feeds back into agent state, returns next state + next intent

See [Pattern 04](patterns/04-execution-intent.md) for the complete Intent → RawResult → Outcome chain.

---

## ⚡ The Big Shift

**Traditional "Agent Frameworks"** hide the control loop, manage memory implicitly, and mix side effects with logic.

**EMDCA Agents** are:
1. **Visible:** The control loop is explicit—state machine with transition methods.
2. **Pure:** The "Brain" outputs Intents. It never touches the network.
3. **Type-Safe:** Every LLM response is validated into a Pydantic model before use.
4. **No Exceptions:** Infrastructure returns Sum Types. Models parse, they don't catch.

Use EMDCA to turn your "Demo" into a "System."
