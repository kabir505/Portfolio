# Inefficient membership test
names = ["Alice", "Bob", "Charlie", "Dave", "Eve"]
if "Charlie" in names:
    print("Found")

# Manual counting using a dict
letter_counts = {}
for c in "artificialintelligence":
    letter_counts[c] = letter_counts.get(c, 0) + 1

# List used as a queue
queue = []
queue.append("start")
queue.append("process")
queue.pop(0)
queue.pop(0)

# Deep nested usage
users = [{"id": i} for i in range(1000)]
found = False
for user in users:
    if user["id"] in names:
        found = True

# Redundant dictionary usage
scores = {}
scores["math"] = scores.get("math", 0) + 1
scores["science"] = scores.get("science", 0) + 1
