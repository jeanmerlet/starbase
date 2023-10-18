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

    def outer(self):
        return [
            [(x, self.y1-1) for x in range(self.x1-1, self.x2+1)],
            [(x, self.y2) for x in range(self.x1-1, self.x2+1)],
            [(self.x1-1, y) for y in range(self.y1-1, self.y2+1)],
            [(self.x2, y) for y in range(self.y1-1, self.y2+1)]
        ]


class Hallway(RectRoom):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(x1, y1, x2, y2)


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

    def _rooms(self, x, y, angles):
        # not needed, will do rooms in map
        rooms = []
        if (-1, 0) in angles and (1, 0) in angles:
            if (0, -1) in angles:
                rooms.append(RectRoom(0, 0, x, y))
                rooms.append(RectRoom(x, 0, self.s-1, y))
                rooms.append(RectRoom(0, y, self.s-1, self.s-1))
            if (0, 1) in angles:
                rooms.append(RectRoom(0, 0, self.s-1, y))
                rooms.append(RectRoom(0, y, x, self.s-1))
                rooms.append(RectRoom(x, y, self.s-1, self.s-1))
        if (0, -1) in angles and (0, 1) in angles:
            if (-1, 0) in angles:
                rooms.append(RectRoom(0, 0, x, y, dx, dy))
                rooms.append(RectRoom(0, y, x, self.s-1, dx, dy))
                rooms.append(RectRoom(x, 0, self.s-1, self.s-1))
            if (1, 0) in angles:
                rooms.append(RectRoom(0, 0, x, self.s-1, dx, dy))
                rooms.append(RectRoom(x, 0, self.s-1, y, dx, dy))
                rooms.append(RectRoom(x, y, self.s-1, self.s-1))
        return rooms

    def divide(self, padding):
        """Split block into rooms and hallways.
        The edge coords are all walls.

        padding: minimum number of tiles from a wall that 
                 a split point can be picked
        """
        splitx, splity = self._gen_split_xy(self.s, self.s, padding)
        split_angles = self._gen_split_angles()
        self._split(splitx, splity, split_angles)
        #rooms = self._rooms(splitx, splity, split_angles)
        #return rooms


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
        rooms = []
        for x in range(self.w):
            for y in range(self.h):
                block = Block(self.size)
                block.divide(padding)
                self._add_block_to_tile_idx(x, y, block)

    def connect_blocks(self):
        for x in range(0, self.w):
            v_wall_x = (x * self.size) - x
            h_wall_minx = (x * self.size) + 1 - x
            h_wall_maxx = (x * self.size) + self.size - x - 1
            for y in range(0, self.h):
                v_wall_miny = (y * self.size) + 1 - y
                v_wall_maxy = (y * self.size) + self.size - y - 1
                v_walls = [(v_wall_x, z) for z in range(v_wall_miny, v_wall_maxy)]
                num_doors = 2 if np.random.rand() < 0.25 else 1
                v_wall_idx = np.random.choice(len(v_walls), size=num_doors, replace=False)
                v_doors = [v_walls[idx] for idx in v_wall_idx]
                for door in v_doors:
                    if x == 0: break
                    self.tile_idx[door] = 2
                h_wall_y = (y * self.size) - y
                h_walls = [(z, h_wall_y) for z in range(h_wall_minx, h_wall_maxx)]
                num_doors = 2 if np.random.rand() < 0.25 else 1
                h_wall_idx = np.random.choice(len(h_walls), size=num_doors, replace=False)
                h_doors = [h_walls[idx] for idx in h_wall_idx]
                for door in h_doors:
                    if y == 0: break
                    self.tile_idx[door] = 2
