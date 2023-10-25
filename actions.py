import config
from display import MenuDisplay


class Action:
    def __init__(self):
        self.msgs = []

    def perform(self, engine, entity):
        raise NotImplementedError()


class DeathAction(Action):
    def __init__(self):
        super().__init__()

    def perform(self, engine, entity):
        if entity is engine.player:
            self.msgs.append('You have DIED.')
            engine.change_event_handler(1)
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
        return []


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

    def _attack(self, entity, target):
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
            dam = self._attack(entity, target)
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


class ItemAction(Action):
    def __init__(self, item):
        super().__init__()
        self.item = item

    def perform(self, engine, entity):
        raise NotImplementedError()


class InspectItem(ItemAction):
    def perform(self, engine, entity):
        self.msgs.append(f'This is a nice looking {self.item.name}.')
        return self.msgs


class DropItem(ItemAction):
    def perform(self, engine, entity):
        entity.inventory.items.remove(self.item)
        self.item.x = entity.x
        self.item.y = entity.y
        engine.entities.add(self.item)
        self.msgs.append("You drop {item.name}.")
        engine.gui.menu = None
        engine.change_event_handler(0)
        return self.msgs


class PickupAction(Action):
    def perform(self, engine, entity):
        items = engine.get_items_at_xy(entity.x, entity.y)
        if items:
            inventory = entity.inventory
            item = items[0]
            if not inventory.is_full():
                inventory.items.append(item)
                engine.entities.remove(item)
                self.msgs.append(f"You pickup {item.name}.")
            else:
                self.msgs.append(f"There's no room for {item.name}.")
        else:
            self.msgs.append("There's nothing here.")
            engine.no_turn_taken = True
        return self.msgs


class MenuAction(Action):
    def __init__(self):
        super().__init__()

    def perform(self, engine, entity):
        raise NotImplementedError()


class OpenInventoryAction(MenuAction):
    def __init__(self, state):
        super().__init__()
        self.state = state

    def perform(self, engine, entity):
        w = config.INVENTORY_WIDTH
        h = config.INVENTORY_HEIGHT
        x = (config.SCREEN_WIDTH - config.INVENTORY_WIDTH) // 2
        y = (config.SCREEN_HEIGHT - h) // 2
        menu_items = entity.inventory.items
        inv_size = entity.inventory.size
        inv_avail = inv_size - len(entity.inventory.items)
        menu_title = f'Inventory: {inv_avail}/{inv_size} spots available'
        engine.gui.menu = MenuDisplay(x, y, w, h, menu_items, menu_title)
        if self.state == 'inspect':
            engine.change_event_handler(2)
        elif self.state == 'drop':
            engine.change_event_handler(3)
        engine.no_turn_taken = True
        return self.msgs


class CloseInventoryAction(MenuAction):
    def perform(self, engine, entity):
        engine.gui.menu = None
        engine.change_event_handler(0)
        engine.no_turn_taken = True
        return self.msgs
