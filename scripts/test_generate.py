from generate import level, streaks, render_stat_card, render_header, render_activity

assert streaks([]) == (0, 0)
assert streaks([1, 1, 0, 1, 1, 1]) == (3, 3)
assert streaks([1, 1, 1, 0, 2, 0]) == (1, 3)  # today empty: streak still alive
assert streaks([1, 0, 0]) == (0, 1)
assert level(0, 10) == 0 and level(1, 10) == 1 and level(10, 10) == 4

# Test card rendering
sc = render_stat_card("Repositories", 13, "repo", "#8b5cf6")
assert "<svg" in sc and "Repositories" in sc and "13" in sc

print("ok")
