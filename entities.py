import helper_functions as hf
import numpy as np
import pandas as pd


class Entity:
    def __init__(self, name, x, y, char, color, graphic, blocking,
                 render_order):
        self.name = name
        self.x, self.y = x, y
        self.char = char
        self.color = color
        self.icon = f'[color={color}]{char}'
        if not pd.isnull(graphic):
            self.icon = graphic
        self.blocking = blocking
        self.render_order = render_order
        self.target = None

    def render(self, blt):
        blt.print(self.x*4, self.y*2, self.icon)

    def get_stats(self):
        return [f'This is a nice looking {self.name}']


class Actor(Entity):
    def __init__(self, name, x, y, char, color, graphic, combat, ai,
                 fov_radius, inventory, equipment, attributes, skills,
                 corpse_graphic):
        super().__init__(name, x, y, char, color, graphic, blocking=True,
                         render_order=0)
        self.combat = combat
        self.ai = ai
        self.fov_radius = fov_radius
        self.inventory = inventory
        self.equipment = equipment
        self.attributes = attributes
        self.skills = skills
        self.corpse_graphic = corpse_graphic

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def is_alive(self):
        return True if self.combat.hit_points.hp > 0 else False

    def die(self):
        self.name = f'{self.name} corpse'
        self.char = '%'
        self.color = 'dark red'
        if self.corpse_graphic:
            self.icon = self.corpse_graphic
        else:
            self.icon = '[color=dark red]%'
        self.blocking = False
        self.ai = None
        self.render_order = 2


class Item(Entity):    
    def __init__(self, name, x, y, char, color, graphic):
        super().__init__(name, x, y, char, color, graphic, blocking=False,
                         render_order=1)
        self.ai = None
        self.owner = None


class Consumable(Item):
    def __init__(self, name, x, y, char, color, graphic, verb):
        super().__init__(name, x, y, char, color, graphic)
        self.verb = verb

    def use(self):
        raise NotImplementedError()


class InjectedConsumable(Consumable):
    def __init__(self, name, x, y, char, color, graphic, amount, verb):
        super().__init__(name, x, y, char, color, graphic, verb)
        self.rolls, self.max_amount = hf.parse_dice(amount)

    def use(self):
        amount = np.sum(np.random.randint(1, self.max_amount + 1, self.rolls))
        self.owner.combat.hit_points.heal(amount)


class ThrownConsumable(Consumable):
    def __init__(self, name, x, y, char, color, graphic, damage, damage_type,
                 max_range, area, verb):
        super().__init__(name, x, y, char, color, graphic, verb)
        self.rolls, self.max_damage = hf.parse_dice(damage)
        self.damage_type = damage_type
        self.max_range = float(max_range)
        self.area = int(area)

    def roll_damage(self):
        return np.sum(np.random.randint(1, self.max_damage + 1, self.rolls))


class Equippable(Item):
    def __init__(self, name, x, y, char, color, graphic, att_type, max_range,
                 area, damage, damage_type, shp_bonus, scr_bonus, scd_bonus,
                 slot_type):
        super().__init__(name, x, y, char, color, graphic)
        self.att_type = att_type
        self.max_range = float(max_range)
        if not pd.isnull(area):
            self.area = int(area)
        else:
            self.area = None
        self.damage = damage
        self.damage_type = damage_type
        self.shp_bonus = shp_bonus
        self.scr_bonus = scr_bonus
        self.scd_bonus = scd_bonus
        self.slot_type = slot_type
        self.equipped = False
