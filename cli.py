# cli.py

import argparse
from analyser import analyse_code
from suggestor import Suggestor
from report_generator import ReportGenerator
from usage_data import UsageDataCollector

def calculate_sustainability_score(suggestions):
    """
    Simple heuristic: base score of 100 minus 2 points per suggestion,
    with a floor of 0.
    """
    return max(0, 100 - (len(suggestions) * 2))

def main():
    parser = argparse.ArgumentParser(description="Data Structure Sustainability Suggestion Tool")
    parser.add_argument("--input", required=True, help="Path to the Python file to analyse.")
    parser.add_argument("--report", help="Path to save the Markdown report.")
    parser.add_argument("--score", action="store_true", help="Display sustainability score.")
    parser.add_argument("--export-csv", help="Export usage and suggestion data to CSV.")
    parser.add_argument("--verbose", action="store_true", help="Print suggestions in the console.")

    args = parser.parse_args()

    with open(args.input, "r") as file:
        code = file.read()

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
            print(f"Impact: {suggestion['impact_estimate']}\n")

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

if __name__ == "__main__":
    main()
