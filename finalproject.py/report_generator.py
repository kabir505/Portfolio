# report_generator.py

import datetime

class ReportGenerator:
    """
    Generates a Markdown (.md) report summarising the data structure
    suggestions made by the tool, including context, explanations, impact,
    and example code snippets.
    """

    def __init__(self, suggestions, sustainability_score=None):
        """
        Initializes the ReportGenerator.

        Parameters:
        - suggestions (list): A list of suggestion dictionaries.
        - sustainability_score (int, optional): The calculated sustainability score (0–100).
        """
        self.suggestions = suggestions
        self.sustainability_score = sustainability_score

    def generate_markdown_report(self, file_name="sustainability_suggestions_report.md"):
        """
        Builds the Markdown report from the suggestion data and writes it to a file.

        Parameters:
        - file_name (str): Output filename for the report (default is 'sustainability_suggestions_report.md').

        Returns:
        - str: Path to the written report file.
        """
        report_lines = []

        # Report title and timestamp
        report_lines.append("# Data Structure Sustainability Suggestions Report")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_lines.append(f"_Generated on {timestamp}_\n")

        # Optional: add sustainability score if available
        if self.sustainability_score is not None:
            report_lines.append(f"## Sustainability Score: {self.sustainability_score}/100\n")

        # If no suggestions were found
        if not self.suggestions:
            report_lines.append("No suggestions found. Great job!\n")
        else:
            # Loop through and format each suggestion
            for suggestion in self.suggestions:
                report_lines.append(f"### Line {suggestion['line']}")
                report_lines.append(f"- **Current structure:** {suggestion['current_type']}")
                
                # Optional: include usage context if available
                if suggestion.get("usage_context"):
                    report_lines.append(f"- **Usage context:** {suggestion['usage_context']}")
                
                report_lines.append(f"- **Suggestion:** {suggestion['suggestion']}")
                report_lines.append(f"- **Explanation:** {suggestion['explanation']}")
                report_lines.append(f"- **Impact:** {suggestion['impact_estimate']}")

                # Optional: include code fix snippet if available
                fix_snippet = suggestion.get("fix_snippet")
                if fix_snippet:
                    report_lines.append("")  # Add spacing
                    report_lines.append("```python")
                    report_lines.append(fix_snippet.strip())
                    report_lines.append("```")

                # Add a blank line between suggestions
                report_lines.append("")

        # Write the report to file
        with open(file_name, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))

        return file_name
