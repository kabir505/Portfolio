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
            print(f"\n[DEBUG STRUCTURE] Line {structure.get('line')}, Type: {structure.get('type')}, Details: {structure.get('details')}")
            for rule in rules:
                result = rule.apply(structure)
                if result:
                    print(f"[✅ RULE MATCHED] {result['line']}: {result['suggestion']}")
                    self.suggestions.append(result)


    def get_suggestions(self):
        """Returns compiled suggestions after applying rules."""
        self.apply_rules()
        return self.suggestions
