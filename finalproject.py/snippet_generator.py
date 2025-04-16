# snippet_generator.py

def get_fix_snippet(suggestion):
    """
    Returns a Python code snippet (as a string) that shows how to apply the suggestion.

    Parameters:
    - suggestion: A dictionary containing fields such as:
        - "suggestion": The text recommendation (e.g. "Use collections.Counter...")
        - "usage_context": The rule context tag (e.g. "manual_counter")
        - "current_type": The structure type detected (e.g. "Dictionary")

    Returns:
    - A string containing a suggested Python code snippet that resolves the issue.
    - If no match is found, returns a default placeholder comment.
    """
    suggestion_text = suggestion.get("suggestion", "").lower()
    context = suggestion.get("usage_context", "")
    structure = suggestion.get("current_type", "").lower()

    # === Rule 1: Manual counter → Use collections.Counter
    if "counter" in suggestion_text:
        return (
            "from collections import Counter\n"
            "counts = Counter()\n"
            "counts.update(your_data_here)\n"
        )

    # === Rule 2: Membership test on list → Use a set
    if "set" in suggestion_text and context == "membership_test":
        return (
            "data = { ... }  # Use a set instead of a list\n"
            "if item in data:\n"
            "    print(\"Found\")\n"
        )

    # === Rule 3: List used as a queue → Use deque
    if "deque" in suggestion_text and context == "append_or_pop":
        return (
            "from collections import deque\n"
            "queue = deque()\n"
            "queue.append(\"item\")\n"
            "queue.popleft()\n"
        )

    # === Rule 4: Dict.keys()/values()/items() → Iterate directly
    if "iterate directly" in suggestion_text and context == "dict_keys_loop":
        return (
            "my_dict = {\"a\": 1, \"b\": 2}\n"
            "for key in my_dict:\n"
            "    print(key)\n"
        )

    # === Rule 5: Redundant list(set(...)) or set(list(...)) conversion
    if "redundant" in suggestion_text and context == "redundant_conversion":
        return (
            "# Remove unnecessary wrapping like list(set(...)) or set(list(...))\n"
            "unique_items = set(data)  # or list(data), depending on your needs\n"
        )

    # === Rule 6: Manual dict loop → Use dict comprehension
    if "comprehension" in suggestion_text and "dictionary" in structure:
        return (
            "result = {k: v for k, v in pairs}\n"
        )

    # === Rule 7: reversed(list(...)) → Avoid temporary list
    if "reversed" in suggestion_text and context == "reversed_temp_list":
        return (
            "data = get_data()\n"
            "for item in reversed(data):\n"
            "    print(item)\n"
        )

    # === Rule 8: OrderedDict used like normal dict
    if "ordereddict" in suggestion_text:
        return (
            "from collections import OrderedDict\n"
            "ordered_dict = OrderedDict()\n"
            "ordered_dict[\"key\"] = \"value\"\n"
        )

    # === Additional: defaultdict usage
    if "defaultdict" in suggestion_text:
        return (
            "from collections import defaultdict\n"
            "d = defaultdict(int)\n"
            "d[key] += 1\n"
        )

    # === Fallback: No matching snippet found
    return "# No fix snippet available for this suggestion.\n"
