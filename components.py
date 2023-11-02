import numpy as np
import helper_functions as hf


class Combat:
    def __init__(self, hit_points, shields, attacks):
        self.hit_points = hit_points
        self.shields = shields
        self.attacks = attacks

    def update_equipment(self, equipment_items):
        self.shields.update(equipment_items)
        for attack in self.attacks:
            attack.update(equipment_items)

    def tick(self):
        self.shields.charge()
        self.hit_points.regen()


class Attack:
    def __init__(self, name, damage, damage_type):
        self.base_name = name
        self.base_dice = damage
        self.base_num_dice, self.base_damage = hf.parse_dice(damage)
        self.base_damage_type = damage_type

    def roll_hit(self):
        pass

    def roll_damage(self):
        rolls = np.random.randint(1, self.damage + 1, self.num_dice)
        damage = np.sum(rolls)
        return damage

    def update(self, equipment_items):
        weapon = equipment_items['weapon']
        if weapon:
            self.name = weapon.name
            self.num_dice, self.damage = hf.parse_dice(weapon.damage)
            self.damage_type = weapon.damage_type
        else:
            self.name = self.base_name
            self.num_dice, self.damage = hf.parse_dice(self.base_dice)
            self.damage_type = self.base_damage_type


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
        item.owner = self.entity
        free_slots = [x for x in self.items.keys() if self.items[x] == None]
        free_slots.sort()
        self.next_slot = free_slots[0]

    def drop(self, item):
        for key, value in self.items.items():
            if value == item:
                slot = key
        self.items[slot] = None
        item.owner = None
        if ord(slot) < ord(self.next_slot): self.next_slot = slot

    def is_full(self):
        if self.size > len([k for k in self.items.keys() if self.items[k]]):
            return False
        else:
            return True

    def get_slot_from_item(self, item):
        slots = self.items.keys()
        return [slot for slot in slots if self.items[slot] == item][0]


class Equipment:
    def __init__(self, weapon, armor, shields):
        self.slots = {
            'weapon': weapon,
            'armor': armor,
            'shields': shields,
        }

    def items(self):
        return self.slots

    def get_item_in_slot(self, slot):
        return self.slots[slot]

    def update_actor_stats(self):
        self.entity.combat.update_equipment(self.items())

    def equip_to_slot(self, slot, item):
        self.slots[slot] = item
        item.equipped = True
        self.update_actor_stats()

    def unequip_from_slot(self, slot, item):
        self.slots[slot] = None
        item.equipped = False
        self.update_actor_stats()


class Shields:
    def __init__(self, hp, charge_rate, charge_delay):
        self.hp = 0
        self.base_max_hp = hp
        self.base_charge_rate = charge_rate
        self.base_charge_delay = charge_delay
        self.time_until_charge = charge_delay
        self.equipped_shield = None

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

    #TODO: fix the shield hp 0 logic
    def update(self, equipment_items):
        shp_bonus, scr_bonus, scd_bonus = 0, 0, 0
        for slot, item in equipment_items.items():
            if item is not None:
                shp_bonus += item.shp_bonus
                scr_bonus += item.scr_bonus
                scd_bonus += item.scd_bonus
        self.max_hp = self.base_max_hp + shp_bonus
        self.charge_rate = self.base_charge_rate + scr_bonus
        self.charge_delay = self.base_charge_delay + scd_bonus
        if equipment_items['shields']:
            if (self.equipped_shield is None
                or self.equipped_shield is not equipment_items['shields']):
                self.hp = 0
                self.time_until_charge = self.charge_delay + 1
                self.equipped_shield = equipment_items['shields']
