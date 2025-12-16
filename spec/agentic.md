# Agentic Systems: The EMDCA Blueprint

**How to build reliable, production-grade AI Agents using Explicit Architecture.**

"Agentic" is not a new architecture; it is a set of capabilities that require extreme architectural rigor. EMDCA provides the structural guarantees necessary to tame the probabilistic nature of LLMs.

---

## 🥋 The Translation Guide

If you are building an "Agent," you are building a system with **Probabilistic State Transitions**. Here is how to map Agent concepts to EMDCA patterns.

| The Agent Concept | The EMDCA Pattern | Why? |
| :--- | :--- | :--- |
| **"The Agent"** | **[Pattern 09: Process as State Machine](patterns/09-workflow-state-machine.md)** | An Agent is just a state machine where the transition function (`step()`) uses an LLM to decide the next state instead of `if/else`. |
| **"Tools"** | **[Pattern 04: Intent as Contract](patterns/04-execution-intent.md)** | Tools are side effects. Return `ToolCallIntent` with complete specification (`on_success`/`on_failure`). The Shell executes it generically. |
| **"LLM Call"** | **Pattern 04 + Pattern 07** | Calling is an Intent (`InferIntent`). The Response is a Foreign Reality (`LlmResponse`). The Intent owns the translation. |
| **"Prompting"** | **[Pattern 07: Foreign Reality](patterns/07-acl-translation.md)** | The Prompt is the Request Contract. The output is chaotic text that must be parsed into a strict Domain Model via `.to_domain()`. |
| **"Memory"** | **[Pattern 02: State (Sum Types)](patterns/02-state-sum-types.md)** | Memory is just State. Use Discriminated Unions to model exactly what the agent knows at each step (`Thinking`, `Deciding`, `Acting`). |
| **"Configuration"** | **[Pattern 10: Infrastructure as Data](patterns/10-infrastructure-capability-as-data.md)** | Your System Prompt, Model Name, and Temperature are topology configuration. Model them as `AgentConfig`. |

---

## 🔄 The Complete Agent Loop

EMDCA unifies the "Outbound" (Intent) and "Inbound" (Translation) patterns into a rigorous cycle.

### 1. Outbound: The Inference Intent (Pattern 04)
The Agent decides to call the LLM. This is a side effect. The Intent defines the parameters and how to map the raw string response into a Foreign Model.

```python
class InferIntent(BaseModel):
    model_config = {"frozen": True}
    
    model: str
    messages: list[Message]
    temperature: float
    catch_exceptions: tuple[str, ...] = ("RateLimitError", "TimeoutError")
    
    def on_success(self, response_text: str, model: str, usage: int) -> "LlmResponse":
        """Receives extracted primitives, not raw API response object."""
        return LlmResponse(
            text=response_text,
            model=model,
            tokens_used=usage,
        )
    
    def on_failure(self, error: str) -> "InferenceFailed":
        return InferenceFailed(error=error)
```

### 2. Inbound: The Foreign Model Translation (Pattern 07)
The Shell executes the intent, extracts the primitives, and calls `on_success`. We get `LlmResponse`. Now we naturalize it.

```python
# Shell execution
on_success=lambda resp: intent.on_success(
    response_text=resp.choices[0].message.content,
    model=resp.model,
    usage=resp.usage.total_tokens,
)
```

### 3. The Cycle
1.  **Decide:** Agent State → `InferIntent` (Specification to call LLM).
2.  **Execute:** Shell reads Intent, calls LLM, catches exceptions (Generic Executor).
3.  **Result:** Success → `LlmResponse` (Foreign Model).
4.  **Translate:** `LlmResponse.to_domain()` → `ToolCallIntent | FinalAnswer | NoOp`.
5.  **Act:** If `ToolCallIntent`, Shell executes via generic executor.
6.  **Update:** Result feeds back into Agent State.

This cycle ensures that **Probabilistic Logic** (The LLM) is sandwiched between **Deterministic Guards** (Intents and Foreign Models).

---

## ⚡ The Big Shift

**Traditional "Agent Frameworks"** often hide the control loop, manage memory implicitly, and mix side effects (Tool calls) with logic (Reasoning).

**EMDCA Agents** are:
1.  **Visible:** The control loop is explicit in the Service Layer.
2.  **Pure:** The "Brain" outputs **Decision Outcomes** (Intents or NoOp). It never touches the network.
3.  **Type-Safe:** Every "thought" from the LLM is validated into a Pydantic model before use.

Use EMDCA to turn your "Demo" into a "System."
