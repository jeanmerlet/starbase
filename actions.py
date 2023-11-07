import config
from commands import *
from display import MenuDisplay, Reticule
from entities import Actor, Equippable, Consumable
from ai import HostileEnemy
from tiles import Door
import event_handlers as eh
import numpy as np


class Action:
    def __init__(self):
        self.time_units = 1000

    def perform(self, engine, entity):
        raise NotImplementedError()


class FPSToggle(Action):
    def __init__(self):
        self.time_units = 0

    def perform(self, engine, entity):
        engine.toggle_fps()


class QuitAction(Action):
    def perform(self, engine, entity):
        raise SystemExit()


class WaitAction(Action):
    def perform(self, engine, entity):
        pass


class DirectedAction(Action):
    def __init__(self, dx, dy):
        self.dx = dx
        self.dy = dy

    def perform(self, engine, entity):
        raise NotImplementedError()

    def _get_target_xy(self, entity):
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy
        return dest_x, dest_y


class MoveAction(DirectedAction):
    def __init__(self, dx, dy):
        super().__init__(dx, dy)
        self.time_units = 1000

    def perform(self, engine, entity):
        dest_x, dest_y = self._get_target_xy(entity)
        blocking_ent = engine.get_blocking_entity_at_xy(dest_x, dest_y)
        dest_tile = engine.game_map.tiles[dest_x, dest_y]
        if blocking_ent:
            msg = f'ERROR: {blocking_ent.name} blocking'
            engine.add_log_msg(msg)
        elif not engine.game_map.in_bounds(dest_x, dest_y):
            msg = 'ERROR: out of bounds!'
            engine.add_log_msg(msg)
        elif not dest_tile.walkable:
            if isinstance(dest_tile, Door):
                action = OpenDoorAction(self.dx, self.dy)
                engine.event_handler.actions.append(action)
                self.time_units = 0
                return
            else:
                msg = "You can't go there."
                engine.add_log_msg(msg)
        else:
            entity.move(self.dx, self.dy)


class OpenDoorAction(DirectedAction):
    def __init__(self, dx, dy):
        super().__init__(dx, dy)
        self.time_units = 1000

    def perform(self, engine, entity):
        dest_x, dest_y = self._get_target_xy(entity)
        door = engine.game_map.tiles[dest_x, dest_y]
        door.ai.open(engine)


class AttackAction(Action):
    def perform(self, engine, entity):
        raise NotImplementedError()

    def _check_for_death(self, engine, target):
        if not target.is_alive():
            if target is engine.player:
                engine.push_event_handler(eh.GameOverEventHandler())
                msg = 'You have DIED.'
                engine.add_log_msg(msg)
            else:
                msg = f'The {target.name} dies.'
                engine.add_log_msg(msg)
            target.die()

    def _get_damage(self, attack, entity, target):
        dam = attack.roll_damage()
        if target.combat.shields:
            dam = target.combat.shields.take_hit(dam)
        return dam

    def _roll_hit(self, attack, entity, target):
        hit_chance = attack.hit_chance() - target.combat.defense()
        roll = np.random.randint(101)
        if roll <= hit_chance: return True
        return False

    def _get_animation(self, attack, target, entity):
        animation_imgs = attack.animation_imgs
        ox, oy = entity.x, entity.y
        tx, ty = target.x, target.y

    #TODO: log text includes shields
    def _attack(self, attack, target, engine, entity):
        if not target.is_alive(): return
        if entity is engine.player:
            subj = 'You'
            obj = f'the {target.name}'
        else:
            subj = f'The {entity.name}'
            obj = 'you'
        if not self._roll_hit(attack, entity, target):
            verb = 'miss' if entity is engine.player else 'misses'
            msg = f'{subj} {verb} {obj}.'
            engine.add_log_msg(msg)
            return
        dam = self._get_damage(attack, entity, target)
        target.combat.hit_points.take_damage(dam)
        verb = 'hit' if entity is engine.player else 'hits'
        if dam > 0:
            msg = f'{subj} {verb} {obj} for {dam} damage.'
            engine.add_log_msg(msg)
        else:
            msg = f'{subj} {verb} {obj} but does no damage.'
            engine.add_log_msg(msg)
        self._check_for_death(engine, target)


