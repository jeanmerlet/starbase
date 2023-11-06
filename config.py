from bearlibterminal import terminal as blt


# map
MAP_WIDTH = 100
MAP_HEIGHT = 100
GRIDW = 80
GRIDH = 80
BLOCK_SIZE = 20


# display
SCREEN_WIDTH = 160
SCREEN_HEIGHT = 54

VIEWPORT_WIDTH = 138
VIEWPORT_HEIGHT = 48

SIDE_PANEL_WIDTH = 22
VERT_PANEL_HEIGHT = 6

INVENTORY_WIDTH = 58
INVENTORY_HEIGHT = 29

TARGETY = 10


# blt
def set_blt_settings():
    blt.set(f'window.size={SCREEN_WIDTH}x{SCREEN_HEIGHT}')
    blt.set('window: cellsize=8x16')

    font = 'Saira'
    blt.set(f'font: ./fonts/{font}-Regular.ttf, size=24, spacing=4x2')
    blt.set(f'gui font: ./fonts/{font}-Regular.ttf, size=12')
    blt.set(f'bold_gui font: ./fonts/{font}-Bold.ttf, size=11')

    blt.set('0xE000: ./graphics/targetting.png, spacing=4x2')
    blt.set('0xE001: ./graphics/station_floor.png, spacing=4x2')
    blt.set('0xE002: ./graphics/station_wall.png, spacing=4x2')
    blt.set('0xE003: ./graphics/station_door_open.png, spacing=4x2')
    blt.set('0xE004: ./graphics/station_door_closed.png, spacing=4x2')
    blt.set('0xE005: ./graphics/basic_shield_belt.png, spacing=4x2')
    blt.set('0xE006: ./graphics/blaster.png, spacing=4x2')
    blt.set('0xE007: ./graphics/skitterling.png, spacing=4x2')

    blt.set('palette.shade = 200,0,0,0')
    blt.set('palette.blue = 0,102,204')
    blt.set('palette.l_stl = 160,160,160')
    blt.set('palette.d_stl = 32,32,32')
    blt.set('palette.menu_border = 0,76,153')
