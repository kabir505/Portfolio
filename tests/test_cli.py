import subprocess
import os
import textwrap

def test_cli_runs(tmp_path):
    test_code = textwrap.dedent("""\
        numbers = [1, 2, 3]
        if 2 in numbers:
            print("Found")
    """)

    test_file = tmp_path / "test_script.py"
    test_file.write_text(test_code)

    report_file = tmp_path / "test_report.md"
    csv_file = tmp_path / "test_usage.csv"

    result = subprocess.run(
        [
            "python", "cli.py",
            "--input", str(test_file),
            "--report", str(report_file),
            "--export-csv", str(csv_file),
            "--score"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",     
        errors="ignore"       
    )

    assert result.returncode == 0
    assert report_file.exists()
    assert csv_file.exists()
    assert "Sustainability Score" in result.stdout
