# Mini Project — AI Study Assistant (Course Companion)

**Course:** Fundamentals of Building AI Agents  
**Goal:** Understand tool calling, LCEL, LangChain agents, memory, SQL, and data visualization through one small Python project.

## Architecture

```text
                        [User Request]
                              |
                 +------------+------------+
                 |                         |
          Offline Router                LLM Agent
           (Fixed Rules)           (Dynamic Decision)
                 |                         |
                 +-----------+-------------+
                             |
                    [Tool Registry]
                 /       |        \
           Calculator  SQLite    Chart/Notes
                 \       |        /
                       [Results]
                             |
                   [Final Response]
```

**Important distinction:** The offline router is a deterministic demonstration, not an AI model. The LangChain agent uses an LLM and chooses tools dynamically.

## Module 1 — Foundations of Tool Calling

- **Tool Definition:** Name + Description + Parameters.
- **Tool Request:** A structured instruction specifying which tool to call and the arguments.
- **Tool Execution:** External Python code runs the requested function.
- **Tool Validation:** A schema checks arguments before execution.
- **Traditional Pattern:** Application directly handles requests and calls.
- **Embedded Pattern:** A framework manages the calling loop.

**Flow:** `Request → Tool Selection → Structured Arguments → Execution → Observation → Response`

## Module 2 — LCEL and Manual Tool Calling

- **LCEL (LangChain Expression Language):** Compose fixed runnable operations using `|`.
- **RunnableLambda:** Wrap a Python function as a runnable step.
- **Manual Calling:** Application explicitly validates and dispatches JSON-like tool requests.
- **Structured Outputs:** Make actions machine-readable.
- **Validation:** Reject unknown tools, unexpected arguments, and invalid types.

**Flow:** `Parse | Validate/Execute | Format` (fixed chain)

## Module 3 — Agents, SQL, and Visualization

- **LangChain `@tool`:** Exposes a documented Python function to an LLM.
- **`create_agent()`:** Combines an LLM and tools within an execution loop.
- **Memory:** `InMemorySaver()` keeps conversation state for a thread until the process ends.
- **SQL Tool:** Runs predefined read-only database queries.
- **Visualization Tool:** Produces an SVG file from sample data.
- **Agent Loop:** `Decide → Use Tool → Observe → Repeat or Answer`.

## Study Checklist

- [ ] Run `python main.py --demo`.
- [ ] Read `manual.py` and understand the tool schema.
- [ ] Explain why a structured tool call is **not** tool execution.
- [ ] Run the LCEL pipeline and explain why it is a workflow, not an agent.
- [ ] Add a new custom tool.
- [ ] Run the optional real LangChain agent (if API access is available).
- [ ] Ask the agent to query SQL data and generate a chart.
- [ ] Read `tests/test_course_lab.py` and explain every assertion.

## Quick Comparison

| Approach | Who Selects Tools? | Who Executes? | Needs LLM? |
|---|---|---|---|
| Offline Demo | Rule-based parser | Python | No |
| Manual Tool Calling with LLM | LLM | Application (`manual_llm.py`) | Yes |
| LCEL Demo | Fixed pipeline | LangChain runnables | No |
| LangChain Agent | LLM | LangChain tools | Yes |

> **Golden Rule:** An LLM selects *what to do*; the application/framework executes *how to do it*.

**Manual LLM exercise:** `bind_tools()` → read `AIMessage.tool_calls` → Python executes → create `ToolMessage` → invoke again.