class MeleeAction(DirectedAction, AttackAction):
    def __init__(self, dx, dy):
        DirectedAction.__init__(self, dx, dy)
        self.time_units = 1000

    def perform(self, engine, entity):
        dest_x, dest_y = self._get_target_xy(entity)
        target = engine.get_blocking_entity_at_xy(dest_x, dest_y)
        if target is None:
            msg = 'Nothing there.'
            engine.add_log_msg(msg)
        else:
            for attack in entity.combat.melee_attacks:
                self._attack(attack, target, engine, entity)


class RangedAction(AttackAction):
    def perform(self, engine, entity):
        target = entity.target
        for attack in entity.combat.ranged_attacks:
            self._attack(attack, target, engine, entity)
        animation = self._get_animation(attack, target, entity)
        engine.display_manager.animation_manager.animations.append(animation)
        engine.event_handler.actions.append(CancelTargetAction())


class CheckAction(DirectedAction):
    def __init__(self, dx, dy):
        super().__init__(dx, dy)
        self.time_units = 0

    def perform(self, engine, entity):
        dest_x, dest_y = self._get_target_xy(entity)
        if engine.get_blocking_entity_at_xy(dest_x, dest_y):
            engine.event_handler.actions.append(MeleeAction(self.dx, self.dy))
        else:
            engine.event_handler.actions.append(MoveAction(self.dx, self.dy))


class ReticuleAction(Action):
    def __init__(self):
        self.time_units = 0

    def _create_reticule(self, x, y, engine):
        reticule = Reticule(x, y)
        engine.display_manager.viewport.reticule = reticule

    def perform(self, engine, entity):
        raise NotImplementedError()


#TODO: different reticule color when inspecting (blue) vs. targetting (red)
class MoveReticuleAction(ReticuleAction):
    def __init__(self, dx, dy):
        super().__init__()
        self.dx = dx
        self.dy = dy

    def perform(self, engine, entity):
        if not engine.display_manager.viewport.reticule:
            x, y = entity.x, entity.y
            self._create_reticule(x, y, engine)
            engine.event_handler.actions.append(MoveReticuleAction(0, 0))
            engine.push_event_handler(eh.InspectEventHandler())
            return
        reticule = engine.display_manager.viewport.reticule
        reticule.x += self.dx
        reticule.y += self.dy
        entities = engine.get_entities_at_xy(reticule.x, reticule.y,
                                             visible=True)
        entities = engine._get_render_sorted_entities(entities)
        if entities:
            target = entities[0]
            engine.display_manager.gui.target_display.target = target
            if (isinstance(engine.event_handler, eh.TargetEventHandler) and
                (isinstance(target, Actor) and target.ai and
                 isinstance(target.ai, HostileEnemy))):
                entity.target = target
        else:
            entity.target = None
            engine.display_manager.gui.target_display.target = None


class NextTargetAction(ReticuleAction):
    def perform(self, engine, entity):
        tgts = engine.get_hostile_ents_visible_from_xy(entity.x, entity.y)
        tgts = engine.get_dist_sorted_entities(tgts)
        if not tgts:
            return
        elif (engine.display_manager.viewport.reticule is None and
             not entity.combat.ranged_attacks):
            return
        if entity.target:
            target = tgts[(tgts.index(entity.target) + 1) % len(tgts)]
        else:
            target = tgts[0]
        entity.target = target
        engine.display_manager.gui.target_display.target = target
        if engine.display_manager.viewport.reticule:
            engine.display_manager.viewport.reticule.x = target.x
            engine.display_manager.viewport.reticule.y = target.y
        else:
            self._create_reticule(target.x, target.y, engine)
            engine.push_event_handler(eh.TargetEventHandler())


