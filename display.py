from bearlibterminal import terminal as blt
import textwrap
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
        self.orig_y = y
        self.w, self.h = w, h
        self.max_h = y + h
        self.new_msgs, self.old_msgs = [], []
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

    def update(self, msgs):
        new_msgs = []
        for msg in msgs:
            if self.old_msgs and self.old_msgs[-1][:len(msg)] == msg:
                self.repeat += 1
                old_msg = self.old_msgs[-1][:len(msg)]
                old_msg += (f' x{self.repeat}').ljust(5)
                self.old_msgs[-1] = old_msg
            else:
                new_msgs.append(msg)
                self.repeat = 0
        self.new_msgs = new_msgs

    def render(self):
        self.y = self.orig_y
        blt.clear_area(self.x, self.y, self.w, self.h)
        num_new_msgs = len(self.new_msgs)
        new_msgs = []
        for msg in self.new_msgs:
            new_msgs += self._wrap_msg(msg)
        new_msgs = new_msgs[-self.h:]
        n_lines = self.h - len(new_msgs)
        if n_lines > 0:
            old_msgs = []
            for msg in self.old_msgs[-n_lines:]:
                old_msgs += self._wrap_msg(msg)
            old_msgs = old_msgs[-n_lines:]
            msgs = old_msgs + new_msgs
        else:
            msgs = new_msgs
        for msg in msgs:
            blt.print(self.x, self.y, msg)
            self.y += 1
        self.old_msgs += self.new_msgs
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
        self.log = DisplayLog(logx, logy, hpx - 1, 5)

    def render(self):
        self.hp_bar.render()
        self.log.render()

    def update(self, player, msgs):
        self.hp_bar.update(player.combat.hp)
        self.log.update(msgs)
        #self.shields_bar.update(player.combat.shields)
