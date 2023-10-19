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

    def update(self, value):
        self.value = int(value)
        self.length = int((self.value / self.max_value) * self.max_length)
        self.bg = ' ' * self.length
        self.text = f'{self.name}: {self.value} / {self.max_value}'

    def render(self):
        #blt.print(self.x, self.y, self.bg)
        #blt.print(self.x, self.y, self.text)
        for i in range(self.max_length):
            if i < self.length:
                blt.print(self.x+i, self.y+1, self.full_bar_tile)
            else:
                blt.print(self.x+i, self.y+1, self.empty_bar_tile)


class DisplayLog:
    def __init__(self, x, y, width, height):
        self.x, self.y = x, y
        self.max_h = y + height
        self.new_msgs, self.old_msgs = [], []

    def update(self, msgs):
        self.new_msgs = msgs

    def render(self):
        for msg in self.new_msgs:
            if self.y == self.max_h:
                pass
            else:
                blt.print(self.x, self.y, msg)
                self.old_msgs.append(msg)
                self.y += 1
        self.new_msgs = []
        

class GUI:
    def __init__(self, hp, max_hp):
        hpx = config.SCREEN_WIDTH - config.SIDE_PANEL_WIDTH + 2
        hpy = 1
        logx = 1
        logy = config.SCREEN_HEIGHT - config.VERT_PANEL_HEIGHT
        self.hp_bar = DisplayBar(hpx, hpy, 20, 'hp', 'red', hp, max_hp)
        #self.shields_bar = DisplayBar(hpx, hpy, 20, 'shields', 'blue', 
        #                              shields, max_shields)
        self.log = DisplayLog(logx, logy, 60, 5)

    def render(self):
        self.hp_bar.render()
        self.log.render()

    def update(self, player, msgs):
        self.hp_bar.update(player.combat.hp)
        self.log.update(msgs)
        #self.shields_bar.update(player.combat.shields)
