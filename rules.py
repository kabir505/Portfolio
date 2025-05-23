# rules.py

class SuggestionRule:
    """
    Represents a rule that checks for a certain usage context or structure pattern
    and provides a recommendation.
    """

    def __init__(self, condition_function, suggestion, explanation, impact_estimate):
        """
        :param condition_function: A function that takes a structure dict and returns True if the rule applies.
        :param suggestion: Suggested alternative data structure.
        :param explanation: Explanation of why the alternative is better.
        :param impact_estimate: Estimated improvement impact (textual description).
        """
        self.condition_function = condition_function
        self.suggestion = suggestion
        self.explanation = explanation
        self.impact_estimate = impact_estimate

    def apply(self, structure):
        if self.condition_function(structure):
            return {
                "line": structure.get("line"),
                "current_type": structure.get("type"),
                "usage_context": structure.get("usage_context"),
                "suggestion": self.suggestion,
                "explanation": self.explanation,
                "impact_estimate": self.impact_estimate
            }
        return None

# === RULE CONDITIONS ===

def is_membership_test_on_list(structure):
    """
    Matches structures that represent inefficient membership tests on a list.
    """
    return (
        structure.get("usage_context") == "membership_test" and
        structure.get("type", "").lower().startswith("membership test")
    )

def is_manual_counter_detected(structure):
    """
    Matches dictionaries that are being used as manual counters.
    """
    return structure.get("usage_context") == "manual_counter"

def is_queue_like_list_usage(structure):
    """
    Matches list usage patterns that simulate a queue (e.g. append + pop(0)).
    """
    return structure.get("usage_context") == "append_or_pop"

# === RULE DEFINITIONS ===

rules = [
    SuggestionRule(
        is_membership_test_on_list,
        suggestion="Use a set for membership testing.",
        explanation="Sets offer O(1) lookup time compared to O(n) for lists.",
        impact_estimate="Can reduce lookup time and CPU cycles significantly, improving sustainability."
    ),
    SuggestionRule(
        is_manual_counter_detected,
        suggestion="Use collections.Counter instead of manual dictionary counting.",
        explanation="Cleaner, more efficient counting with optimised memory handling.",
        impact_estimate="Reduces repeated memory operations and redundant instructions."
    ),
    SuggestionRule(
        is_queue_like_list_usage,
        suggestion="Consider using collections.deque for queue operations.",
        explanation="Deques are optimised for appending and popping from both ends.",
        impact_estimate="Reduces unnecessary re-indexing in lists, saving computational effort."
    )
]
