"""The Lighthouse: a small text adventure driven by data."""
from dataclasses import dataclass, field

ROOMS = {
    "beach": {
        "description": "You stand on a cold beach. A lighthouse rises to the "
                       "north. A rowing boat lies on the sand.",
        "exits": {"north": "door"},
        "items": ["driftwood"],
    },
    "door": {
        "description": "A heavy iron door blocks the lighthouse entrance.",
        "exits": {"south": "beach", "in": "hall"},
        "locked": "in",
        "key": "rusty key",
    },
    "hall": {
        "description": "A round hall. A spiral staircase leads up. Something "
                       "glints under the stairs.",
        "exits": {"out": "door", "up": "lamp"},
        "items": ["lantern oil"],
    },
    "lamp": {
        "description": "The lamp room. The great lamp is dark and dry.",
        "exits": {"down": "hall"},
        "items": [],
    },
}
HIDDEN = {"driftwood": "rusty key"}       # examining one item reveals another


@dataclass
class Player:
    room: str = "beach"
    inventory: list[str] = field(default_factory=list)
    moves: int = 0


class Game:
    def __init__(self, rooms=None):
        rooms = rooms or ROOMS
        self.rooms = {name: dict(data, items=list(data.get("items", [])))
                      for name, data in rooms.items()}
        self.hidden = dict(HIDDEN)
        self.player = Player()
        self.finished = False

    @property
    def here(self):
        return self.rooms[self.player.room]

    def look(self):
        lines = [self.here["description"]]
        if self.here["items"]:
            lines.append("You see: " + ", ".join(self.here["items"]) + ".")
        lines.append("Exits: " + ", ".join(self.here["exits"]) + ".")
        return "\n".join(lines)

    def go(self, direction):
        if direction not in self.here["exits"]:
            return "You can't go that way."
        if self.here.get("locked") == direction:
            return "It's locked."
        self.player.room = self.here["exits"][direction]
        return self.look()

    def take(self, item):
        if item not in self.here["items"]:
            return f"There is no {item} here."
        self.here["items"].remove(item)
        self.player.inventory.append(item)
        return f"Taken: {item}."

    def examine(self, item):
        if item not in self.player.inventory:
            return f"You aren't carrying {item}."
        if item in self.hidden:
            found = self.hidden.pop(item)
            self.player.inventory.append(found)
            return f"Inside the {item} you find a {found}!"
        return f"It's an ordinary {item}."

    def use(self, item):
        if item not in self.player.inventory:
            return f"You aren't carrying {item}."
        if item == self.here.get("key") and "locked" in self.here:
            del self.here["locked"]
            return "The key turns with a screech. The door swings open."
        if item == "lantern oil" and self.player.room == "lamp":
            self.finished = True
            return ("You fill the great lamp and light it. A beam sweeps "
                    "across the sea. A distant ship turns toward safety.\n"
                    "*** You win! ***")
        return "Nothing happens."

    def inventory(self):
        items = self.player.inventory
        return "You carry: " + (", ".join(items) if items else "nothing") + "."

    def handle(self, command):
        words = command.lower().split()
        if not words:
            return "Say something!"
        verb, rest = words[0], " ".join(words[1:])
        self.player.moves += 1
        actions = {
            "look": lambda: self.look(),
            "go": lambda: self.go(rest),
            "take": lambda: self.take(rest),
            "examine": lambda: self.examine(rest),
            "use": lambda: self.use(rest),
            "inventory": lambda: self.inventory(),
        }
        if verb in ("north", "south", "in", "out", "up", "down"):
            return self.go(verb)
        if verb in actions:
            return actions[verb]()
        return ("I don't understand. Try: look, go <dir>, take <item>, "
                "examine <item>, use <item>, inventory, quit.")


def main():
    game = Game()
    print("THE LIGHTHOUSE\n")
    print(game.look())
    while not game.finished:
        command = input("\n> ").strip()
        if command.lower() in ("quit", "exit"):
            print("Goodbye.")
            return
        print(game.handle(command))
    print(f"You finished in {game.player.moves} moves.")


if __name__ == "__main__":
    main()
