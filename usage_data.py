# usage_data.py

import pandas as pd

class UsageDataCollector:
    """
    Collects detected data structure information and suggestions into a pandas DataFrame
    for export and further analysis.
    """

    def __init__(self):
        self.records = []

    def add_detected_structure(self, structure):
        """Adds a detected structure to the records."""
        self.records.append({
            "line": structure.get("line"),
            "structure_type": structure.get("type"),
            "details": structure.get("details"),
            "usage_context": structure.get("usage_context")
        })

    def add_suggestion(self, suggestion):
        """Adds a suggestion entry to the records."""
        self.records.append({
            "line": suggestion.get("line"),
            "structure_type": suggestion.get("current_type"),
            "details": suggestion.get("suggestion"),
            "usage_context": suggestion.get("usage_context"),
            "impact_estimate": suggestion.get("impact_estimate")
        })

    def export_csv(self, file_name="usage_data.csv"):
        """Exports the collected data to a CSV file."""
        df = pd.DataFrame(self.records)
        df.to_csv(file_name, index=False)
        return file_name

    def get_dataframe(self):
        """Returns the pandas DataFrame of all collected records."""
        return pd.DataFrame(self.records)
