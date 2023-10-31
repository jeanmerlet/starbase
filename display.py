from bearlibterminal import terminal as blt
import textwrap
import config


class Display:
    def __init__(self, x, y):
        self.x, self.y = x, y


class BarDisplay(Display):
    def __init__(self, x, y, length, name, lcolor, dcolor, value, max_value):
        super().__init__(x, y)
        self.length = length
        self.max_length = length
        self.name = name
        self.value = value
        self.max_value = max_value
        self.full_bar_tile = f'[color={lcolor}]\u2588[/color]'
        self.empty_bar_tile = f'[color={dcolor}]\u2588[/color]'

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
            blt.print(self.x, self.y, self.name)
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
            blt.print(self.x, self.y, msg)
            self.y += 1


class MenuDisplay(Display):
    def __init__(self, x, y, w, h, menu_title, menu_items):
        super().__init__(x, y)
        self.orig_y = y
        self.w, self.h = w, h
        self.menu_title = menu_title
        self.menu_items = menu_items
        self.border_tile = '[color=menu_border]\u2592[/color]'

    def _render_border(self):
        blt.print(self.x, self.y, self.border_tile * self.w)
        for y in range(self.h - 2):
            blt.print(self.x, self.y + y + 1, self.border_tile)
            blt.print(self.x + self.w - 1, self.y + y + 1, self.border_tile)
        blt.print(self.x, self.y + self.h - 1, self.border_tile * self.w)

    def render(self):
        self.y = self.orig_y
        blt.clear_area(self.x, self.y, self.w, self.h)
        self._render_border()
        self.y += 1
        blt.print(self.x + 2, self.y, self.menu_title)
        self.y += 1
        menu_idx = list(map(chr, range(97, 123)))
        for item in self.menu_items:
            blt.print(self.x + 2, self.y, item)
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

    def render(self):
        self.hp_bar.render()
        self.shields_bar.render()
        self.log.render()
        if self.menus:
            for menu in self.menus:
                menu.render()

    def update(self, player):
        self.hp_bar.update(player.combat.hp, player.combat.max_hp)
        self.shields_bar.update(player.combat.shields.hp,
                                player.combat.shields.max_hp)
