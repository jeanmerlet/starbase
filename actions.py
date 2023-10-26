import config
from display import MenuDisplay
from entities import Equippable


class Action:
    def __init__(self):
        self.msgs = []

    def perform(self, engine, entity):
        raise NotImplementedError()


class InstantAction(Action):
    def perform(self, engine, entity):
        raise NotImplementedError()


class ItemAction(Action):
    def __init__(self, item):
        super().__init__()
        self.item = item

    def perform(self, engine, entity):
        raise NotImplementedError()


class DeathAction(Action):
    def __init__(self):
        super().__init__()

    def perform(self, engine, entity):
        if entity is engine.player:
            self.msgs.append('You have DIED.')
            engine.set_event_handler('game_over')
        else:
            self.msgs.append(f'The {entity.name} dies.')
        entity.name = f'{entity.name} corpse'
        entity.char = '%'
        entity.color = 'dark red'
        entity.icon = '[color=dark red]%'
        entity.blocking = False
        entity.ai = None
        entity.render_order = 2
        return self.msgs


class QuitAction(Action):
    def perform(self, engine, entity):
        raise SystemExit()


class WaitAction(Action):
    def perform(self, engine, entity):
        return self.msgs


class DirectedAction(Action):
    def __init__(self, dx, dy):
        super().__init__()
        self.dx = dx
        self.dy = dy

    def perform(self, engine, entity):
        raise NotImplementedError()

    def _get_target_xy(self, entity):
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy
        return dest_x, dest_y


class AttackAction(DirectedAction):
    def perform(self, engine, entity):
        raise NotImplementedError()

    def _check_for_death(self, engine, target):
        if not target.combat.is_alive():
            self.msgs += DeathAction().perform(engine, target)

    def _roll_damage(self, entity, target):
        dam = int(entity.combat.att - target.combat.armor())
        if target.combat.shields:
            dam = target.combat.shields.take_hit(dam)
        return dam


class MeleeAction(AttackAction):
    def perform(self, engine, entity):
        dest_x, dest_y = self._get_target_xy(entity)
        target = engine.get_blocking_entity_at_xy(dest_x, dest_y)
        if not target:
            self.msgs.append('Nothing there.')
        else:
            dam = self._roll_damage(entity, target)
            if entity is engine.player:
                subj = 'You'
                verb = 'hit'
                obj = f'the {target.name}'
            else:
                subj = f'The {entity.name}'
                verb = 'hits'
                obj = 'you'
            if dam > 0:
                self.msgs.append(f'{subj} {verb} {obj} for {dam} damage.')
                target.combat.set_hp(target.combat.hp - dam)
            else:
                self.msgs.append(f'{subj} {verb} {obj} but does no damage.')
        self._check_for_death(engine, target)
        return self.msgs


class MoveAction(DirectedAction):
    def perform(self, engine, entity):
        dest_x, dest_y = self._get_target_xy(entity)
        blocking_ent = engine.get_blocking_entity_at_xy(dest_x, dest_y)
        if blocking_ent:
            self.msgs.append(f'ERROR: {blocking_ent.name} blocking')
        elif not engine.game_map.in_bounds(dest_x, dest_y):
            self.msgs.append('ERROR: out of bounds!')
        elif not engine.game_map.tiles[dest_x, dest_y].walkable:
            self.msgs.append("You can't go there.")
        else:
            entity.move(self.dx, self.dy)
        return self.msgs


class CheckAction(DirectedAction):
    def perform(self, engine, entity):
        dest_x, dest_y = self._get_target_xy(entity)
        if engine.get_blocking_entity_at_xy(dest_x, dest_y):
            return MeleeAction(self.dx, self.dy).perform(engine, entity)
        else:
            return MoveAction(self.dx, self.dy).perform(engine, entity)


