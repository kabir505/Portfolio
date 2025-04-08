# snippet_generator.py

def get_fix_snippet(suggestion):
    """
    Returns a Python code snippet (as a string) that shows how to apply the suggestion.
    """
    suggestion_text = suggestion.get("suggestion", "").lower()
    context = suggestion.get("usage_context", "")
    structure = suggestion.get("current_type", "").lower()

    # Manual counter → Counter()
    if "counter" in suggestion_text:
        return (
            "from collections import Counter\n"
            "counts = Counter()\n"
            "counts.update(your_data_here)\n"
        )

    # Membership test on list → use set
    if "set" in suggestion_text and context == "membership_test":
        return (
            "data = { ... }  # Use a set instead of a list\n"
            "if item in data:\n"
            "    print(\"Found\")\n"
        )

    # Queue using list → use deque
    if "deque" in suggestion_text and context == "append_or_pop":
        return (
            "from collections import deque\n"
            "queue = deque()\n"
            "queue.append(\"item\")\n"
            "queue.popleft()\n"
        )

    # Defaultdict fix
    if "defaultdict" in suggestion_text:
        return (
            "from collections import defaultdict\n"
            "d = defaultdict(int)\n"
            "d[key] += 1\n"
        )

    # OrderedDict fix
    if "ordereddict" in suggestion_text:
        return (
            "from collections import OrderedDict\n"
            "ordered_dict = OrderedDict()\n"
            "ordered_dict[\"key\"] = \"value\"\n"
        )

    # Dict comprehension
    if "comprehension" in suggestion_text and "dictionary" in structure:
        return (
            "result = {k: v for k, v in pairs}\n"
        )

    # Fallback
    return "# No fix snippet available for this suggestion.\n"
