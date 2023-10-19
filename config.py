from bearlibterminal import terminal as blt


# terminal
SCREEN_WIDTH = 160
SCREEN_HEIGHT = 55

SIDE_PANEL_WIDTH = 24
VERT_PANEL_HEIGHT = 5

# map
MAP_WIDTH = 160
MAP_HEIGHT = 50
GRIDW = 100
GRIDH = 40
BLOCK_SIZE = 20


class TerminalSettings:
    def __init__(self):
        self._set_colors()

    def _set_colors(self):
        blt.set(f'window.size={SCREEN_WIDTH}x{SCREEN_HEIGHT}')
        blt.set('palette.blue = 0,102,204')
        blt.set('palette.l_stl = 160,160,160')
        blt.set('palette.d_stl = 32,32,32')
