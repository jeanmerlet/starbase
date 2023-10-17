from bearlibterminal import terminal as blt

class Entity:
    def __init__(self, x, y, char, color):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.icon = f'[color={color}]{char}'


class Actor(Entity):
    def __init__(self, x, y, char, color):
        super().__init__(x, y, char, color)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def render(self):
       blt.print(self.x, self.y, self.icon)
 
