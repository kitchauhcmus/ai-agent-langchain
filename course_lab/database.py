"""DATA LAYER. A tiny SQLite database filled from a local CSV file.

We expose a few safe read-only SQL operations instead of giving an LLM
permission to execute arbitrary SQL statements.
"""

import csv
import sqlite3
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "study_scores.csv"


class StudyDatabase:
    def __init__(self, csv_path: Path = DATA_PATH):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute(
            "CREATE TABLE grades (student TEXT NOT NULL, "
            "course TEXT NOT NULL, score REAL NOT NULL)"
        )
        with open(csv_path, newline="", encoding="utf-8") as f:
            records = csv.DictReader(f)
            self.conn.executemany(
                "INSERT INTO grades(student, course, score) VALUES (?, ?, ?)",
                [
                    (row["student"], row["course"], float(row["score"]))
                    for row in records
                ],
            )
        self.conn.commit()

    def average_score(self) -> float:
        row = self.conn.execute("SELECT AVG(score) AS value FROM grades").fetchone()
        return round(float(row["value"]), 2)

    def top_students(self, limit: int = 3) -> list[dict]:
        # Parameterized SQL avoids inserting untrusted values into a query.
        if type(limit) is not int or not 1 <= limit <= 10:
            raise ValueError("limit must be an integer from 1 to 10")
        rows = self.conn.execute(
            "SELECT student, ROUND(AVG(score), 2) AS average "
            "FROM grades GROUP BY student ORDER BY average DESC, student LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]

    def course_averages(self) -> list[dict]:
        rows = self.conn.execute(
            "SELECT course, ROUND(AVG(score), 2) AS average "
            "FROM grades GROUP BY course ORDER BY course"
        ).fetchall()
        return [dict(row) for row in rows]

    def all_grades(self) -> list[dict]:
        rows = self.conn.execute(
            "SELECT student, course, score FROM grades "
            "ORDER BY student, course"
        ).fetchall()
        return [dict(row) for row in rows]

    def close(self) -> None:
        self.conn.close()
