import numpy as np
import pandas as pd
from procgen import Grid, RectRoom, Hallway
from entities import Entity, Actor
from tiles import *


class Map:
    TILE_ID = {
        0: Wall(),
        1: Floor(),
        2: ClosedDoor()
    }

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = np.empty((width, height), dtype=object)
        self.opaque = np.full((width, height), fill_value=False)
        self.visible = np.full((width, height), fill_value=False)
        self.explored = np.full((width, height), fill_value=False)
        self.visible = np.full((width, height), fill_value=True)
        self.explored = np.full((width, height), fill_value=True)
        self.rooms = []

    def render(self, blt):
        for x in range(self.width):
            for y in range(self.height):
                if self.explored[x, y]:
                    if self.visible[x, y]:
                        blt.print(x, y, self.tiles[x, y].light_icon)
                    else:
                        blt.print(x, y, self.tiles[x, y].dark_icon)

    def get_start(self):
        x = np.random.randint(self.width)
        y = np.random.randint(self.height)
        if isinstance(self.tiles[x, y], Floor):
            return x, y
        else:
            return self.get_start()

    def in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self. height

    def is_adjacent(self, x1y1_coords, x2y2_coords):
        x1, y1 = x1y1_coords
        x2, y2 = x2y2_coords
        if abs(x1-x2) <= 1 and abs(y1-y2) <= 1:
            return True
        return False

    def _convert_grid_idx_to_tiles(self, x1, x2, y1, y2, grid_idx):
        for x in range(x1, x2):
            for y in range(y1, y2):
                self.tiles[x, y] = self.TILE_ID[grid_idx[x - x1, y - y1]]
                if self.tiles[x, y].opaque:
                    self.opaque[x, y] = True

    def _gen_tiles(self, gridx, gridy, grid_idx):
        for x in range(self.width):
            for y in range(self.height):
                self.tiles[x, y] = Space()
        x1 = gridx
        y1 = gridy
        x2 = gridx + grid_idx.shape[0]
        y2 = gridy + grid_idx.shape[1]
        self._convert_grid_idx_to_tiles(x1, x2, y1, y2, grid_idx)

    def _define_room(self, x, y, checked):
        """(Rect)Rooms and hallways are defined by the top left
        and bottom right corners of their wall tiles. Hallways
        are rooms with width or height 1.
        """
        x1, y1 = x - 1, y - 1
        x2 = x + 1
        while not isinstance(self.tiles[x2, y], (Wall, Door)):
            x2 += 1
        y2 = y + 1
        while not isinstance(self.tiles[x, y2], (Wall, Door)):
            y2 += 1
        if x2 - x1 == 2 or y2 - y1 == 2:
            self.rooms.append(Hallway(x1, y1, x2, y2))
        else:
            self.rooms.append(RectRoom(x1, y1, x2, y2))
        checked[x1:x2+1, y1:y2+1] = True

    def _find_rooms(self):
        checked = np.full((self.width, self.height), fill_value=False)
        for x in range(self.width):
            for y in range(self.height):
                if checked[x, y]: continue
                if isinstance(self.tiles[x, y], Floor):
                    self._define_room(x, y, checked)
                else:
                    checked[x, y] = True

    def _create_entity(self, ent_data, name, x, y):
        char = ent_data.loc[name, 'char']
        color = ent_data.loc[name, 'color']
        blocking = ent_data.loc[name, 'blocking']
        return Actor(name, x, y, char, color, blocking)

    def _place_ent(self, entities, ent_data, name, room):
        x = np.random.randint(room.x1+1, room.x2)
        y = np.random.randint(room.y1+1, room.y2)
        if np.any([ent.x == x and ent.y == y for ent in entities]):
            self._place_ent(entities, ent_data, name, room)
        else:
            entity = self._create_entity(ent_data, name, x, y)
            entities.append(entity)

    def populate(self, entities):
        ent_data = pd.read_csv('./data/entities.csv', index_col=0, header=0)
        for room in self.rooms:
            if isinstance(room, Hallway): continue
            prob_dist = ent_data.loc[:, 'prob']
            names = np.random.choice(ent_data.index, size=1, p=prob_dist)
            for name in names:
                if name == 'none': continue
                min_num = ent_data.loc[name, 'min_num']
                max_num = ent_data.loc[name, 'max_num']
                num = np.random.randint(min_num, max_num + 1)
                for _ in range(num):
                    self._place_ent(entities, ent_data, name, room)

    def gen_map(self, gridw, gridh, block_size, padding):
        grid = Grid(gridw, gridh, block_size)
        grid.divide_blocks(padding)
        grid.connect_blocks()
        gridx = (self.width - grid.tile_idx.shape[0]) // 2
        gridy = (self.height - grid.tile_idx.shape[1]) // 2
        self._gen_tiles(gridx, gridy, grid.tile_idx)
        self._find_rooms()
