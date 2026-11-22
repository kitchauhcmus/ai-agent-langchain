"""Run: python -m unittest discover -s tests -v"""

import json
import tempfile
import unittest
from pathlib import Path

from course_lab.database import StudyDatabase
from course_lab.tools import StudyTools
from course_lab.manual import (
    parse_offline_command, validate_tool_call, execute_tool_call,
)


class TestMiniAgent(unittest.TestCase):
    def setUp(self):
        self.db = StudyDatabase()
        self.tmp = tempfile.TemporaryDirectory()
        self.tools = StudyTools(self.db, Path(self.tmp.name))

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def test_calculator(self):
        call = parse_offline_command("calc 12 * 5")
        result = execute_tool_call(call, self.tools)
        self.assertEqual(result["result"], 60)

    def test_division_error(self):
        call = parse_offline_command("calc 10 / 0")
        with self.assertRaises(ValueError):
            execute_tool_call(call, self.tools)

    def test_reject_unknown_tool(self):
        with self.assertRaises(ValueError):
            validate_tool_call({"name": "os.system", "arguments": {}})

    def test_reject_invalid_tool_arguments(self):
        with self.assertRaises(ValueError):
            validate_tool_call({"name": "top_students", "arguments": {"limit": "SELECT *"}})
        with self.assertRaises(ValueError):
            validate_tool_call({"name": "calculator", "arguments": {"a": 1, "b": 2, "operation": "add", "hack": True}})

    def test_sql_average(self):
        self.assertAlmostEqual(self.db.average_score(), 8.46)

    def test_sql_top(self):
        ranked = self.db.top_students(limit=2)
        self.assertEqual(len(ranked), 2)
        self.assertEqual(ranked[0]["student"], "An")

    def test_notes(self):
        result = self.tools.search_notes("lcel")
        self.assertEqual(result["results"][0]["topic"], "lcel")

    def test_chart(self):
        result = self.tools.plot_scores()
        path = Path(result["chart_file"])
        self.assertTrue(path.exists())
        self.assertIn("<svg", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
