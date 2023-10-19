from bearlibterminal import terminal as blt
import config


class DisplayBar:
    def __init__(self, x, y, length, name, color, value, max_value):
        self.x, self.y = x, y
        self.length = length
        self.max_length = length
        self.name = name
        self.value = value
        self.max_value = max_value
        self.full_bar_tile = f'[color=darker {color}]\u2588[/color]'
        self.empty_bar_tile = f'[color=darkest {color}]\u2588[/color]'
        self.bg = ' ' * self.length

    def update(self, value):
        self.value = value
        self.length = int((self.value / self.max_value) * self.max_length)
        #self.text = f'{self.name}: {self.value} / {self.max_value}'

    def render(self):
        blt.print(self.x, self.y, self.bg)
        blt.print(self.x, self.y, self.name)
        for i in range(self.max_length):
            if i < self.length:
                blt.print(self.x+i, self.y+1, self.full_bar_tile)
            else:
                blt.print(self.x+i, self.y+1, self.empty_bar_tile)


class DisplayLog:
    def __init__(self, x, y, w, h):
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.max_h = y + h
        self.new_msgs, self.old_msgs = [], []

    def update(self, msgs):
        self.new_msgs = msgs

    def render(self):
        for msg in self.new_msgs:
            if self.y == self.max_h:
                self.y -= self.h
                blt.clear_area(self.x, self.y, self.w, self.h)
                for i in range(self.h - 1):
                    blt.print(self.x, self.y, self.old_msgs[-self.h + i + 1])
                    self.y += 1
                blt.print(self.x, self.y, msg)
            else:
                blt.print(self.x, self.y, msg)
            self.old_msgs.append(msg)
            self.y += 1
        self.new_msgs = []
        

class GUI:
    def __init__(self, hp, max_hp):
        hpx = config.SCREEN_WIDTH - config.SIDE_PANEL_WIDTH
        hpy = 1
        logx = 2
        logy = config.SCREEN_HEIGHT - config.VERT_PANEL_HEIGHT
        self.hp_bar = DisplayBar(hpx, hpy, 20, 'Health', 'red', hp, max_hp)
        #self.shields_bar = DisplayBar(hpx, hpy, 20, 'shields', 'blue', 
        #                              shields, max_shields)
        self.log = DisplayLog(logx, logy, 100, 5)

    def render(self):
        self.hp_bar.render()
        self.log.render()

    def update(self, player, msgs):
        self.hp_bar.update(player.combat.hp)
        self.log.update(msgs)
        #self.shields_bar.update(player.combat.shields)