class InspectUnderReticuleAction(ReticuleAction):
    def perform(self, engine, entity):
        target = engine.display_manager.gui.target_display.target
        if target:
            engine.event_handler.actions.append(InspectEntity(target))


class CancelTargetAction(Action):
    def __init__(self):
        self.time_units = 0

    def perform(self, engine, entity):
        entity.target = None
        engine.display_manager.gui.target_display.target = None
        engine.display_manager.viewport.reticule = None
        engine.pop_event_handler()


class PickupAction(Action):
    def perform(self, engine, entity):
        items = engine.get_items_at_xy(entity.x, entity.y)
        if items:
            inventory = entity.inventory
            item = items[0]
            if not inventory.is_full():
                inventory.pickup(item)
                engine.entities.remove(item)
                msg = f"You pickup {item.name}."
                engine.add_log_msg(msg)
            else:
                msg = f"There's no room for {item.name}."
                engine.add_log_msg(msg)
                engine.no_turn_taken = True
        else:
            msg = "There's nothing to pick up here."
            engine.add_log_msg(msg)
            engine.no_turn_taken = True


class SelectAction(Action):
    def __init__(self, selection):
        self.selection = selection

    def perform(self, engine, entity):
        raise NotImplementedError()


class SelectInventoryItem(SelectAction):
    def perform(self, engine, entity):
        item = entity.inventory.items[self.selection]
        if item is None or not self._is_valid_item(item, entity):
            self.time_units = 0
            return
        else:
            self.time_units = 1000
            self._perform(engine, entity, item)


class ConsumeItem(SelectInventoryItem):
    def _is_valid_item(self, item, entity):
        return isinstance(item, Consumable)

    def _perform(self, engine, entity, item):
        item.use()
        msg = f"You use a {item.name}."
        engine.add_log_msg(msg)
        entity.inventory.items[self.selection] = None
        engine.event_handler.actions.append(CloseMenuAction())


class DropItem(SelectInventoryItem):
    def _is_valid_item(self, item, entity):
        return not (isinstance(item, Equippable) and item.equipped)

    def _perform(self, engine, entity, item):
        entity.inventory.drop(item)
        item.x = entity.x
        item.y = entity.y
        engine.entities.add(item)
        msg = f"You drop {item.name}."
        engine.add_log_msg(msg)
        engine.event_handler.actions.append(CloseMenuAction())


class EquipItem(SelectInventoryItem):
    def _is_valid_item(self, item, entity):
        return isinstance(item, Equippable) and not item.equipped

    def _perform(self, engine, entity, item):
        slot = item.slot_type
        item_in_slot = entity.equipment.get_item_in_slot(slot)
        if item_in_slot:
            selection = entity.inventory.get_slot_from_item(item_in_slot)
            engine.event_handler.actions.append(UnequipItem(selection, False))
            engine.event_handler.actions.append(EquipItem(self.selection))
            self.time_units = 0
            return
        entity.equipment.equip_to_slot(slot, item)
        msg = f'You equip {item.name}.'
        item.name += ' (equipped)'
        engine.add_log_msg(msg)
        engine.event_handler.actions.append(CloseMenuAction())


class UnequipItem(SelectInventoryItem):
    def __init__(self, selection, close_menu=True):
        super().__init__(selection)
        self.close_menu = close_menu

    def _is_valid_item(self, item, entity):
        print(item.equipped)
        return isinstance(item, Equippable) and item.equipped

    def _perform(self, engine, entity, item):
        slot = item.slot_type
        entity.equipment.unequip_from_slot(slot, item)
        item.name = item.name[:-11]
        msg = f'You unequip {item.name}.'
        engine.add_log_msg(msg)
        if self.close_menu:
            engine.event_handler.actions.append(CloseMenuAction())


