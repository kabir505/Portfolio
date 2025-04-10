from flask import Flask, render_template, request
import os
import sys
from datetime import datetime
import csv
from collections import defaultdict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from analyser import analyse_code
from suggestor import Suggestor
from cli import calculate_sustainability_score
from generate_chart import generate_chart

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def index():
    suggestions = []
    score = None
    filename = None
    raw_code = ""
    highlighted_code = ""
    summary = {}
    structure_summary = {}
    structure_chart_data = []
    suggestion_category_data = {}

    if request.method == "POST":
        editor_code = request.form.get("editor_code")
        uploaded_file = request.files.get("codefile")

        # Determine source of input
        if editor_code:
            filename = "LiveEditorCode.py"
            raw_code = editor_code

        elif uploaded_file and uploaded_file.filename.endswith(".py"):
            filename = uploaded_file.filename
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            uploaded_file.save(filepath)

            with open(filepath, "r") as f:
                raw_code = f.read()

        else:
            # No valid input submitted
            return render_template("index.html")

        # Analyse and suggest
        detected = analyse_code(raw_code)
        suggestor = Suggestor(detected)
        suggestions = suggestor.get_suggestions()
        score = calculate_sustainability_score(suggestions)

        # Fix Summary
        for s in suggestions:
            s_type = s.get("suggestion", "Unknown").split(" ")[-1].lower()
            summary[s_type] = summary.get(s_type, 0) + 1

        # Structure Summary
        for d in detected:
            key = d["type"]
            if key not in structure_summary:
                structure_summary[key] = {"count": 0, "lines": [], "suggested": False}
            structure_summary[key]["count"] += 1
            structure_summary[key]["lines"].append(d["line"])

        for s in suggestions:
            if s["current_type"] in structure_summary:
                structure_summary[s["current_type"]]["suggested"] = True

        # Log suggestions
        log_file = "sustainability_log.csv"
        headers = ["timestamp", "filename", "score", "num_suggestions", "suggestion_type"]
        if not os.path.exists(log_file):
            with open(log_file, "w", newline="") as f:
                csv.writer(f).writerow(headers)

        for s in suggestions:
            s_type = s.get("suggestion", "Unknown").split(" ")[1]
            with open(log_file, "a", newline="") as f:
                csv.writer(f).writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    filename,
                    score,
                    1,
                    s_type
                ])

        generate_chart()

        # Structure chart data
        structure_chart_data = [
            {
                "type": struct,
                "count": data["count"],
                "efficiency": 100 if not data["suggested"]
                else round((1 - len([s for s in suggestions if s["current_type"] == struct]) / data["count"]) * 100, 2)
            }
            for struct, data in structure_summary.items()
        ]

        # Suggestion categories
        category_counter = defaultdict(int)
        for s in suggestions:
            category = s.get("suggestion", "").split()[-1].lower()
            category_counter[category] += 1

        suggestion_category_data = dict(category_counter)

        # Highlight code
        theme = request.form.get("theme", "dracula")
        formatter = HtmlFormatter(
            linenos="table",
            lineanchors="line",
            anchorlinenos=True,
            style=theme,
            noclasses=True
        )
        highlighted_code = highlight(raw_code, PythonLexer(), formatter)

        # Add anchor IDs to lines
        lines = highlighted_code.splitlines()
        count = 0
        for i, line in enumerate(lines):
            if "<tr>" in line:
                count += 1
                lines[i] = line.replace("<tr>", f'<tr id="line-{count}">', 1)
        highlighted_code = "\n".join(lines)

    return render_template("index.html",
        suggestions=suggestions,
        score=score,
        filename=filename,
        code=highlighted_code,
        summary=summary,
        structure_summary=structure_summary,
        structure_chart_data=structure_chart_data,
        suggestion_category_data=suggestion_category_data
    )


if __name__ == "__main__":
    app.run(debug=True)
