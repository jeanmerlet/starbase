import numpy as np


class Ellipse:
    def __init__(self, x, y, rx, ry, rt):
        self.x = x
        self.y = y
        self.rx = rx
        self.ry = ry
        self.rt = rt

    def coords(self):
        pi_range = np.linspace(0, 2*np.pi, 1000)
        coords = []
        for t in pi_range:
            x = round((self.rx * np.cos(t) * np.cos(self.rt))
                - (self.ry * np.sin(t) * np.sin(self.rt)) + self.x)
            y = round((self.rx * np.cos(t) * np.sin(self.rt))
                + (self.ry * np.sin(t) * np.cos(self.rt)) + self.y)
            if (x, y) not in coords: coords.append((x, y))
        return coords


class RectRoom:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        if self.x2 < self.x1:
            self.x1, self.x2 = self.x2, self.x1
        if self.y2 < self.y1:
            self.y1, self.y2 = self.y2, self.y1

    def inner(self):
        return slice(self.x1+1, self.x2), slice(self.y1+1, self.y2)


class Hallway(RectRoom):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(x1, y1, x2, y2)


class Block:
    def __init__(self, x1, y1, x2, y2, div_prob, min_area, padding,
                 door_prob, tile_idx=None):
        """Grid blocks or subblocks.
        area: inner (floor) area
        tile index:
        0 - wall
        1 - floor
        2 - door
        3 - broken door
        """
        self.x1, self.x2 = x1, x2
        self.y1, self.y2 = y1, y2
        self.w = abs(x1 - x2) + 1
        self.h = abs(y1 - y2) + 1
        self.area = (self.w - 2) * (self.h - 2)
        if tile_idx is None:
            self.tile_idx = np.ones((self.w, self.h), dtype=int)
        else:
            self.tile_idx = tile_idx
        self.div_prob = div_prob
        self.min_area = min_area
        self.padding = padding
        self.door_prob = door_prob
        self.num_div = 3
        self._add_walls()
        self._add_doors()
        self._divide()

    def _add_walls(self):
        self.tile_idx[self.x1:self.x2+1, self.y1] = 0
        self.tile_idx[self.x1:self.x2+1, self.y2] = 0
        self.tile_idx[self.x1, self.y1:self.y2+1] = 0
        self.tile_idx[self.x2, self.y1:self.y2+1] = 0

    def _add_doors(self):
        # exclude corners
        self._add_door(slice(self.x1+1, self.x2), self.y1)
        self._add_door(slice(self.x1+1, self.x2), self.y2)
        self._add_door(self.x1, slice(self.y1+1, self.y2))
        self._add_door(self.x2, slice(self.y1+1, self.y2))

    def _add_door(self, slice_x, slice_y):
        wall = self.tile_idx[slice_x, slice_y]
        if np.random.rand() < self.door_prob:
            wall[np.random.randint(len(wall))] = 2
        else:
            wall[np.random.randint(len(wall))] = 3

    def _divide(self):
        """Recursively divide the block based on parameters."""
        if (self.area >= self.min_area and 
            np.random.rand() < self.div_prob and
            self.w > 4 and self.h > 4):
            divx, divy = self._gen_div_xy()
            div_angles = self._gen_div_angles()
            self._create_subblock(divx, divy, div_angles)

    def _gen_div_xy(self):
        x1, x2 = self.x1 + 1 + self.padding, self.x2 - self.padding
        y1, y2 = self.y1 + 1 + self.padding, self.y2 - self.padding
        x = np.random.randint(x1, x2)
        y = np.random.randint(y1, y2)
        return x, y

    def _gen_div_angles(self):
        angles = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        idx = np.random.choice(len(angles), size=self.num_div, replace=False)
        div_angles = [angles[x] for x in idx]
        return div_angles

    def _create_subblock(self, divx, divy, angles):
        """This assumes 3 angles."""
        if (-1, 0) in angles and (1, 0) in angles:
            if (0, -1) in angles:
                corner_pairs = [(self.x1, self.y1, divx, divy),
                                (divx, self.y1, self.x2, divy),
                                (self.x1, divy, self.x2, self.y2)]
            else:
                corner_pairs = [(self.x1, self.y1, self.x2, divy),
                                (self.x1, divy, divx, self.y2),
                                (divx, divy, self.x2, self.y2)]
        else:
            if (-1, 0) in angles:
                corner_pairs = [(self.x1, self.y1, divx, divy),
                                (divx, self.y1, self.x2, self.y2),
                                (self.x1, divy, divx, self.y2)]
            else:
                corner_pairs = [(self.x1, self.y1, divx, self.y2),
                                (divx, self.y1, self.x2, divy),
                                (divx, divy, self.x2, self.y2)]
        for corner_pair in corner_pairs: 
            Block(*corner_pair, self.div_prob, self.min_area, self.padding,
                     self.door_prob, self.tile_idx)


class Grid:
    def __init__(self, w, h, block_size):
        self.w = w
        self.h = h
        self.block_size = block_size
        self.num_blocks_x = w // block_size
        self.num_blocks_y = h // block_size
        tiles_w = (block_size - 1) * self.num_blocks_x + 1
        tiles_h = (block_size - 1) * self.num_blocks_y + 1
        self.tile_idx = np.zeros((tiles_w, tiles_h), dtype=int)

    def create_blocks(self):
        for x in range(self.num_blocks_x):
            for y in range(self.num_blocks_y):
                x1, y1 = 0, 0
                x2, y2 = self.block_size - 1, self.block_size - 1
                if np.random.rand() < 0.2:
                    min_area = 256
                    padding = 2
                    div_prob = 0.9
                else:
                    min_area = 64
                    padding = 1
                    div_prob = 1
                door_prob = 0.7
                block = Block(x1, y1, x2, y2, div_prob, min_area, padding,
                              door_prob)
                self._add_block_to_tile_idx(x, y, block)

    def _add_block_to_tile_idx(self, x, y, block):
        x1 = x * self.block_size - x
        y1 = y * self.block_size - y
        x2 = (x + 1) * (self.block_size) - x
        y2 = (y + 1) * (self.block_size) - y
        self.tile_idx[x1: x2, y1: y2] = block.tile_idx
