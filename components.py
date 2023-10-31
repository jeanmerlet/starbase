class Combat:
    def __init__(self, hit_points, base_armor, shields, att):
        self.hit_points = hit_points
        self.base_armor = base_armor
        self.armor_bonus = 0
        self.shields = shields
        self.att = att

    def armor(self):
        return self.base_armor + self.armor_bonus

    def update_stats(self, equipment_items):
        self.shields.update(equipment_items)

    def update(self):
        self.shields.charge()
        self.hit_points.regen()


class HitPoints:
    def __init__(self, hp, regen_rate):
        self.hp = hp
        self.max_hp = hp
        self.regen_rate = regen_rate

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp: self.hp = self.max_hp

    def take_damage(self, amount):
        self.hp -= amount

    def regen(self):
        self.heal(self.regen_rate)


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
        self.slots = {
            'weapon': weapon,
            'armor': armor,
            'shields': shields,
        }

    def items(self):
        return self.slots.values()

    def get_item_in_slot(self, slot):
        return self.slots[slot]

    def update_entity_stats(self):
        self.entity.combat.update_stats(self.items())

    def equip_to_slot(self, slot, item):
        self.slots[slot] = item
        self.update_entity_stats()

    def unequip_from_slot(self, slot):
        self.slots[slot] = None
        self.update_entity_stats()


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

    def update(self, equipment_items):
        shp_bonus, scr_bonus, scd_bonus = 0, 0, 0
        for item in equipment_items:
            if item is not None:
                shp_bonus += item.shp_bonus
                scr_bonus += item.scr_bonus
                scd_bonus += item.scd_bonus
        self.hp = 0
        self.max_hp = self.base_max_hp + shp_bonus
        self.charge_rate = self.base_charge_rate + scr_bonus
        self.charge_delay = self.base_charge_delay + scd_bonus
        self.time_until_charge = self.charge_delay + 1
