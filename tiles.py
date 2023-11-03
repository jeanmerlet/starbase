class Tile:
    def __init__(self, char, color, tile, walkable, opaque):
        self.char = char
        self.icon = f'[color={color}]{char}'
        if tile is None:
            self.tile = self.icon
        else:
            self.tile = tile
        self.walkable = walkable
        self.opaque = opaque

class Floor(Tile):
    def __init__(self):
        super().__init__('.', 'l_stl', '[0xE001]', True, False)

class Wall(Tile):
    def __init__(self):
        super().__init__('#', 'l_stl', '[0xE002]', False, True)

class Door(Tile):
    def __init__(self, char, color, tile, walkable, opaque, open_tile,
                 closed_tile):
        super().__init__(char, color, tile, walkable, opaque)
        self.open_tile = open_tile
        self.closed_tile = closed_tile

class AutoDoor(Door):
    def __init__(self):
        super().__init__('+', 'l_stl', '[0xE004]', False, True, '[0xE003]',
                         '[0xE004]')

class Space(Tile):
    def __init__(self):
        super().__init__('\u2592', 'black', None, True, False)

class MapEdge(Tile):
    def __init__(self):
        super().__init__('\u2592', 'black', None, False, True)
