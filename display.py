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


class GUI:
    def __init__(self, hp, max_hp):
        hp_x = config.SCREEN_WIDTH - config.SIDE_PANEL_WIDTH + 2
        hp_y = 1
        self.hp_bar = DisplayBar(hp_x, hp_y, 20, 'HP', 'red', hp, max_hp)

    def render(self):
        self.hp_bar.render()

    def update(self, player):
        self.hp_bar.update(player.combat.hp)
