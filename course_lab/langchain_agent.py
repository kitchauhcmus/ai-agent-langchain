"""REAL AI AGENT using LangChain (optional; requires an OpenAI API key).

This agent dynamically chooses tools, can make multiple calls, and remembers
conversation context in memory for a single thread. Its dataset is synthetic.
"""

import os
from .tools import StudyTools


def create_study_agent(tools: StudyTools):
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError(
            "Missing OPENAI_API_KEY. Optional API mode has separate usage costs.\n"
            "Windows PowerShell: $env:OPENAI_API_KEY='YOUR_KEY'"
        )

    try:
        from langchain.agents import create_agent
        from langchain.tools import tool
        from langgraph.checkpoint.memory import InMemorySaver
    except ImportError as e:
        raise RuntimeError(
            "Install optional dependencies: python -m pip install -r requirements-optional.txt"
        ) from e

    @tool
    def calculator(a: float, b: float, operation: str) -> dict:
        """Calculate two numbers using add, subtract, multiply or divide.

        Args:
            a: First number.
            b: Second number.
            operation: One of add, subtract, multiply, divide.
        """
        return tools.calculator(a, b, operation)

    @tool
    def average_score() -> dict:
        """Find the average student score from a sample SQLite database."""
        return tools.average_score()

    @tool
    def top_students(limit: int = 3) -> dict:
        """Find the top N students by average grade from sample SQLite data.

        Args:
            limit: Number of students to retrieve, from 1 through 10.
        """
        return tools.top_students(limit)

    @tool
    def list_grades() -> dict:
        """List all student grades from a fictional demonstration database."""
        return tools.list_grades()

    @tool
    def plot_scores() -> dict:
        """Make a local SVG bar chart showing average scores by course."""
        return tools.plot_scores()

    @tool
    def search_notes(topic: str) -> dict:
        """Look up a term in a small offline knowledge base on AI agents.

        Args:
            topic: Search topic, e.g. tool calling, LCEL, SQL, memory.
        """
        return tools.search_notes(topic)

    model = os.environ.get("OPENAI_MODEL", "openai:gpt-4.1-mini")
    return create_agent(
        model=model,
        tools=[calculator, average_score, top_students,
               list_grades, plot_scores, search_notes],
        checkpointer=InMemorySaver(),
        system_prompt=(
            "You are a friendly AI study assistant. Use available tools for "
            "arithmetic, grading data, chart generation, and notes retrieval. "
            "The grades are fictional demo data, not real school records. "
            "Do not fabricate tool results. Report errors clearly. "
            "For simple chat, answer directly without a tool."
        ),
    )


def run_real_agent(agent, question: str, thread_id: str = "classroom-demo") -> str:
    # Using the same thread_id lets InMemorySaver preserve prior messages.
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        config={"configurable": {"thread_id": thread_id}, "recursion_limit": 18},
    )

    # Show what was actually called, not a fabricated sequence.
    messages = result["messages"]
    last_human = max(
        (i for i, message in enumerate(messages) if message.type == "human"),
        default=0,
    )
    for message in messages[last_human + 1:]:
        if getattr(message, "tool_calls", None):
            for call in message.tool_calls:
                print(f"[LLM selected tool] {call['name']}({call['args']})")
    final_message = result["messages"][-1]
    return str(final_message.content)
