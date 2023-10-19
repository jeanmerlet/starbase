import numpy as np


class FieldOfView:
    # multipliers for transforming coordinates to other octants
    MULT = np.array([[1,  0,  0,  1, -1,  0,  0, -1],
                     [0,  1,  1,  0,  0, -1, -1,  0],
                     [0,  1, -1,  0,  0, -1,  1,  0],
                     [1,  0,  0, -1, -1,  0,  0,  1]], dtype=int)

    def __init__(self, opaque):
        self.opaque = opaque
        self.max_x = opaque.shape[0] - 1
        self.max_y = opaque.shape[1] - 1

    def do_fov(self, origin, visible):
        x = origin.x
        y = origin.y
        self._light(x, y, visible)
        radius = origin.fov_radius
        for octant in range(8):
            self._cast_light(visible, x, y, radius, 1, 1.0, 0.0,
                             self.MULT[0, octant], self.MULT[1, octant],
                             self.MULT[2, octant], self.MULT[3, octant])

    def _cast_light(self, visible, ox, oy, radius, row,
                    start, end, xx, xy, yx, yy):
        if start < end:
            return

        radius_sq = radius**2
        for j in range(row, radius+1):
            out_of_bounds = False
            blocked = False
            dx = -j - 1
            dy = -j
            while dx <= 0:
                dx += 1
                X = ox + dx * xx + dy * xy
                Y = oy + dx * yx + dy * yy
                # out of bounds check
                if X < 0 or X > self.max_x or Y < 0 or Y > self.max_y:
                    continue
                l_slope = (dx - 0.5)/(dy + 0.5)
                r_slope = (dx + 0.5)/(dy - 0.5)
                if start < r_slope:
                    continue
                elif end > l_slope:
                    break
                else:
                    if dx**2 + dy**2 < radius_sq:
                        self._light(X, Y, visible)
                    if blocked:
                        if self.opaque[X, Y]:
                            new_start = r_slope
                            continue
                        else:
                            blocked = False
                            start = new_start
                    else:
                        if self.opaque[X, Y] and j < radius:
                            blocked = True
                            self._cast_light(visible, ox, oy, radius, j+1,
                                             start, l_slope, xx, xy, yx, yy)
                            new_start = r_slope
            if blocked:
                break

    def _light(self, x, y, visible):
        visible[x, y] = True
