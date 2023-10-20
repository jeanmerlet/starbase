from actions import ItemAction


class Combat:
    def __init__(self, hp, armor, att):
        self.hp = hp
        self.max_hp = hp
        #self.shields = shields
        #self.max_shields = shields
        #self.charge_delay = charge_delay
        #self.base_armor = armor
        self.armor = armor
        self.att = att

    def set_hp(self, value):
        self.hp = min(value, self.max_hp)

    def set_shields(self, value):
        pass
        #self.shields = min(value, self.max_shields)
        #if self.shields <= 0:
        #    self.shields.broken = True

    def is_alive(self):
        return True if self.hp > 0 else False


class Consumable:
    def get_action(self, consumer):
        return ItemAction(consumer, self.entity)

    def activate(self, action)
        raise NotImplementedError()


class HealingConsumable(Consumable):
    def __init__(self, amount):
        self.amount = amount

    def activate(self, action):
        pass
