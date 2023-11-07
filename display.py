from bearlibterminal import terminal as blt
import textwrap
import config
import time


class DisplayManager:
    def __init__(self, viewport, gui, animation_manager):
        self.viewport = viewport
        self.gui = gui
        self.animation_manager = animation_manager

    def render(self, game_map, entities, player):
        self.viewport.render(game_map, entities, player)
        self.gui.render()
        self.animation_manager.render()


#TODO: doors as entities with transparency over floor tile when open
#TODO: shadows as its own map layer that is displayed as np blt array
class Viewport:
    def __init__(self, x, y, w, h):
        self.x, self.y = x, y
        self.w, self.h = w // 4, h // 2
        self.x_off = self.w // 2
        self.y_off = self.h // 2
        self.reticule = None
        self.dark_tile = '[color=shade]\u2592[\color]'

    def render(self, game_map, entities, player):
        blt.layer(2)
        blt.clear_area(self.x, self.y, self.w*4, self.h*2)
        blt.layer(0)
        blt.clear_area(self.x, self.y, self.w*4, self.h*2)
        px, py = player.x, player.y
        for i in range(1, self.w):
            for j in range(1, self.h):
                x = px - self.x_off + i
                y = py - self.y_off + j
                if game_map.in_bounds(x, y) and game_map.explored[x, y]:
                    blt.print(i*4, j*2, game_map.tiles[x, y].tile)
                    if not game_map.visible[x, y]:
                        blt.layer(2)
                        blt.print(i*4, j*2, self.dark_tile)
                        blt.layer(0)
        blt.layer(1)
        blt.clear_area(self.x, self.y, self.w*4, self.h*2)
        for ent in entities:
            x = self.x_off - (px - ent.x)
            y = self.y_off - (py - ent.y)
            if game_map.visible[ent.x, ent.y]:
                blt.print(x*4, y*2, ent.icon)
        if self.reticule:
            self.reticule.render(self.x_off, self.y_off, px, py)
        blt.layer(0)


class Reticule:
    def __init__(self, x, y, max_range, area, color):
        self.x, self.y = x, y
        self.max_range = float(max_range)
        self.area = int(area)
        self.graphic = f'[color={color}][0xE000][/color]'

    def get_xys(self, x, y):
        xys = []
        for i in range(-self.area, self.area + 1):
            for j in range(-self.area, self.area + 1):
                if (i**2 + j**2) <= self.area**2:
                    xys.append(((x+i)*4, (y+j)*2))
        return xys
    

    def render(self, x_off, y_off, px, py):
        x = x_off - (px - self.x)
        y = y_off - (py - self.y)
        blt.composition(1)
        blt.print(x*4, y*2, self.graphic)
        if self.area > 0:
            for x, y in self.get_xys(x, y):
                blt.print(x, y, self.graphic)
        blt.composition(0)


class TargettingLine:
    def __init__(self, start_x, start_y, end_x, end_y, color):
        self.ox, self.oy = start_x + 0.5, start_y + 0.5
        self.ex, self.ey = end_x + 0.5, end_y + 0.5
        self.color = color

    def render(self):
        slope = (ex - ox) / (ey - oy)
        tiles = []
        while True:
            next_tile = ox


class Display:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def render(self):
        raise NotImplementedError()


class TargetDisplay(Display):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.target = None

    def render(self):
        blt.clear_area(self.x, self.y, 20, 1)
        target = self.target
        if target:
            name = target.name.capitalize()
            target_text = f'[color={target.color}]{name}[/color]'
            blt.print(self.x, self.y, f'[font=gui]{target_text}')


class BarDisplay(Display):
    def __init__(self, x, y, length, name, lcolor, dcolor, value, max_value):
        super().__init__(x, y)
        self.length = length
        self.max_length = length
        self.name = name
        self.value = value
        self.max_value = max_value
        self.full_bar_tile = f'[font=gui][color={lcolor}]\u2588[/color]'
        self.empty_bar_tile = f'[font=gui][color={dcolor}]\u2588[/color]'

    def update(self, value, max_value):
        self.max_value = max_value
        self.value = value
        if self.max_value == 0:
            self.length = 0
        else:
            self.length = int((self.value / self.max_value) * self.max_length)
        #self.text = f'{self.name}: {self.value} / {self.max_value}'

    def render(self):
        blt.clear_area(self.x, self.y, self.max_length, 2)
        if self.max_value > 0:
            blt.print(self.x, self.y, f'[font=bold_gui]{self.name}')
            for i in range(self.max_length):
                if i < self.length:
                    blt.print(self.x+i, self.y+1, self.full_bar_tile)
                else:
                    blt.print(self.x+i, self.y+1, self.empty_bar_tile)


