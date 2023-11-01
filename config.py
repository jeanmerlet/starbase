from bearlibterminal import terminal as blt


# gui
SCREEN_WIDTH = 160
SCREEN_HEIGHT = 54

SIDE_PANEL_WIDTH = 22
VERT_PANEL_HEIGHT = 6

INVENTORY_WIDTH = 40
INVENTORY_HEIGHT = 29


# map
MAP_WIDTH = 138
MAP_HEIGHT = 48
GRIDW = 100
GRIDH = 40
BLOCK_SIZE = 20


# blt
def set_blt_settings():
    blt.set(f'window.size={SCREEN_WIDTH}x{SCREEN_HEIGHT}')
    blt.set('palette.blue = 0,102,204')
    blt.set('palette.l_stl = 160,160,160')
    blt.set('palette.d_stl = 32,32,32')
    blt.set('palette.menu_border = 0,76,153')
