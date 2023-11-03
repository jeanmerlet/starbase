import config
from commands import *
from display import MenuDisplay, Reticule
from entities import Equippable, Consumable
from tiles import Door
import event_handlers


class Action:
    def __init__(self):
        self.time_units = 1000

    def perform(self, engine, entity):
        raise NotImplementedError()


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
            engine.gui.log.add_message(msg)
        elif not engine.game_map.in_bounds(dest_x, dest_y):
            msg = 'ERROR: out of bounds!'
            engine.gui.log.add_message(msg)
        elif not dest_tile.walkable:
            if isinstance(dest_tile, Door):
                action = OpenDoorAction(self.dx, self.dy)
                engine.event_handler.actions.append(action)
                self.time_units = 0
                return
            else:
                msg = "You can't go there."
                engine.gui.log.add_message(msg)
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
                engine.push_event_handler(event_handlers.GameOverEventHandler())
                msg = 'You have DIED.'
                engine.gui.log.add_message(msg)
            else:
                msg = f'The {target.name} dies.'
                engine.gui.log.add_message(msg)
            target.die()

    def _get_damage(self, attack, entity, target):
        dam = attack.roll_damage()
        if target.combat.shields:
            dam = target.combat.shields.take_hit(dam)
        return dam


#TODO: log text includes shields
class MeleeAction(DirectedAction, AttackAction):
    def __init__(self, dx, dy):
        DirectedAction.__init__(self, dx, dy)
        self.time_units = 1000

    def perform(self, engine, entity):
        dest_x, dest_y = self._get_target_xy(entity)
        target = engine.get_blocking_entity_at_xy(dest_x, dest_y)
        if target is None:
            msg = 'Nothing there.'
            engine.gui.log.add_message(msg)
        else:
            for attack in entity.combat.attacks:
                if not target.is_alive(): return
                dam = self._get_damage(attack, entity, target)
                target.combat.hit_points.take_damage(dam)
                if entity is engine.player:
                    subj = 'You'
                    verb = 'hit'
                    obj = f'the {target.name}'
                else:
                    subj = f'The {entity.name}'
                    verb = 'hits'
                    obj = 'you'
                if dam > 0:
                    msg = f'{subj} {verb} {obj} for {dam} damage.'
                    engine.gui.log.add_message(msg)
                else:
                    msg = f'{subj} {verb} {obj} but does no damage.'
                    engine.gui.log.add_message(msg)
                self._check_for_death(engine, target)


class TargetAction(Action):
    def __init__(self):
        self.time_units = 0

    def _create_reticule(self, x, y, engine):
        reticule = Reticule(x, y)
        engine.viewport.reticule = reticule

    def perform(self, engine, entity):
        raise NotImplementedError()


class RangedTargetAction(TargetAction):
    def perform(self, engine, entity):
        targets = engine.get_blocking_ents_visible_from_xy(entity.x, entity.y)
        if not targets:
            msg = 'Nothing to target.'
            engine.gui.log.add_message(msg)
        else:
            targets = engine.get_dist_sorted_entities(targets)
            target = targets[0]
            entity.target = target
            self._create_reticule(x, y, engine)
            engine.push_event_handler(event_handlers.TargetEventHandler())


class InspectTargetAction(TargetAction):
    def perform(self, engine, entity):
        x, y = entity.x, entity.y
        self._create_reticule(x, y, engine)
        #engine.gui.target_display.target = target
        engine.push_event_handler(event_handlers.InspectEventHandler())


class NextTargetAction(Action):
    def __init__(self):
        self.time_units = 0

    def perform(self, engine, entity):
        ents = engine.get_blocking_ents_visible_from_xy(entity.x, entity.y)
        ents = engine.get_dist_sorted_entities(ents)
        target = ents[(ents.index(entity.target) + 1) % len(ents)]
        entity.target = target
        engine.gui.target_display.target = target
        engine.viewport.reticule.x = target.x
        engine.viewport.reticule.y = target.y


