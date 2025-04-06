numbers = [1, 2, 3, 4, 5]

# Inefficient membership check
if 3 in numbers:
    print("Found!")

# Manual counter pattern
counts = {}
counts['a'] = counts.get('a', 0) + 1

# List acting like a queue
q = []
q.append(10)
q.pop(0)
