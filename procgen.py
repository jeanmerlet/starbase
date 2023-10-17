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
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
        if self.x2 < self.x1:
            self.x1, self.x2 = self.x2-1, self.x1+1
        if self.y2 < self.y1:
            self.y1, self.y2 = self.y2-1, self.y1+1

    def inner(self):
        return slice(self.x1, self.x2), slice(self.y1, self.y2)

    def outer(self):
        return [
            [(x, self.y1-1) for x in range(self.x1-1, self.x2+1)],
            [(x, self.y2) for x in range(self.x1-1, self.x2+1)],
            [(self.x1-1, y) for y in range(self.y1-1, self.y2+1)],
            [(self.x2, y) for y in range(self.y1-1, self.y2+1)]
        ]


class Hallway(RectRoom):
    def __init__(self):
        super().__init__()


class Block:
    def __init__(self, size):
        """Grid blocks.
        tile idx:
        0 - wall
        1 - floor
        2 - door
        """
        self.s = size
        self.tile_idx = np.ones((size, size), dtype=int)
        self._add_outer_walls()

    def _add_outer_walls(self):
        self.tile_idx[:, 0] = 0
        self.tile_idx[:, self.s - 1] = 0
        self.tile_idx[0, :] = 0
        self.tile_idx[self.s - 1, :] = 0

    def _gen_split_xy(self, w, h, padding):
        x = np.random.randint(1 + padding, w - padding - 1)
        y = np.random.randint(1 + padding, h - padding - 1)
        return x, y

    def _gen_split_angles(self, num_angles=3):
        angles = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        idx = np.random.choice(len(angles), size=num_angles, replace=False)
        split_angles = [angles[x] for x in idx]
        return split_angles

    def _add_inner_wall(self, x, y, angle):
        dest_xy = tuple(np.add((x, y), angle))
        walls = []
        while self.tile_idx[dest_xy] != 0:
            self.tile_idx[dest_xy] = 0
            walls.append(dest_xy)
            x, y = dest_xy
            dest_xy = tuple(np.add((x, y), angle))
        door_xy = walls[np.random.choice(len(walls))]
        self.tile_idx[door_xy] = 2

    def _split(self, splitx, splity, angles):
        self.tile_idx[splitx, splity] = 0
        for angle in angles:
            self._add_inner_wall(splitx, splity, angle)
            
    def divide(self, padding):
        """Split block into rooms and hallways.
        The edge coords are all walls.

        padding: minimum number of tiles from a wall that 
                 a split point can be picked
        """
        splitx, splity = self._gen_split_xy(self.s, self.s, padding)
        split_angles = self._gen_split_angles()
        self._split(splitx, splity, split_angles)


class Grid:
    def __init__(self, w, h, block_size):
        self.w = w
        self.h = h
        self.size = block_size
        total_w = (block_size * w) - (w - 1)
        total_h = (block_size * h) - (h - 1)
        self.tile_idx = np.zeros((total_w, total_h), dtype=int)

    def _add_block_to_tile_idx(self, x, y, block):
        x1, y1 = x * self.size, y * self.size
        x2, y2 = (x+1) * self.size, (y+1) * self.size
        if x > 0:
            x1 -= x
            x2 -= x
        if y > 0:
            y1 -= y
            y2 -= y
        self.tile_idx[x1: x2, y1: y2] = block.tile_idx

    def divide_blocks(self, padding):
        for x in range(self.w):
            for y in range(self.h):
                block = Block(self.size)
                block.divide(padding)
                self._add_block_to_tile_idx(x, y, block)

    def connect_blocks(self):
        pass






