from bearlibterminal import terminal as blt
import numpy as np
from procgen import Grid, RectRoom
from tiles import *

TILE_ID = {
    0: Wall(),
    1: Floor(),
    2: ClosedDoor()
}

class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.ctx = width // 2
        self.cty = height // 2

    def in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self. height

    def render(self):
        for x in range(self.width):
            for y in range(self.height):
                blt.print(x, y, self.tiles[x, y].icon)

    def is_adjacent(self, x1y1_coords, x2y2_coords):
        x1, y1 = x1y1_coords
        x2, y2 = x2y2_coords
        if abs(x1-x2) <= 1 and abs(y1-y2) <= 1:
            return True
        return False

    def _convert_grid_idx_to_tiles(self, x1, x2, y1, y2, grid_idx):
        for x in range(x1, x2):
            for y in range(y1, y2):
                #print(grid_idx[x - x1, y - y1])
                self.tiles[x, y] = TILE_ID[grid_idx[x - x1, y - y1]]

    def _gen_tiles(self, gridx, gridy, grid_idx):
        self.tiles = np.empty((self.width, self.height), dtype=object)
        for x in range(self.width):
            for y in range(self.height):
                self.tiles[x, y] = Space()
        x1 = gridx
        y1 = gridy
        x2 = gridx + grid_idx.shape[0]
        y2 = gridy + grid_idx.shape[1]
        self._convert_grid_idx_to_tiles(x1, x2, y1, y2, grid_idx)

    def gen_map(self, gridw, gridh, block_size, padding):
        grid = Grid(gridw, gridh, block_size)
        grid.divide_blocks(padding)
        gridx = (self.width - grid.tile_idx.shape[0]) // 2
        gridy = (self.height - grid.tile_idx.shape[1]) // 2
        self._gen_tiles(gridx, gridy, grid.tile_idx)
