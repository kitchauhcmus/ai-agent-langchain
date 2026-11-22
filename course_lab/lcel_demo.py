"""LCEL: compose a fixed chain with RunnableLambda and | (no LLM needed).

This illustrates a predictable chain, NOT a reasoning agent. Requires
langchain-core (installed with requirements-optional.txt).
"""

import json
from .manual import execute_tool_call, parse_offline_command
from .tools import StudyTools


def run_lcel_demo(tools: StudyTools, command: str):
    try:
        from langchain_core.runnables import RunnableLambda
    except ImportError as e:
        raise RuntimeError(
            "LCEL needs LangChain. Run: python -m pip install -r requirements-optional.txt"
        ) from e

    # Step 1: parse text -> Step 2: execute explicit tool -> Step 3: format
    def parse(text):
        tool_call = parse_offline_command(text)
        if tool_call is None:
            raise ValueError("Try 'calc 12 * 5', 'avg', 'top 3', or 'chart'")
        return tool_call

    def execute(tool_call):
        return {"requested_tool": tool_call["name"],
                "result": execute_tool_call(tool_call, tools)}

    def format_output(payload):
        return json.dumps(payload, indent=2, ensure_ascii=False)

    chain = (RunnableLambda(parse)
             | RunnableLambda(execute)
             | RunnableLambda(format_output))
    print("LCEL pipeline: parse | execute | format")
    return chain.invoke(command)
