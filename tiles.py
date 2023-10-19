class Tile:
    def __init__(self, char, lcol, dcol, walkable, opaque):
        self.light_icon = f'[color={lcol}]{char}'
        self.dark_icon = f'[color={dcol}]{char}'
        self.walkable = walkable
        self.opaque = opaque

class Floor(Tile):
    def __init__(self):
        super().__init__('.', 'l_stl', 'd_stl', True, False)

class Wall(Tile):
    def __init__(self):
        super().__init__('#', 'l_stl', 'd_stl', False, True)

class Door(Tile):
    def __init__(self, char, lcol, dcol, walkable, opaque):
        super().__init__(char, lcol, dcol, walkable, opaque)

class ClosedDoor(Door):
    def __init__(self):
        super().__init__('+', 'l_stl', 'd_stl', True, True)

class OpenDoor(Door):
    def __init__(self):
        super().__init__('.', 'l_stl', 'd_stl', True, False)

class BrokenDoor(Door):
    def __init__(self):
        super().__init__('.', 'l_stl', 'd_stl', True, False)

class TestDoor(Door):
    def __init__(self):
        super().__init__('+', 'red', 'red', True, False)

class Airlock(Tile):
    def __init__(self):
        super().__init__('*', 'l_stl', 'd_stl', False, True)

class Space(Tile):
    def __init__(self):
        super().__init__('\u2592', 'black', 'dark gray', True, False)

class MapEdge(Tile):
    def __init__(self):
        super().__init__('.', 'black', 'black', False, True)
