class Tile:
    def __init__(self, char, color, walkable, transparent):
        self.char = char
        self.color = color
        self.icon = f'[color={color}]{char}'
        self.walkable = walkable
        self.transparent = transparent

class Floor(Tile):
    def __init__(self):
        super().__init__('.', 'steel_floor', True, True)

class Wall(Tile):
    def __init__(self):
        super().__init__('#', 'steel_wall', False, False)

class Door(Tile):
    def __init__(self, char, color, walkable, transparent):
        super().__init__(char, color, walkable, transparent)

class ClosedDoor(Door):
    def __init__(self):
        super().__init__('+', 'steel_floor', False, False)

class OpenDoor(Door):
    def __init__(self):
        super().__init__('.', 'steel_floor', True, True)

class BrokenDoor(Door):
    def __init__(self):
        super().__init__('.', 'steel_floor', True, True)

class Airlock(Tile):
    def __init__(self):
        super().__init__('*', 'steel_floor', False, False)

class Space(Tile):
    def __init__(self):
        super().__init__(' ', 'black', True, True)