class LogDisplay(Display):
    def __init__(self, x, y, w, h):
        super().__init__(x, y)
        self.orig_y = y
        self.w, self.h = w, h
        self.max_h = y + h
        self.msgs = []
        self.repeat = 0
        self.max_l = self.w - 5

    def _wrap_msg(self, msg):
        msg_len = len(msg)
        if msg_len > self.max_l:
            num_chunks = msg_len // self.max_l
            wrapped_msg = []
            for i in range(0, num_chunks + 1):
                wrapped_msg.append(msg[i*self.max_l: (i+1)*self.max_l])
            return wrapped_msg
        else:
            return [msg]

    def add_message(self, msg):
        if self.msgs and self.msgs[-1][:len(msg)] == msg:
            self.repeat += 1
            last_msg = self.msgs[-1][:len(msg)]
            last_msg += (f' x{self.repeat + 1}').ljust(5)
            self.msgs[-1] = last_msg
        else:
            self.msgs.append(msg)
            self.repeat = 0

    def render(self):
        self.y = self.orig_y
        blt.clear_area(self.x, self.y, self.w, self.h)
        wrapped_msgs = []
        for msg in self.msgs[-self.h:]:
            wrapped_msgs += self._wrap_msg(msg)
        wrapped_msgs = wrapped_msgs[-self.h:]
        for msg in wrapped_msgs:
            blt.print(self.x, self.y, f'[font=gui]{msg}')
            self.y += 1


class MenuDisplay(Display):
    def __init__(self, x, y, w, h, menu_title, menu_items):
        super().__init__(x, y)
        self.orig_y = y
        self.w, self.h = w, h
        self.menu_title = menu_title
        self.menu_items = menu_items
        self.border_tile = '[font=gui][color=menu_border]\u2588[/color]'

    def _render_border(self):
        blt.print(self.x, self.y, self.border_tile * (self.w + 1))
        for y in range(self.h - 2):
            blt.print(self.x, self.y + y + 1, self.border_tile * 2)
            blt.print(self.x + self.w - 1, self.y + y + 1, self.border_tile * 2)
        blt.print(self.x, self.y + self.h - 1, self.border_tile * (self.w + 1))

    def render(self):
        self.y = self.orig_y
        blt.clear_area(self.x - 1, self.y, self.w, self.h)
        blt.layer(1)
        blt.clear_area(self.x - 1, self.y, self.w, self.h)
        blt.layer(2)
        blt.clear_area(self.x - 1, self.y, self.w, self.h)
        blt.layer(0)
        self._render_border()
        self.y += 1
        blt.print(self.x + 2, self.y, f'[font=gui]{self.menu_title}')
        self.y += 1
        menu_idx = list(map(chr, range(97, 123)))
        for item in self.menu_items:
            blt.print(self.x + 2, self.y, f'[font=gui]{item}')
            self.y += 1


class GUI:
    def __init__(self, hp, max_hp, shields_hp, max_shields_hp):
        hpx = config.SCREEN_WIDTH - config.SIDE_PANEL_WIDTH
        hpy = 1
        logx = 2
        logy = config.SCREEN_HEIGHT - config.VERT_PANEL_HEIGHT
        self.hp_bar = BarDisplay(hpx, hpy, 20, 'Health', 'dark red',
                                 'darker red', hp, max_hp)
        self.shields_bar = BarDisplay(hpx, hpy + 3, 20, 'Shields',
                                      'light blue', 'darker blue',
                                      shields_hp, max_shields_hp)
        self.log = LogDisplay(logx, logy, hpx - 1, 5)
        self.menus = []
        self.target_display = TargetDisplay(hpx, config.TARGETY)
        self.show_fps = False
        self.last_time = time.time()

    def render(self):
        self.hp_bar.render()
        self.shields_bar.render()
        self.log.render()
        self.target_display.render()
        if self.menus:
            for menu in self.menus:
                menu.render()
        if self.show_fps:
            blt.clear_area(1, 1, 8, 1)
            fps = 1 // (time.time() - self.last_time)
            blt.print(1, 1, f'[font=gui]fps: {fps}')
            self.last_time = time.time()

    def update(self, player):
        self.hp_bar.update(player.combat.hit_points.hp,
                           player.combat.hit_points.max_hp)
        self.shields_bar.update(player.combat.shields.hp,
                                player.combat.shields.max_hp)
