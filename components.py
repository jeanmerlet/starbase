from actions import ItemAction


class Combat:
    def __init__(self, hp, armor, shields, att):
        self.hp = hp
        self.max_hp = hp
        self.base_armor = armor
        self.armor = armor
        self.shields = shields
        self.att = att

    def set_hp(self, value):
        self.hp = min(value, self.max_hp)

    def is_alive(self):
        return True if self.hp > 0 else False


class Shields:
    def __init__(self, hp, charge_rate, charge_delay):
        self.hp = 0
        self.max_hp = hp
        self.charge_rate = charge_rate
        self.charge_delay = charge_delay
        self.time_until_charge = charge_delay

    def _break_shield(self):
        self.time_until_charge = self.charge_delay

    def take_hit(self, value):
        breakthrough = value - self.hp
        self.hp = min(0, max(value, self.max_hp))
        if self.hp == 0: self._break_shield()
        return breakthrough

    def charge(self):
        self.hp += self.charge_rate
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def update(self):
        if self.time_until_charge == 0:
            self.charge()
        else:
            self.time_until_charge -= 1


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
