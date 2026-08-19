# ADR-001: Choice of LangGraph Over Plain Function-Calling Loop

## Context & Problem Statement
ScoutSphere relies on a multi-agent system where multiple specialized agents (Discovery, Resume Analysis, Matching, Skill Gap, Resume Tailoring, Application Assistant, Tracking, Chatbot/Roadmap) must coordinate stateful execution. 

Standard LLM tool loops (e.g. OpenAI function calling loops) execute linearly in a stateless manner. As agent complexity grows—requiring cyclic conditional routing, state persistence across background jobs, parallel execution, and Human-In-The-Loop (HITL) approval steps—simple function-calling loops become fragile and unmaintainable.

## Decision Drivers
- Need for explicit, deterministic control over multi-agent state flow.
- Support for cyclic workflows (e.g., re-running resume tailoring after skill gap analysis).
- In-memory and persistent state tracking across long-running background tasks.
- Ability to pause graph execution for human approval before submitting job applications.
- Zero extra hosting cost / open-source compatibility.

## Considered Options
1. **Plain LLM Function-Calling Loop (Stateless While-Loop)**
2. **LangChain Sequential Chains / AgentExecutor**
3. **LangGraph (Stateful Multi-Agent Graph Framework)**

## Decision Outcome
Chosen Option: **Option 3 - LangGraph**.

### Justification:
- **Statefulness**: LangGraph provides native `TypedDict` / Pydantic state persistence across execution nodes.
- **Cyclic Graphs**: Unlike standard DAGs or sequential chains, LangGraph allows cycles (e.g., validation loops where an agent re-evaluates outputs).
- **Sub-graphs & Modularity**: Each of ScoutSphere's 9 agents can be developed and unit-tested as isolated graph nodes before being wired into the parent Orchestrator graph.
- **Human-in-the-Loop**: LangGraph supports graph interrupts, allowing the platform to generate a tailored resume or cover letter draft and wait for user review before continuing.

## Status
Accepted.

## Consequences
- **Positive**: Clear visualization, testability, cyclic execution capability, and strict state management.
- **Negative**: Requires learning LangGraph state transitions and maintaining clean node reducer logic.
