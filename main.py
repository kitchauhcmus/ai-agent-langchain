"""VS Code entry point for the small modular LangChain learning project.

Run: python main.py --demo
     python main.py --mode offline
     python main.py --mode lcel
     python main.py --mode manual-llm
     python main.py --mode agent
"""

import argparse
import json

from course_lab.database import StudyDatabase
from course_lab.tools import StudyTools
from course_lab.manual import TOOL_SCHEMAS, manual_demo

HELP = """Commands in OFFLINE and LCEL mode:
  calc 12 * 5    -> Calculator tool
  calc 15 / 3    -> Calculator tool
  avg            -> SQLite average grade
  top 3          -> SQLite top students
  grades         -> List all demo records
  chart          -> Write outputs/course_averages.svg
  notes lcel     -> Search hardcoded notes (retrieval demo)
  remember An    -> Local memory (OFFLINE only)
  whoami         -> Read local memory (OFFLINE only)
  tools          -> Show available tool schemas
  help           -> Print these commands
  exit           -> Quit

MANUAL-LLM and AGENT modes accept free-form English or Vietnamese questions.
Example: "What is the average grade? Make a chart too." 
"""


def print_tools():
    print(json.dumps(TOOL_SCHEMAS, indent=2, ensure_ascii=False))


def process_offline(tools, text, memory):
    normalized = text.lower().strip()
    if normalized.startswith("remember "):
        memory["name"] = text[9:].strip()
        print("Stored locally:", memory["name"])
    elif normalized == "whoami":
        print("Name in current session:", memory.get("name", "Unknown"))
    elif normalized == "tools":
        print_tools()
    else:
        result = manual_demo(tools, text)
        if result is None:
            print("Unknown command. Type 'help'.")


def process_lcel(tools, text):
    from course_lab.lcel_demo import run_lcel_demo
    print(run_lcel_demo(tools, text))


def main():
    parser = argparse.ArgumentParser(description="Mini modular AI Agent course lab")
    parser.add_argument("--mode", choices=["offline", "lcel", "manual-llm", "agent"],
                        default="offline")
    parser.add_argument("--demo", action="store_true",
                        help="Run a small automated demo in offline mode")
    args = parser.parse_args()

    db = StudyDatabase()
    tools = StudyTools(db)
    memory = {}

    try:
        if args.demo:
            print("=== OFFLINE TOOL CALLING DEMO ===")
            for command in ("calc 12 * 5", "avg", "top 3", "notes tool calling", "chart"):
                print("\nUSER:", command)
                process_offline(tools, command, memory)
            print("\nDone. Open outputs/course_averages.svg")
            return

        if args.mode == "agent":
            from course_lab.langchain_agent import create_study_agent, run_real_agent
            agent = create_study_agent(tools)
        if args.mode == "manual-llm":
            from course_lab.manual_llm import create_manual_llm, manual_llm_turn
            model = create_manual_llm()
            from langchain_core.messages import SystemMessage
            messages = [SystemMessage(content="You are a helpful study assistant. Use tools for factual demo data. The dataset is fictional.")]
        print(f"\nAI Study Assistant | mode={args.mode.upper()}")
        print(HELP)
        while True:
            try:
                message = input("You> ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not message:
                continue
            if message.lower() == "exit":
                break
            if message.lower() == "help":
                print(HELP)
                continue
            try:
                if args.mode == "offline":
                    process_offline(tools, message, memory)
                elif args.mode == "lcel":
                    process_lcel(tools, message)
                elif args.mode == "manual-llm":
                    print("LLM>", manual_llm_turn(model, tools, messages, message))
                else:
                    print("Agent>", run_real_agent(agent, message))
            except Exception as exc:
                # In a study demo show errors instead of abruptly crashing.
                print(f"ERROR ({type(exc).__name__}): {exc}")
    except (RuntimeError, ImportError) as exc:
        print("Setup error:", exc)
    finally:
        db.close()
        print("Bye!")


if __name__ == "__main__":
    main()
