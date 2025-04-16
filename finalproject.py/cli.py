# cli.py

import argparse
import os
from analyser import analyse_code
from suggestor import Suggestor
from report_generator import ReportGenerator
from usage_data import UsageDataCollector
from auto_fixer import apply_auto_fixes

def calculate_sustainability_score(suggestions):
    """
    Calculates a sustainability score based on the number of suggestions.
    Starts at 100 and subtracts 2 points per suggestion, with a minimum of 0.
    """
    return max(0, 100 - (len(suggestions) * 2))

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Data Structure Sustainability Suggestion Tool")
    parser.add_argument("--input", help="Path to the Python file to analyse.")
    parser.add_argument("--report", help="Path to save the Markdown report.")
    parser.add_argument("--score", action="store_true", help="Display sustainability score.")
    parser.add_argument("--export-csv", help="Export usage and suggestion data to CSV.")
    parser.add_argument("--verbose", action="store_true", help="Print suggestions in the console.")
    parser.add_argument("--auto-fix", action="store_true", help="Auto-rewrite inefficient patterns with sustainable fixes.")
    parser.add_argument("--chart", action="store_true", help="Generate charts from sustainability_log.csv.")
    args = parser.parse_args()

    # If chart generation is requested
    if args.chart:
        from generate_chart import generate_chart
        generate_chart()
        return

    # Require input file unless using --chart
    if not args.input:
        print("Warning: Please provide an --input file unless you're using --chart.")
        return

    # Read the input Python file
    with open(args.input, "r") as file:
        code = file.read()

    # Apply auto-fixes if requested
    if args.auto_fix:
        fixed_code, changed = apply_auto_fixes(code)
        if changed:
            fixed_path = args.input.replace(".py", "_autofixed.py")
            with open(fixed_path, "w", encoding="utf-8") as f:
                f.write(fixed_code)
            print(f"Auto-fixed file saved as: {fixed_path}")
        else:
            print("No auto-fixes were needed.")

    # Analyse the code and collect structure usage
    detected_structures = analyse_code(code)

    # Generate suggestions using Suggestor
    suggestor = Suggestor(detected_structures)
    suggestions = suggestor.get_suggestions()

    # Calculate sustainability score
    sustainability_score = calculate_sustainability_score(suggestions)

    # Print suggestions in the terminal if verbose mode is on
    if args.verbose:
        for suggestion in suggestions:
            print(f"Line {suggestion['line']}: {suggestion['suggestion']}")
            print(f"Explanation: {suggestion['explanation']}")
            print(f"Impact: {suggestion['impact_estimate']}")
            print("Fix Snippet:\n" + suggestion.get("fix_snippet", "").strip())
            print()

    # Generate a Markdown report if requested
    if args.report:
        report_generator = ReportGenerator(suggestions, sustainability_score=sustainability_score)
        report_file = report_generator.generate_markdown_report(file_name=args.report)
        print(f"Report saved to: {report_file}")

    # Export structured data to CSV if requested
    if args.export_csv:
        collector = UsageDataCollector()
        for struct in detected_structures:
            collector.add_detected_structure(struct)
        for suggestion in suggestions:
            collector.add_suggestion(suggestion)
        csv_file = collector.export_csv(file_name=args.export_csv)
        print(f"Usage data exported to: {csv_file}")

    # Only print the score if requested
    if args.score:
        print(f"Sustainability Score: {sustainability_score}/100")

if __name__ == "__main__":
    main()
