class Entity:
    def __init__(self, name, x, y, char, color, blocking, render_order):
        self.name = name
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.icon = f'[color={color}]{char}'
        self.blocking = blocking
        self.render_order = render_order

    def render(self, blt):
       blt.print(self.x, self.y, self.icon)


class Actor(Entity):
    def __init__(self, name, x, y, char, color, blocking, combat, ai,
                 fov_radius=None):
        super().__init__(name, x, y, char, color, blocking, render_order=0)
        self.combat = combat
        self.ai = ai
        self.fov_radius = fov_radius

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    
