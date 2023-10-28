from bearlibterminal import terminal as blt
from actions import *


MOVE = {
    blt.TK_KP_1: (-1, 1),
    blt.TK_KP_2: (0, 1),
    blt.TK_KP_3: (1, 1),
    blt.TK_KP_4: (-1, 0),
    blt.TK_KP_6: (1, 0),
    blt.TK_KP_7: (-1, -1),
    blt.TK_KP_8: (0, -1),
    blt.TK_KP_9: (1, -1)
}

WAIT = {
    blt.TK_KP_5,
    blt.TK_PERIOD
}

ESCAPE = {
    blt.TK_ESCAPE
}

OPTIONS = {
    blt.TK_Q: 'exit_game'
}

MAIN = {
    blt.TK_D: 'drop_item',
    blt.TK_E: 'equip_item',
    blt.TK_G: 'get_item',
    blt.TK_I: 'open_inventory',
    blt.TK_U: 'unequip_item'
}


class EventHandler():
    def dispatch(self, event):
        raise NotImplementedError()


class MainGameEventHandler(EventHandler):
    def dispatch(self, event):
        if event in MOVE:
            dx, dy = MOVE[event]
            action = CheckAction(dx, dy)
        elif event in WAIT:
            action = WaitAction()
        elif event in MAIN:
            command = MAIN[event]
            if command == 'get_item':
                action = PickupAction()
            elif command == 'open_inventory':
                action = InspectInventoryMenu()
            elif command == 'drop_item':
                action = DropInventoryMenu()
            elif command == 'equip_item':
                action = EquipInventoryMenu()
            elif command == 'unequip_item':
                action = UnequipInventoryMenu()
        elif event in OPTIONS:
            command = OPTIONS[event]
            if command == 'quit':
                action = QuitAction()
        else:
            action = None
        return action


class MenuEventHandler(EventHandler):
    def dispatch(self, event):
        if event in ESCAPE:
            action = CloseMenuAction()
        elif event in list(range(4, 30)):
            selection = chr(event + 93)
            if self._selection_is_valid(selection):
                action = self._get_action()
            else:
                action = None
        else:
            action = None
        return action


class InventoryMenuHandler(MenuEventHandler):
    def __init__(self, inventory, valid_items):
        self.inventory = inventory
        self.valid_items = valid_items

    def _selection_is_valid(self, slot):
        item = self.inventory.items[slot]
        if item and item in self.valid_items:
            self.item = item
            return True
        return False


class InspectInventoryHandler(InventoryMenuHandler):
    def _get_action(self):
        action = InspectItem(self.item)
        return action
        

class DropInventoryHandler(InventoryMenuHandler):
    def _get_action(self):
        action = DropItem(self.item)
        return action


class EquipInventoryHandler(InventoryMenuHandler):
    def _get_action(self):
        action = EquipItem(self.item)
        return action


class UnequipInventoryHandler(InventoryMenuHandler):
    def _get_action(self):
        action = UnequipItem(self.item)
        return action


class GameOverEventHandler(EventHandler):
    def dispatch(self, event):
        if event in OPTIONS:
            command = OPTIONS[event]
            if command == 'quit':
                action = QuitAction()
        else:
            action = None
        return action
