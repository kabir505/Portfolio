# report_generator.py

import datetime

class ReportGenerator:
    """
    Generates a structured Markdown report of suggestions, including explanations and sustainability impact.
    """

    def __init__(self, suggestions, sustainability_score=None):
        self.suggestions = suggestions
        self.sustainability_score = sustainability_score

    def generate_markdown_report(self, file_name="sustainability_suggestions_report.md"):
        """Generates and writes the Markdown report to a file."""
        report_lines = []
        report_lines.append("# Data Structure Sustainability Suggestions Report")
        report_lines.append(f"_Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n")

        if self.sustainability_score is not None:
            report_lines.append(f"## Sustainability Score: {self.sustainability_score}/100\n")

        if not self.suggestions:
            report_lines.append("No suggestions found. Great job!\n")
        else:
            for suggestion in self.suggestions:
                report_lines.append(f"### Line {suggestion['line']}")
                report_lines.append(f"- **Current structure:** {suggestion['current_type']}")
                if suggestion.get("usage_context"):
                    report_lines.append(f"- **Usage context:** {suggestion['usage_context']}")
                report_lines.append(f"- **Suggestion:** {suggestion['suggestion']}")
                report_lines.append(f"- **Explanation:** {suggestion['explanation']}")
                report_lines.append(f"- **Impact:** {suggestion['impact_estimate']}\n")

        with open(file_name, "w") as f:
            f.write("\n".join(report_lines))

        return file_name