class CloseMenuAction(Action):
    def __init__(self):
        self.time_units = 0

    def perform(self, engine, entity):
        engine.display_manager.gui.menus.pop()
        engine.pop_event_handler()


class OpenMenuAction(Action):
    def __init__(self):
        self.time_units = 0

    def _create_menu(self, engine, w, h, dx, dy, title, menu_items):
        x = (config.SCREEN_WIDTH - w) // 2 + dx
        y = (config.SCREEN_HEIGHT - h) // 2 + dy
        menu = MenuDisplay(x, y, w, h, title, menu_items)
        engine.display_manager.gui.menus.append(menu)
        engine.push_event_handler(self.event_handler)

    def perform(self, engine, entity):
        raise NotImplementedError()


class InspectEntity(OpenMenuAction):
    def __init__(self, entity):
        super().__init__()
        self.event_handler = eh.InspectEntityHandler()
        self.entity = entity

    def perform(self, engine, entity):
        w = config.INVENTORY_WIDTH
        h = config.INVENTORY_HEIGHT
        dx, dy = 2, 2
        color, name = self.entity.color, self.entity.name.capitalize()
        title = f'[color={color}]{name}[/color]'
        menu_items = self.entity.get_stats()
        self._create_menu(engine, w, h, dx, dy, title, menu_items)


class InspectItem(SelectAction):
    def __init__(self, selection):
        super().__init__(selection)
        self.time_units = 0

    def perform(self, engine, entity):
        item = entity.inventory.items[self.selection]
        if item is None:
            return
        else:
            engine.event_handler.actions.append(InspectEntity(item))


class OpenInventoryMenu(OpenMenuAction):
    def __init__(self):
        super().__init__()

    def _get_menu_items(self, inventory):
        menu_items = []
        for slot, item in inventory.items.items():
            if item is None: continue
            if self._item_is_valid(item):
                text = f'{slot}. [color={item.color}]{item.name}[/color]'
                menu_items.append(text)
        return menu_items

    def perform(self, engine, entity):
        w = config.INVENTORY_WIDTH
        h = config.INVENTORY_HEIGHT
        dx, dy = 0, 0
        inventory = entity.inventory
        title = self._get_title(inventory)
        menu_items = self._get_menu_items(inventory)
        self._create_menu(engine, w, h, dx, dy, title, menu_items)


class ConsumeMenu(OpenInventoryMenu):
    def __init__(self):
        super().__init__()
        self.event_handler = eh.ConsumeMenuHandler()

    def _get_title(self, inventory):
        return 'Use which item?'

    def _item_is_valid(self, item):
        return isinstance(item, Consumable)


class InventoryMenu(OpenInventoryMenu):
    def __init__(self):
        super().__init__()
        self.event_handler = eh.InventoryMenuHandler()

    def _get_title(self, inventory):
        inv_size = inventory.size
        inv_unavail = len([k for k, v in inventory.items.items() if v])
        return f'Inventory: {inv_unavail}/{inv_size} spots taken'

    def _item_is_valid(self, item):
        return True


class DropMenu(OpenInventoryMenu):
    def __init__(self):
        super().__init__()
        self.event_handler = eh.DropMenuHandler()

    def _get_title(self, inventory):
        return 'Drop which item?'

    def _item_is_valid(self, item):
        return not item.equipped


class EquipMenu(OpenInventoryMenu):
    def __init__(self):
        super().__init__()
        self.event_handler = eh.EquipMenuHandler()

    def _get_title(self, inventory):
        return 'Equip which item?'

    def _item_is_valid(self, item):
        return (isinstance(item, Equippable) and not item.equipped)


class UnequipMenu(OpenInventoryMenu):
    def __init__(self):
        super().__init__()
        self.event_handler = eh.UnequipMenuHandler()

    def _get_title(self, inventory):
        return 'Unequip which item?'

    def _item_is_valid(self, item):
        return (isinstance(item, Equippable) and item.equipped)
