import argparse
from analyser import analyse_code
from suggestor import Suggestor
from report_generator import ReportGenerator
from usage_data import UsageDataCollector

import os
import csv
from datetime import datetime

def calculate_sustainability_score(suggestions):
    """
    Simple heuristic: base score of 100 minus 2 points per suggestion,
    with a floor of 0.
    """
    return max(0, 100 - (len(suggestions) * 2))

def main():
    parser = argparse.ArgumentParser(description="Data Structure Sustainability Suggestion Tool")
    parser.add_argument("--input", help="Path to the Python file to analyse.")
    parser.add_argument("--report", help="Path to save the Markdown report.")
    parser.add_argument("--score", action="store_true", help="Display sustainability score.")
    parser.add_argument("--export-csv", help="Export usage and suggestion data to CSV.")
    parser.add_argument("--verbose", action="store_true", help="Print suggestions in the console.")
    parser.add_argument("--auto-fix", action="store_true", help="Auto-rewrite inefficient patterns with sustainable fixes.")
    parser.add_argument("--chart", action="store_true", help="Generate charts from sustainability_log.csv.")

    args = parser.parse_args()

    # === Generate chart if requested ===
    if args.chart:
        from generate_chart import generate_chart
        generate_chart()
        return

    if not args.input:
        print("⚠️ Please provide an --input file unless you're using --chart.")
        return

    with open(args.input, "r") as file:
        code = file.read()

    from auto_fixer import apply_auto_fixes

    if args.auto_fix:
        fixed_code, changed = apply_auto_fixes(code)
        if changed:
            fixed_path = args.input.replace(".py", "_autofixed.py")
            with open(fixed_path, "w", encoding="utf-8") as f:
                f.write(fixed_code)
            print(f"Auto-fixed file saved as: {fixed_path}")
        else:
            print("No auto-fixes were needed.")

    detected_structures = analyse_code(code)
    suggestor = Suggestor(detected_structures)
    suggestions = suggestor.get_suggestions()

    # Calculate score
    sustainability_score = calculate_sustainability_score(suggestions)

    # Verbose output
    if args.verbose:
        for suggestion in suggestions:
            print(f"Line {suggestion['line']}: {suggestion['suggestion']}")
            print(f"Explanation: {suggestion['explanation']}")
            print(f"Impact: {suggestion['impact_estimate']}")
            print("Fix Snippet:\n" + suggestion.get("fix_snippet", "").strip())
            print()

    # Generate report if requested
    if args.report:
        report_generator = ReportGenerator(suggestions, sustainability_score=sustainability_score)
        report_file = report_generator.generate_markdown_report(file_name=args.report)
        print(f"Report saved to: {report_file}")

    # Export CSV if requested
    if args.export_csv:
        collector = UsageDataCollector()
        for struct in detected_structures:
            collector.add_detected_structure(struct)
        for suggestion in suggestions:
            collector.add_suggestion(suggestion)
        csv_file = collector.export_csv(file_name=args.export_csv)
        print(f"Usage data exported to: {csv_file}")

    # Display sustainability score if requested
    if args.score:
        print(f"Sustainability Score: {sustainability_score}/100")

        # === Append score and suggestions to sustainability_log.csv ===
        log_file = "sustainability_log.csv"
        log_headers = ["timestamp", "filename", "score", "num_suggestions", "suggestion_type"]

        if not os.path.exists(log_file):
            with open(log_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(log_headers)

        for suggestion in suggestions:
            suggestion_type = suggestion.get("suggestion", "Unknown").split(" ")[1]  # e.g. "set", "Counter"
            with open(log_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    os.path.basename(args.input),
                    sustainability_score,
                    1,
                    suggestion_type
                ])

if __name__ == "__main__":
    main()
