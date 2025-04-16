# usage_data.py

import pandas as pd

class UsageDataCollector:
    """
    Collects detected data structure usage and suggestion entries,
    and stores them in a format suitable for export or further analysis.

    This class uses a unified internal record structure (a list of dictionaries),
    and supports exporting to CSV or retrieving a pandas DataFrame.
    """

    def __init__(self):
        # Internal list to store all usage and suggestion records
        self.records = []

    def add_detected_structure(self, structure):
        """
        Adds a detection record to the internal records list.

        Parameters:
        - structure (dict): A dictionary containing information about a detected structure,
          typically from analyser.py
        """
        self.records.append({
            "type": "detection",
            "line": structure.get("line"),
            "structure_type": structure.get("type"),
            "details": structure.get("details"),
            "usage_context": structure.get("usage_context"),
            "impact_estimate": ""  # Not applicable to raw detections
        })

    def add_suggestion(self, suggestion):
        """
        Adds a suggestion record to the internal records list.

        Parameters:
        - suggestion (dict): A dictionary containing information about a suggestion,
          typically from suggestor.py
        """
        self.records.append({
            "type": "suggestion",
            "line": suggestion.get("line"),
            "structure_type": suggestion.get("current_type"),
            "details": suggestion.get("suggestion"),
            "usage_context": suggestion.get("usage_context"),
            "impact_estimate": suggestion.get("impact_estimate"),
            "fix_snippet": suggestion.get("fix_snippet", "").strip()
        })

    def export_csv(self, file_name="usage_data.csv"):
        """
        Exports all collected records to a CSV file.

        Parameters:
        - file_name (str): The name/path of the file to write to

        Returns:
        - str: Path of the file that was written
        """
        df = pd.DataFrame(self.records)
        df.to_csv(file_name, index=False)
        return file_name

    def get_dataframe(self):
        """
        Returns the collected data as a pandas DataFrame.

        Returns:
        - pd.DataFrame: The structured record data
        """
        return pd.DataFrame(self.records)
