"""VISUALIZATION LAYER. Create a real SVG chart with the Python stdlib.

No plotting library or API key is needed to understand data visualization.
"""

from html import escape
from pathlib import Path


def make_course_chart(course_averages: list[dict], output_path: Path) -> str:
    if not course_averages:
        raise ValueError("No data to visualize")
    width, height = 660, 350
    bottom, top = 288, 74
    max_score = 10.0
    left, gap, bar_width = 90, 50, 120
    bars = []
    for index, item in enumerate(course_averages):
        course = escape(str(item["course"]))
        avg = float(item["average"])
        if not 0 <= avg <= max_score:
            raise ValueError("Scores must be from 0 to 10")
        bar_height = (bottom - top) * avg / max_score
        x = left + index * (bar_width + gap)
        y = bottom - bar_height
        bars.extend([
            f'<rect x="{x}" y="{y:.1f}" width="{bar_width}" '
            f'height="{bar_height:.1f}" rx="7" fill="#6277ee"/>',
            f'<text x="{x + bar_width / 2}" y="{y - 10:.1f}" '
            f'text-anchor="middle" font-size="16" fill="#18253b">{avg:.2f}</text>',
            f'<text x="{x + bar_width / 2}" y="{bottom + 27}" '
            f'text-anchor="middle" font-size="15" fill="#18253b">{course}</text>',
        ])
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    <rect width="100%" height="100%" fill="#ffffff"/>
    <text x="34" y="36" font-family="Arial" font-weight="bold" font-size="22" fill="#18253b">Average score by course</text>
    <text x="34" y="57" font-family="Arial" font-size="13" fill="#64748b">Demo student dataset · maximum score: 10</text>
    <line x1="53" y1="{bottom}" x2="623" y2="{bottom}" stroke="#94a3b8" stroke-width="2"/>
    <line x1="53" y1="{top}" x2="53" y2="{bottom}" stroke="#94a3b8" stroke-width="2"/>
    <text x="35" y="{top+5}" font-family="Arial" font-size="13" fill="#64748b">10</text>
    <text x="42" y="{bottom+5}" font-family="Arial" font-size="13" fill="#64748b">0</text>
    <g font-family="Arial">{''.join(bars)}</g>
    </svg>'''
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg, encoding="utf-8")
    return str(output_path.resolve())
