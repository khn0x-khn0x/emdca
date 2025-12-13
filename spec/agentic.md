# Agentic Systems: The EMDCA Blueprint

**How to build reliable, production-grade AI Agents using Explicit Architecture.**

"Agentic" is not a new architecture; it is a set of capabilities that require extreme architectural rigor. EMDCA provides the structural guarantees necessary to tame the probabilistic nature of LLMs.

---

## 🥋 The Translation Guide

If you are building an "Agent," you are building a system with **Probabilistic State Transitions**. Here is how to map Agent concepts to EMDCA patterns.

| The Agent Concept | The EMDCA Pattern | Why? |
| :--- | :--- | :--- |
| **"The Agent"** | **[Pattern 09: Process as State Machine](patterns/09-workflow-state-machine.md)** | An Agent is just a state machine where the transition function (`step()`) uses an LLM to decide the next state instead of `if/else`. |
| **"Tools"** | **[Pattern 04: Execution Intent](patterns/04-execution-intent.md)** | Tools are side effects. The Agent should never *call* a tool; it should return a `ToolCallIntent`. The Shell executes it. |
| **"Prompting"** | **[Pattern 07: Foreign Reality](patterns/07-acl-translation.md)** | The LLM is a chaotic API. The Prompt is the Request Contract; the Parser is the ACL that forces the output into a pure Domain Model. |
| **"Memory"** | **[Pattern 02: State (Sum Types)](patterns/02-state-sum-types.md)** | Memory is just State. Use Discriminated Unions to model exactly what the agent knows at each step (`Thinking`, `Deciding`, `Acting`). |
| **"Configuration"** | **[Pattern 10: Infrastructure as Data](patterns/10-infrastructure-capability-as-data.md)** | Your System Prompt, Model Name, and Temperature are topology configuration. Model them as `AgentConfig`. |

---

## ⚡ The Big Shift

**Traditional "Agent Frameworks"** often hide the control loop, manage memory implicitly, and mix side effects (Tool calls) with logic (Reasoning).

**EMDCA Agents** are:
1.  **Visible:** The control loop is explicit in the Service Layer.
2.  **Pure:** The "Brain" just outputs Intents. It never touches the network.
3.  **Type-Safe:** Every "thought" from the LLM is validated into a Pydantic model before use.

Use EMDCA to turn your "Demo" into a "System."

