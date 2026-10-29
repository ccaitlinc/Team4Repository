import ast
from pathlib import Path


# Read main.py without importing or running the game.
source = Path("main.py").read_text(encoding="utf-8")
tree = ast.parse(source)

# Extract only the functions needed for testing.
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


red_team = environment["red_team"]
green_team = environment["green_team"]
responses = environment["udp"].responses
process_hit = environment["process_hit"]


# Test friendly fire.
process_hit("101:102")

assert red_team[0]["score"] == -10
assert red_team[1]["score"] == -10
assert green_team[0]["score"] == 0
assert len(responses) == 2
assert set(responses) == {"101", "102"}

print("\nPASS: Shooter loses 10 points.")
print("PASS: Teammate loses 10 points.")
print("PASS: Opponent score stays unchanged.")
print("PASS: Two equipment-ID responses are requested.")


# Test a normal hit against an opponent.
red_team[0]["score"] = 0
green_team[0]["score"] = 0
responses.clear()

process_hit("101:201")

assert red_team[0]["score"] == 0
assert green_team[0]["score"] == 0
assert responses == ["201"]

print("\nPASS: Normal opponent hit does not apply friendly-fire penalties.")
print("PASS: Normal hit requests only the target equipment ID.")


# Test red player scoring on the green base (code 43).
red_team[0]["score"] = 0
red_team[0]["has_base"] = False
responses.clear()

process_hit("101:43")

assert red_team[0]["score"] == 100
assert red_team[0]["has_base"] is True
assert responses == ["101"]

print("\nPASS: Red player receives 100 points for hitting the green base.")
print("PASS: Red player's base indicator is activated.")
print("PASS: Base hit requests the shooter's equipment ID.")


# Test green player scoring on the red base (code 53).
green_team[0]["score"] = 0
green_team[0]["has_base"] = False
responses.clear()

process_hit("201:53")

assert green_team[0]["score"] == 100
assert green_team[0]["has_base"] is True
assert responses == ["201"]

print("\nPASS: Green player receives 100 points for hitting the red base.")
print("PASS: Green player's base indicator is activated.")
print("PASS: Base hit requests the shooter's equipment ID.")


# Test that a player does not score on their own team's base.
red_team[0]["score"] = 0
red_team[0]["has_base"] = False
responses.clear()

process_hit("101:53")

assert red_team[0]["score"] == 0
assert red_team[0]["has_base"] is False
assert responses == ["101"]

print("\nPASS: Hitting your own team's base does not award points.")