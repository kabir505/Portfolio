# suggestor.py

from rules import rules
from snippet_generator import get_fix_snippet  # ✅ Add this import

class Suggestor:
    """
    Applies suggestion rules to detected data structures and compiles recommendations.
    """

    def __init__(self, detected_structures):
        self.detected_structures = detected_structures
        self.suggestions = []

    def apply_rules(self):
        """Applies each suggestion rule to each detected structure."""
        for structure in self.detected_structures:
            for rule in rules:
                result = rule.apply(structure)
                if result:
                    result["fix_snippet"] = get_fix_snippet(result) 
                    self.suggestions.append(result)

    def get_suggestions(self):
        """Returns compiled suggestions after applying rules."""
        self.apply_rules()
        return self.suggestions
