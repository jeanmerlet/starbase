import numpy as np
import helper_functions as hf


class Level:
    def __init__(self, level, max_level, xp, nl_xp, xp_mult):
        self.level = level
        self.max_level = max_level
        self.xp = xp
        self.nl_xp = nl_xp
        self.xp_mult = xp_mult

    def _level(self):
        self.level += 1
        self.nl_xp += self.nl_xp * xp_mult

    def add_xp(self, xp):
        if self.level < self.max_level:
            self.xp += xp
            if self.xp >= self.nl_xp:
                self._level()
        else:
            xp = 'max'


class Combat:
    def __init__(self, hit_points, shields, melee_attacks, ranged_attacks):
        self.hit_points = hit_points
        self.shields = shields
        self.base_melee_attacks = melee_attacks
        self.base_ranged_attacks = ranged_attacks

    def defense(self):
        return self.entity.skills['evasion'].get_value()

    def _update_weapon_attacks(self, equipment_items):
        weapon = equipment_items['weapon']
        if weapon is None:
            self.melee_attacks = self.base_melee_attacks
            self.ranged_attacks = self.base_ranged_attacks
        else:
            name = weapon.name
            damage = weapon.damage
            damage_type = weapon.damage_type
            max_range = weapon.max_range
            area = weapon.area
            if weapon.att_type == 'melee':
                self.melee_attacks = [MeleeAttack(name, damage, damage_type,
                                                  max_range, area)]
                self.ranged_attacks = self.base_ranged_attacks
            else:
                self.ranged_attacks = [RangedAttack(name, damage, damage_type,
                                                    max_range, area)]
                self.melee_attacks = self.base_melee_attacks
        for i, attack in enumerate(self.melee_attacks):
            attack.combat = self
            attack.update(i, equipment_items)
        for i, attack in enumerate(self.ranged_attacks):
            attack.combat = self
            attack.update(i, equipment_items)

    def update_equipment(self, equipment_items):
        self.shields.update(equipment_items)
        self._update_weapon_attacks(equipment_items)

    def tick(self):
        self.shields.charge()
        self.hit_points.regen()


class Attack:
    def __init__(self, name, damage, damage_type, max_range, area):
        self.name = name
        self.dice = damage
        self.num_dice, self.damage = hf.parse_dice(damage)
        self.damage_type = damage_type
        self.max_range = float(max_range)
        self.area = int(area)

    def roll_damage(self):
        rolls = np.random.randint(1, self.damage + 1, self.num_dice)
        damage = np.sum(rolls)
        return damage

    def update(self, attack_num, equipment_items):
        pass


class MeleeAttack(Attack):
    def __init__(self, name, damage, damage_type, max_range, area):
        super().__init__(name, damage, damage_type, max_range, area)

    def hit_chance(self):
        return self.combat.entity.skills['melee'].get_value()


class RangedAttack(Attack):
    def __init__(self, name, damage, damage_type, max_range, area):
        super().__init__(name, damage, damage_type, max_range, area)

    def hit_chance(self):
        return self.combat.entity.skills['ranged'].get_value()


class Skill:
    def __init__(self, name, value, attr1, attr1_mod, attr2, attr2_mod):
        self.name = name
        self.value = value
        self.attr1 = attr1
        self.attr1_mod = attr1_mod
        self.attr2 = attr2
        self.attr2_mod = attr2_mod

    def get_value(self):
        mod1 = self.entity.attributes[self.attr1] * self.attr1_mod
        mod2 = self.entity.attributes[self.attr2] * self.attr2_mod
        total = self.value + mod1 + mod2
        return total


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

    def reset_slots(self, slot):
        if ord(slot) < ord(self.next_slot): self.next_slot = slot

    def drop(self, item):
        for key, value in self.items.items():
            if value == item:
                slot = key
        self.items[slot] = None
        item.owner = None
        self.reset_slots(slot)

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
