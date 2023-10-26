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
        self.items = { chr(x): None for x in range(ord('a'), ord('z')+1) }
        self.next_slot = 'a'

    def pickup(self, item):
        self.items[self.next_slot] = item
        free_slots = [x for x in self.items.keys() if self.items[x] == None]
        free_slots.sort()
        self.next_slot = free_slots[0]

    def drop(self, item):
        for key, value in self.items.items():
            if value == item:
                slot = key
        self.items[slot] = None
        if ord(slot) < ord(self.next_slot): self.next_slot = slot

    def is_full(self):
        if self.size > len([k for k in self.items.keys() if self.items[k]]):
            return False
        else:
            return True


class Equipment:
    def __init__(self, weapon, armor, shields):
        self.weapon_slot = weapon
        self.armor_slot = armor
        self.shields_slot = shields

    def items(self):
        return [self.weapon_slot, self.armor_slot, self.shields_slot]

    def get_item_in_slot(self, slot):
        if slot == 'weapon':
            return self.weapon_slot
        elif slot == 'amor':
            return self.armor_slot
        elif slot == 'shields':
            return self.shields_slot

    def equip_to_slot(self, slot, item):
        if slot == 'weapon':
            self.weapon_slot = item
        elif slot == 'amor':
            self.armor_slot = item
        elif slot == 'shields':
            self.shields_slot = item
            self.entity.combat.shields.update()

    def unequip_from_slot(self, slot):
        if slot == 'weapon':
            self.weapon_slot = None
        elif slot == 'amor':
            self.armor_slot = None
        elif slot == 'shields':
            self.shields_slot = None
            self.entity.combat.shields.update()


class Shields:
    def __init__(self, hp, charge_rate, charge_delay):
        self.hp = 0
        self.base_max_hp = hp
        self.base_charge_rate = charge_rate
        self.base_charge_delay = charge_delay
        self.time_until_charge = charge_delay

    def take_hit(self, dam):
        self.time_until_charge = self.charge_delay + 1
        breakthrough = dam - self.hp
        self.hp -= dam
        if self.hp <= 0: self.hp = 0
        return breakthrough

    def charge(self):
        if self.time_until_charge == 0:
            self.hp += self.charge_rate
            if self.hp > self.max_hp:
                self.hp = self.max_hp
        else:
            self.time_until_charge -= 1

    def update(self):
        shp_bonus, scr_bonus, scd_bonus = 0, 0, 0
        for item in self.entity.equipment.items():
            if item is not None:
                shp_bonus += item.shp_bonus
                scr_bonus += item.scr_bonus
                scd_bonus += item.scd_bonus
        self.hp = 0
        self.max_hp = self.base_max_hp + shp_bonus
        self.charge_rate = self.base_charge_rate + scr_bonus
        self.charge_delay = self.base_charge_delay + scd_bonus
        self.time_until_charge = self.charge_delay + 1
