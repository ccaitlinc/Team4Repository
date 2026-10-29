
import ast
from pathlib import Path


# Read main.py without importing or running the game.
source = Path("main.py").read_text(encoding="utf-8")
tree = ast.parse(source)

# Extract only the functions needed for friendly-fire testing.
needed_functions = {
    "make_empty_team",
    "get_team_list",
    "find_player_by_equipment_id",
    "process_hit",
}

functions = [
    node
    for node in tree.body
    if isinstance(node, ast.FunctionDef)
    and node.name in needed_functions
]

found_functions = {node.name for node in functions}
missing = needed_functions - found_functions

if missing:
    raise RuntimeError(f"Could not find functions: {missing}")


# Record UDP responses instead of sending real network packets.
class FakeUDP:
    def __init__(self):
        self.responses = []

    def broadcast(self, equipment_id):
        self.responses.append(equipment_id)


environment = {
    "MAX_PLAYERS_PER_TEAM": 15,
    "udp": FakeUDP(),
}

test_module = ast.Module(body=functions, type_ignores=[])
exec(compile(test_module, "main.py", "exec"), environment)

# Create the teams.
environment["red_team"] = environment["make_empty_team"]()
environment["green_team"] = environment["make_empty_team"]()

environment["red_team"][0].update({
    "equipment_id": "101",
    "codename": "RedOne",
})
environment["red_team"][1].update({
    "equipment_id": "102",
    "codename": "RedTwo",
})
environment["green_team"][0].update({
    "equipment_id": "201",
    "codename": "GreenOne",
})

# Test friendly fire.
environment["process_hit"]("101:102")

red_team = environment["red_team"]
green_team = environment["green_team"]
responses = environment["udp"].responses

assert red_team[0]["score"] == -10, "Shooter should lose 10 points"
assert red_team[1]["score"] == -10, "Teammate should lose 10 points"
assert green_team[0]["score"] == 0, "Opponent score should not change"
assert len(responses) == 2, "Friendly fire should request two responses"
assert set(responses) == {"101", "102"}, "Both equipment IDs should be sent"

print("\nPASS: Shooter loses 10 points.")
print("PASS: Teammate loses 10 points.")
print("PASS: Opponent score stays unchanged.")
print("PASS: Two equipment-ID responses are requested.")


# Test a normal hit against an opponent.
red_team[0]["score"] = 0
green_team[0]["score"] = 0
responses.clear()

environment["process_hit"]("101:201")

assert red_team[0]["score"] == 0, "Shooter score should not change"
assert green_team[0]["score"] == 0, "Opponent score should not change"
assert responses == ["201"], "Normal hit should respond with target ID"

print("\nPASS: Normal opponent hit does not apply friendly-fire penalties.")
print("PASS: Normal hit requests only the target equipment ID.")