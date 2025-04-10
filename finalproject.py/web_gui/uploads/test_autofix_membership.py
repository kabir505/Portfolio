scores["math"] = scores.get("math", 0) + 1

queue = []
queue.append("task")
queue.pop(0)

names = ["Alice", "Bob", "Charlie"]
if "Charlie" in names:
    print("Found")
