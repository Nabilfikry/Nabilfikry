from generate import level, streaks

assert streaks([]) == (0, 0)
assert streaks([1, 1, 0, 1, 1, 1]) == (3, 3)
assert streaks([1, 1, 1, 0, 2, 0]) == (1, 3)  # today empty: streak still alive
assert streaks([1, 0, 0]) == (0, 1)
assert level(0, 10) == 0 and level(1, 10) == 1 and level(10, 10) == 4
print("ok")

