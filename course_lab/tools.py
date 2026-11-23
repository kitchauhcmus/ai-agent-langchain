"""TOOL LAYER. Functions available to both the offline router and real LLM.

A tool's job is small and focused. The agent chooses WHICH tool to use;
Python is responsible for EXECUTING it.
"""
# Git practice: improve calculator feature
import math
from pathlib import Path
from .database import StudyDatabase
from .visualization import make_course_chart

ROOT = Path(__file__).resolve().parents[1]

NOTES = {
    "tool calling": "LLM generates a structured tool request; external code executes it.",
    "lcel": "LCEL composes small runnable steps into a predictable chain with |.",
    "agent": "An agent selects tools and can repeat a plan-act-observe loop.",
    "memory": "Memory preserves useful context across interactions within a thread.",
    "sql": "SQL queries structured data. Prefer validated read-only operations.",
}


class StudyTools:
    def __init__(self, db: StudyDatabase, output_dir: Path = ROOT / "outputs"):
        self.db = db
        self.output_dir = output_dir

    def calculator(self, a: float, b: float, operation: str) -> dict:
        """Perform safe arithmetic: add, subtract, multiply or divide."""
        if not all(math.isfinite(float(v)) for v in (a, b)):
            raise ValueError("Numbers must be finite")
        operators = {
            "add": lambda: a + b,
            "subtract": lambda: a - b,
            "multiply": lambda: a * b,
            "divide": lambda: a / b,
        }
        if operation not in operators:
            raise ValueError("operation must be add/subtract/multiply/divide")
        if operation == "divide" and b == 0:
            raise ValueError("Cannot divide by zero")
        value = operators[operation]()
        return {"operation": operation, "a": a, "b": b, "result": value}

    def average_score(self) -> dict:
        """Read the overall average grade using SQLite."""
        return {"overall_average": self.db.average_score(), "scale": 10}

    def top_students(self, limit: int = 3) -> dict:
        """Return top students ranked by their average grade from SQLite."""
        return {"top_students": self.db.top_students(limit)}

    def list_grades(self) -> dict:
        """Show the synthetic student/course/score records stored in SQLite."""
        return {"grades": self.db.all_grades()}

    def plot_scores(self) -> dict:
        """Generate an SVG bar chart of average scores per course."""
        output = self.output_dir / "course_averages.svg"
        return {"chart_file": make_course_chart(self.db.course_averages(), output)}

    def search_notes(self, topic: str) -> dict:
        """Search a tiny hardcoded knowledge base, illustrating retrieval."""
        query = topic.strip().lower()
        matches = [
            {"topic": name, "note": value}
            for name, value in NOTES.items()
            if query in name or name in query
        ]
        return {"results": matches, "source": "local demo notes"}