class PickupAction(Action):
    def perform(self, engine, entity):
        items = engine.get_items_at_xy(entity.x, entity.y)
        if items:
            inventory = entity.inventory
            item = items[0]
            if not inventory.is_full():
                inventory.pickup(item)
                engine.entities.remove(item)
                self.msgs.append(f"You pickup {item.name}.")
            else:
                self.msgs.append(f"There's no room for {item.name}.")
                engine.no_turn_taken = True
        else:
            self.msgs.append("There's nothing here.")
            engine.no_turn_taken = True
        return self.msgs


class InspectItem(ItemAction, InstantAction):
    def perform(self, engine, entity):
        print(f'This is a nice looking {self.item.name}.')
        return None


class DropItem(ItemAction):
    def perform(self, engine, entity):
        entity.inventory.drop(self.item)
        self.item.x = entity.x
        self.item.y = entity.y
        engine.entities.add(self.item)
        self.msgs.append(f"You drop {self.item.name}.")
        CloseMenuAction().perform(engine, entity)
        return self.msgs


class EquipItem(ItemAction):
    def perform(self, engine, entity):
        slot = self.item.slot_type
        item_in_slot = entity.equipment.get_item_in_slot(slot)
        if item_in_slot:
            self.msgs += UnequipItem(item_in_slot).perform(engine, entity)
        entity.equipment.equip_to_slot(slot, self.item)
        self.item.equipped = True
        self.item.name = self.item.name + ' (equipped)'
        self.msgs.append(f'You equip {self.item.name}.')
        CloseMenuAction().perform(engine, entity)
        return self.msgs


class UnequipItem(ItemAction):
    def perform(self, engine, entity):
        slot = self.item.slot_type
        entity.equipment.unequip_from_slot(slot)
        self.item.equipped = False
        self.item.name = self.item.name[:-11]
        self.msgs.append(f'You unequip {self.item.name}.')
        CloseMenuAction().perform(engine, entity)
        return self.msgs


class CloseMenuAction(InstantAction):
    def perform(self, engine, entity):
        engine.gui.menu = None
        engine.set_event_handler('main_game')


class InventoryMenu(InstantAction):
    def perform(self, engine, entity):
        w = config.INVENTORY_WIDTH
        h = config.INVENTORY_HEIGHT
        x = (config.SCREEN_WIDTH - config.INVENTORY_WIDTH) // 2
        y = (config.SCREEN_HEIGHT - h) // 2
        inventory = entity.inventory
        items, names = self._get_valid_inventory_items_names(inventory)
        self._set_inventory_options(inventory)
        engine.set_event_handler(self.event_handler, inventory=inventory,
                                 valid_items=items)
        engine.gui.menu = MenuDisplay(x, y, w, h, names, self.menu_title)

    def _get_valid_inventory_items_names(self, inventory):
        valid_items, menu_names = [], []
        for slot, item in inventory.items.items():
            if item is None: continue
            if self._item_is_valid(item):
                valid_items.append(item)
                menu_name = f'{slot}. [color={item.color}]{item.name}[/color]'
                menu_names.append(menu_name)
        return valid_items, menu_names


class InspectInventoryMenu(InventoryMenu):
    def _set_inventory_options(self, inventory):
        inv_size = inventory.size
        inv_avail = inv_size - len(inventory.items)
        self.menu_title = f'Inventory: {inv_avail}/{inv_size} spots available'
        self.event_handler = 'inspect_inventory'

    def _item_is_valid(self, item):
        return True


class DropInventoryMenu(InventoryMenu):
    def _set_inventory_options(self, inventory):
        self.menu_title = f'Drop which item?'
        self.event_handler = 'drop_inventory'

    def _item_is_valid(self, item):
        return not item.equipped


class EquipInventoryMenu(InventoryMenu):
    def _set_inventory_options(self, inventory):
        self.menu_title = f'Equip what?'
        self.event_handler = 'equip_inventory'

    def _item_is_valid(self, item):
        return (isinstance(item, Equippable) and not item.equipped)


class UnequipInventoryMenu(InventoryMenu):
    def _set_inventory_options(self, inventory):
        self.menu_title = f'Unequip what?'
        self.event_handler = 'unequip_inventory'

    def _item_is_valid(self, item):
        return (isinstance(item, Equippable) and item.equipped)