class MoveReticuleAction(Action):
    def __init__(self, dx, dy):
        self.dx = dx
        self.dy = dy
        self.time_units = 0

    def perform(self, engine, entity):
        reticule = engine.viewport.reticule
        reticule.x += self.dx
        reticule.y += self.dy
        entities = engine.get_entities_at_xy(reticule.x, reticule.y)
        if entities:
            target = entities[0]
            entity.target = target
            engine.gui.target_display.target = target
        else:
            entity.target = None
            engine.gui.target_display.target = None


class CancelTargetAction(Action):
    def __init__(self):
        self.time_units = 0

    def perform(self, engine, entity):
        engine.gui.target_display.target = None
        engine.pop_event_handler()
        engine.viewport.reticule = None


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
                engine.gui.log.add_message(msg)
            else:
                msg = f"There's no room for {item.name}."
                engine.gui.log.add_message(msg)
                engine.no_turn_taken = True
        else:
            msg = "There's nothing to pick up here."
            engine.gui.log.add_message(msg)
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
        engine.gui.log.add_message(msg)
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
        engine.gui.log.add_message(msg)
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
        engine.gui.log.add_message(msg)
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
        engine.gui.log.add_message(msg)
        if self.close_menu:
            engine.event_handler.actions.append(CloseMenuAction())


class CloseMenuAction(Action):
    def __init__(self):
        self.time_units = 0

    def perform(self, engine, entity):
        engine.gui.menus.pop()
        engine.pop_event_handler()


class OpenMenuAction(Action):
    def _create_menu(self, engine, w, h, dx, dy, title, menu_items):
        x = (config.SCREEN_WIDTH - w) // 2 + dx
        y = (config.SCREEN_HEIGHT - h) // 2 + dy
        engine.gui.menus.append(MenuDisplay(x, y, w, h, title, menu_items))
        engine.push_event_handler(self.event_handler)

    def perform(self, engine, entity):
        raise NotImplementedError()


class InspectItem(SelectAction, OpenMenuAction):
    def __init__(self, selection):
        SelectAction.__init__(self, selection)
        self.event_handler = event_handlers.InspectItemHandler()
        self.time_units = 0

    def perform(self, engine, entity):
        item = entity.inventory.items[self.selection]
        if item is None: return
        w = config.INVENTORY_WIDTH
        h = config.INVENTORY_HEIGHT
        dx, dy = 2, 2
        title = f'{item.name.capitalize()}'
        menu_items = item.get_stats()
        self._create_menu(engine, w, h, dx, dy, title, menu_items)


class OpenInventoryMenu(OpenMenuAction):
    def __init__(self):
        self.time_units = 0

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
        self.event_handler = event_handlers.ConsumeMenuHandler()

    def _get_title(self, inventory):
        return 'Use which item?'

    def _item_is_valid(self, item):
        return isinstance(item, Consumable)


class InventoryMenu(OpenInventoryMenu):
    def __init__(self):
        super().__init__()
        self.event_handler = event_handlers.InventoryMenuHandler()

    def _get_title(self, inventory):
        inv_size = inventory.size
        inv_unavail = len([k for k, v in inventory.items.items() if v])
        return f'Inventory: {inv_unavail}/{inv_size} spots taken'

    def _item_is_valid(self, item):
        return True


class DropMenu(OpenInventoryMenu):
    def __init__(self):
        super().__init__()
        self.event_handler = event_handlers.DropMenuHandler()

    def _get_title(self, inventory):
        return 'Drop which item?'

    def _item_is_valid(self, item):
        return not item.equipped


class EquipMenu(OpenInventoryMenu):
    def __init__(self):
        super().__init__()
        self.event_handler = event_handlers.EquipMenuHandler()

    def _get_title(self, inventory):
        return 'Equip which item?'

    def _item_is_valid(self, item):
        return (isinstance(item, Equippable) and not item.equipped)


class UnequipMenu(OpenInventoryMenu):
    def __init__(self):
        super().__init__()
        self.event_handler = event_handlers.UnequipMenuHandler()

    def _get_title(self, inventory):
        return 'Unequip which item?'

    def _item_is_valid(self, item):
        return (isinstance(item, Equippable) and item.equipped)
