# Inefficient membership test
names = ["Alice", "Bob", "Charlie", "Dave"]
if "Charlie" in names:
    print("Found!")

# Manual counting
letter_counts = {}
for c in "intelligence":
    letter_counts[c] = letter_counts.get(c, 0) + 1

# List used as queue
queue = []
queue.append("task")
queue.pop(0)

# Membership test inside loop
users = [{"id": i} for i in range(1000)]
for user in users:
    if user["id"] in names:
        print("Found match")

# Another manual counter
scores = {}
scores["math"] = scores.get("math", 0) + 1
