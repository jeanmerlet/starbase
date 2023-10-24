from actions import ItemAction


class Combat:
    def __init__(self, hp, base_armor, shields, att):
        self.hp = hp
        self.max_hp = hp
        self.base_armor = base_armor
        self.armor_bonus = 0
        self.shields = shields
        self.att = att

    def set_hp(self, value):
        self.hp = min(value, self.max_hp)

    def armor(self):
        return self.base_armor + self.armor_bonus

    def is_alive(self):
        return True if self.hp > 0 else False


class Inventory:
    def __init__(self):
        self.size = 26
        self.items = []

    def pickup(self, item):
        self.items.append(item)

    def drop(self, item):
        self.items.remove(item)

    def is_full(self):
        if self.size > len(self.items):
            return False
        else:
            return True


class Equipment:
    def __init__(self, weapon, armor, shields):
        self.weapon = weapon
        self.armor = armor
        self.shields = shields

    def equip_to_slot(self, slot, item):
        if slot is not None:
            unequip_from_slot(slot, item)
        slot = item

    def unequip_from_slot(self, slot):
        slot.item = None


class Shields:
    def __init__(self, hp, charge_rate, charge_delay):
        self.hp = 0
        self.max_hp = hp
        self.charge_rate = charge_rate
        self.charge_delay = charge_delay
        self.time_until_charge = charge_delay

    def take_hit(self, dam):
        self.time_until_charge = self.charge_delay + 1
        breakthrough = dam - self.hp
        self.hp -= dam
        if self.hp <= 0: self.hp = 0
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


