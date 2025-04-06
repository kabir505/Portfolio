from collections import deque, Counter

# Use set for membership
ids = {100, 200, 300}
if 200 in ids:
    print("Found!")

# Use Counter
words = Counter()
words.update("banana")

# Use deque as queue
queue = deque()
queue.append("x")
queue.popleft()
