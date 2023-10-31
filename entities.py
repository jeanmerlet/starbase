class Entity:
    def __init__(self, name, x, y, char, color, blocking, render_order):
        self.name = name
        self.x, self.y = x, y
        self.char = char
        self.color = color
        self.icon = f'[color={color}]{char}'
        self.blocking = blocking
        self.render_order = render_order

    def render(self, blt):
        blt.print(self.x, self.y, self.icon)

class Actor(Entity):
    def __init__(self, name, x, y, char, color, blocking, combat, ai,
                 fov_radius, inventory, equipment):
        super().__init__(name, x, y, char, color, blocking, render_order=0)
        self.combat = combat
        self.ai = ai
        self.fov_radius = fov_radius
        self.inventory = inventory
        self.equipment = equipment

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def die(self):
        self.name = f'{self.name} corpse'
        self.char = '%'
        self.color = 'dark red'
        self.icon = '[color=dark red]%'
        self.blocking = False
        self.ai = None
        self.render_order = 2


class Item(Entity):    
    def __init__(self, name, x, y, char, color, blocking):
        super().__init__(name, x, y, char, color, blocking, render_order=1)
        self.ai = None

    def get_stats(self):
        return [f'This is a nice looking {self.name}']


class Consumable:
    def get_action(self, consumer):
        return ItemAction(consumer, self.entity)

    def activate(self, action):
        raise NotImplementedError()


class HealingConsumable(Consumable):
    def __init__(self, amount):
        self.amount = amount

    def activate(self, action):
        pass


class Equippable(Item):
    def __init__(self, name, x, y, char, color, blocking, equip_time,
                 armor_bonus, def_bonus, att_bonus, dam_bonus, shp_bonus,
                 scr_bonus, scd_bonus, slot_type):
        super().__init__(name, x, y, char, color, blocking)
        self.equip_time = equip_time
        self.armor_bonus = armor_bonus
        self.def_bonus = def_bonus
        self.att_bonus = att_bonus
        self.dam_bonus = dam_bonus
        self.shp_bonus = shp_bonus
        self.scr_bonus = scr_bonus
        self.scd_bonus = scd_bonus
        self.slot_type = slot_type
        self.equipped = False
