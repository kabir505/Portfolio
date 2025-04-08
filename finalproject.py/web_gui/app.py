from flask import Flask, render_template, request
import os
import sys
from datetime import datetime
import csv

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

    if request.method == "POST":
        uploaded_file = request.files["codefile"]
        if uploaded_file and uploaded_file.filename.endswith(".py"):
            filename = uploaded_file.filename
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            uploaded_file.save(filepath)

            with open(filepath, "r") as f:
                raw_code = f.read()

            detected = analyse_code(raw_code)
            suggestor = Suggestor(detected)
            suggestions = suggestor.get_suggestions()
            score = calculate_sustainability_score(suggestions)

            for s in suggestions:
                s_type = s.get("suggestion", "Unknown").split(" ")[-1].lower()
                summary[s_type] = summary.get(s_type, 0) + 1

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

            # ✅ formatter with table layout and dark style
            formatter = HtmlFormatter(
                linenos="table",
                style="dracula",
                noclasses=True
            )
            highlighted_code = highlight(raw_code, PythonLexer(), formatter)

    return render_template("index.html",
        suggestions=suggestions,
        score=score,
        filename=filename,
        code=highlighted_code,
        summary=summary
    )

if __name__ == "__main__":
    app.run(debug=True)


