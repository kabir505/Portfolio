import os
import subprocess
import argparse
from datetime import datetime

USER_SUBMISSIONS_DIR = "examples/user_submissions/"
REPORTS_DIR = "examples/reports/"
EXPECTED_REPORTS_DIR = "examples/expected_reports/"

def compare_reports(generated, expected):
    """Compare generated and expected reports, ignoring timestamps."""
    try:
        with open(generated, 'r') as gen_file, open(expected, 'r') as exp_file:
            gen_lines = [line.strip() for line in gen_file if not line.startswith("_Generated on")]
            exp_lines = [line.strip() for line in exp_file if not line.startswith("_Generated on")]
            return gen_lines == exp_lines
    except FileNotFoundError:
        return False

def run_batch(refresh_expected=False):
    os.makedirs(REPORTS_DIR, exist_ok=True)

    submission_files = [f for f in os.listdir(USER_SUBMISSIONS_DIR) if f.endswith(".py")]
    if not submission_files:
        print("⚠️ No Python files found in user_submissions/")
        return

    summary = []

    print(f"\n🧪 Batch Analysis Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    for file in submission_files:
        base_name = os.path.splitext(file)[0]
        input_path = os.path.join(USER_SUBMISSIONS_DIR, file)
        report_path = os.path.join(REPORTS_DIR, f"{base_name}_report.md")
        csv_path = os.path.join(REPORTS_DIR, f"{base_name}_usage.csv")
        expected_path = os.path.join(EXPECTED_REPORTS_DIR, f"{base_name}_expected.md")

        # Run the CLI
        result = subprocess.run([
            "python", "cli.py",
            "--input", input_path,
            "--report", report_path,
            "--export-csv", csv_path,
            "--score"
        ], capture_output=True, text=True)

        print(f"📄 {file}:")
        print(f"{result.stdout.strip()}\n")

        # Optional: update expected report
        if refresh_expected:
            with open(expected_path, "w") as f:
                with open(report_path, "r") as generated:
                    f.write(generated.read())
            print(f"🔄 Updated expected report for {base_name}\n")
            summary.append((file, "UPDATED"))
            continue

        # Compare reports
        match = compare_reports(report_path, expected_path)
        if match:
            print(f"✅ Test PASSED for {file}")
            summary.append((file, "PASSED"))
        else:
            print(f"❌ Test FAILED for {file}")
            summary.append((file, "FAILED"))

        print("-" * 50)

    # Summary
    print("\n📋 Batch Test Summary:")
    for name, status in summary:
        print(f"• {name}: {status}")
    print("\n✅ All done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run batch analysis and optionally refresh expected reports.")
    parser.add_argument("--refresh", action="store_true", help="Overwrite expected reports with current output.")
    args = parser.parse_args()

    run_batch(refresh_expected=args.refresh)
