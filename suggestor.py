# suggestor.py

from rules import rules

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
                suggestion = rule.apply(structure)
                if suggestion:
                    self.suggestions.append(suggestion)

    def get_suggestions(self):
        """Returns compiled suggestions after applying rules."""
        self.apply_rules()
        return self.suggestions
