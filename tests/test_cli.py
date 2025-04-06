import subprocess
import os
import textwrap  # ✅ Add this import

def test_cli_runs(tmp_path):
    # Create a simple Python file to test
    test_code = textwrap.dedent("""\
        numbers = [1, 2, 3]
        if 2 in numbers:
            print("Found")
    """)

    test_file = tmp_path / "test_script.py"
    test_file.write_text(test_code)

    report_file = tmp_path / "test_report.md"
    csv_file = tmp_path / "test_usage.csv"

    result = subprocess.run([
        "python", "cli.py",
        "--input", str(test_file),
        "--report", str(report_file),
        "--export-csv", str(csv_file),
        "--score"
    ], capture_output=True, text=True)

    assert result.returncode == 0
    assert os.path.exists(report_file)
    assert os.path.exists(csv_file)
    assert "Sustainability Score" in result.stdout
