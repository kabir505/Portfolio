# rules.py

class SuggestionRule:
    """
    Represents a suggestion rule that checks a given structure pattern
    and provides a recommendation if the condition is met.
    
    Each rule contains:
    - A condition function that evaluates the structure
    - A suggestion message
    - An explanation for why the suggestion matters
    - An estimate of the performance or sustainability impact
    """

    def __init__(self, condition_function, suggestion, explanation, impact_estimate):
        self.condition_function = condition_function
        self.suggestion = suggestion
        self.explanation = explanation
        self.impact_estimate = impact_estimate

    def apply(self, structure):
        """
        Applies this rule to a given structure dictionary.
        If the condition function returns True, returns a dictionary
        with the suggestion and metadata; otherwise returns None.
        """
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
    Returns True if the structure is a membership test on a list,
    and it's not already marked as efficient.
    """
    return (
        structure.get("usage_context") == "membership_test" and
        structure.get("type", "").lower().startswith("membership test") and
        "efficient" not in structure.get("details", "").lower()
    )

def is_manual_counter_detected(structure):
    """
    Returns True if the structure shows a manual counter using dict.get() + 1.
    """
    return structure.get("usage_context") == "manual_counter"

def is_queue_like_list_usage(structure):
    """
    Returns True if the structure uses append/pop on a list like a queue,
    but it's not a deque.
    """
    return (
        structure.get("usage_context") == "append_or_pop" and
        "efficient — using deque" not in structure.get("details", "").lower()
    )

def is_dict_keys_loop(structure):
    """
    Returns True if the structure is a for-loop iterating over dict.keys()/values()/items().
    """
    return (
        structure.get("usage_context") == "dict_keys_loop" and
        "dict." in structure.get("details", "")
    )

def is_redundant_conversion(structure):
    """
    Returns True if the structure uses redundant wrapping like list(set(...)) or set(list(...)).
    """
    return structure.get("usage_context") == "redundant_conversion"

def is_manual_dict_loop(structure):
    """
    Returns True if a dictionary is manually built inside a loop.
    """
    return structure.get("usage_context") == "manual_dict_loop"

def is_reversed_temp_list(structure):
    """
    Returns True if the structure uses reversed(list(...)), which is inefficient.
    """
    return structure.get("usage_context") == "reversed_temp_list"

def is_ordereddict_used_like_dict(structure):
    """
    Returns True if OrderedDict is used but there's no specific usage context,
    implying a normal dict could suffice.
    """
    return (
        structure.get("type") == "OrderedDict" and
        "usage_context" not in structure
    )

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
    ),
    SuggestionRule(
        is_dict_keys_loop,
        suggestion="Iterate directly over the dictionary instead of using .keys().",
        explanation="Avoids an unnecessary function call and improves readability.",
        impact_estimate="Reduces CPU instructions and function overhead — especially in large dictionaries."
    ),
    SuggestionRule(
        is_redundant_conversion,
        suggestion="Avoid redundant wrapping like list(set(...)) or set(list(...)).",
        explanation="These patterns create extra objects and often aren't needed.",
        impact_estimate="Avoids unnecessary memory allocations and improves performance."
    ),
    SuggestionRule(
        is_manual_dict_loop,
        suggestion="Use dict(zip(...)) or a dictionary comprehension.",
        explanation="More efficient and idiomatic than building dicts via loops.",
        impact_estimate="Reduces line count and avoids repeated dictionary insertions."
    ),
    SuggestionRule(
        is_reversed_temp_list,
        suggestion="Avoid reversing a temporary list. Use reversed() on existing sequences or generators.",
        explanation="Creating a list just to reverse it wastes memory and CPU cycles.",
        impact_estimate="Removes a full O(n) copy — especially important for large data."
    ),
    SuggestionRule(
        is_ordereddict_used_like_dict,
        suggestion="Use a plain dict instead of OrderedDict if order isn’t needed.",
        explanation="Since Python 3.7+, dict preserves insertion order.",
        impact_estimate="Avoids unnecessary imports and object overhead."
    )
]
