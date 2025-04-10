from collections import deque, Counter

data = [x for x in range(1000)]
if 999 in data:
    print("In list")

frequencies = {}
for c in "supercalifragilisticexpialidocious":
    frequencies[c] = frequencies.get(c, 0) + 1

q = []
for i in range(10):
    q.append(i)

while q:
    q.pop(0)

# Efficient section
my_set = {1, 2, 3}
if 2 in my_set:
    print("Safe check")

letter_count = Counter()
letter_count.update("banana")

dq = deque()
dq.append("first")
dq.popleft()
