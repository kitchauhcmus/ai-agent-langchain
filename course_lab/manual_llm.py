"""REAL LLM + MANUAL TOOL EXECUTION (optional; requires an API key).

Unlike create_agent(), this file manually performs the tool cycle:
1. Ask ChatOpenAI to select a tool (bind_tools)
2. Read AIMessage.tool_calls
3. Validate and execute tool calls in Python
4. Append ToolMessage results to the conversation
5. Ask the model again until it answers.
"""

import json
import os
from .manual import execute_tool_call
from .tools import StudyTools


def get_function_specs() -> list[dict]:
    """Small JSON schemas sent to the model for structured tool requests."""
    return [
        {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "Calculate two numbers with an arithmetic operation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number"},
                        "b": {"type": "number"},
                        "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]},
                    },
                    "required": ["a", "b", "operation"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "average_score",
                "description": "Retrieve overall average grade from an example SQL database.",
                "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "top_students",
                "description": "Get top students by average score (SQL).",
                "parameters": {
                    "type": "object",
                    "properties": {"limit": {"type": "integer", "minimum": 1, "maximum": 10}},
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "plot_scores",
                "description": "Save a chart of sample course scores to a local SVG file.",
                "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "search_notes",
                "description": "Search brief notes about AI agents and tool calling.",
                "parameters": {
                    "type": "object",
                    "properties": {"topic": {"type": "string"}},
                    "required": ["topic"],
                    "additionalProperties": False,
                },
            },
        },
    ]


def create_manual_llm():
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("Set OPENAI_API_KEY in PowerShell first (API billed separately).")
    try:
        from langchain_openai import ChatOpenAI
    except ImportError as e:
        raise RuntimeError("Install optional requirements to use ChatOpenAI") from e
    model = os.environ.get("OPENAI_MODEL", "openai:gpt-4.1-mini")
    model = model.removeprefix("openai:")
    return ChatOpenAI(model=model).bind_tools(get_function_specs())


def manual_llm_turn(model, tools: StudyTools, messages: list, question: str) -> str:
    """Mutates messages so a single terminal session maintains chat context."""
    from langchain_core.messages import HumanMessage, ToolMessage

    messages.append(HumanMessage(content=question))
    for _ in range(6):
        ai_message = model.invoke(messages)
        messages.append(ai_message)
        calls = ai_message.tool_calls
        if not calls:
            return str(ai_message.content)

        for call in calls:
            payload = {"name": call["name"], "arguments": call["args"]}
            print("[LLM requested]", json.dumps(payload, ensure_ascii=False))
            try:
                result = execute_tool_call(payload, tools)
            except (ValueError, TypeError, OverflowError) as exc:
                result = {"error": str(exc)}
            print("[Python executed]", json.dumps(result, ensure_ascii=False))
            messages.append(ToolMessage(
                content=json.dumps(result, ensure_ascii=False),
                tool_call_id=call["id"],
            ))

    return "Stopped after 6 iterations (safety limit)."
