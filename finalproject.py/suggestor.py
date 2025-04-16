# suggestor.py

from rules import rules
from snippet_generator import get_fix_snippet  # Generates example code fixes for each suggestion

class Suggestor:
    """
    The Suggestor class is responsible for applying all defined suggestion rules
    to a list of analysed data structure usages (produced by analyser.py).

    Each suggestion rule checks for inefficiencies or suboptimal patterns and,
    if matched, produces a human-readable recommendation and explanation.
    """

    def __init__(self, detected_structures):
        """
        Initializes the Suggestor with a list of detected structures.
        
        Parameters:
        - detected_structures: List of dictionaries, each describing a data structure usage,
          as returned by analyser.py (including type, line number, context, etc.)
        """
        self.detected_structures = detected_structures
        self.suggestions = []

    def apply_rules(self):
        """
        Applies each suggestion rule to every detected structure.
        If a rule matches a structure, the resulting suggestion (dict) is added to self.suggestions.
        Also attaches a code fix snippet from snippet_generator if available.
        """
        for structure in self.detected_structures:
            for rule in rules:
                result = rule.apply(structure)
                if result:
                    # Generate and attach a fix snippet to the suggestion result
                    result["fix_snippet"] = get_fix_snippet(result)
                    self.suggestions.append(result)

    def get_suggestions(self):
        """
        Returns all generated suggestions for the provided detected structures.
        Triggers rule application if not done already.
        
        Returns:
        - List of suggestion dictionaries, each containing:
          - line number
          - structure type
          - usage context
          - suggestion
          - explanation
          - impact estimate
          - fix_snippet (code example of the improvement)
        """
        self.apply_rules()
        return self.suggestions
