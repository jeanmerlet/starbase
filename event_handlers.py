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

INVENTORY = {
    blt.TK_ESCAPE: 'exit'
}

GAME_MENU = {
    blt.TK_Q: 'quit'
}

MAIN = {
    blt.TK_I: 'open_inventory',
    blt.TK_G: 'get_item',
    blt.TK_D: 'drop_item',
    blt.TK_E: 'equip_item',
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
        elif event in GAME_MENU:
            command = GAME_MENU[event]
            if command == 'quit':
                action = QuitAction()
        else:
            action = None
        return action


class InventoryEventHandler(EventHandler):
    def __init__(self, inventory, valid_items):
        self.inventory = inventory
        self.valid_items = valid_items

    def dispatch(self, event):
        if event in INVENTORY:
            command = INVENTORY[event]
            if command == 'exit':
                action = CloseMenuAction()
        elif event in list(range(4, 30)):
            slot = chr(event + 93)
            item = self.inventory.items[slot]
            if item and item in self.valid_items:
                action = self._get_action(item)
            else:
                action = None
        else:
            action = None
        return action


class InspectInventoryHandler(InventoryEventHandler):
    def _get_action(self, item):
        action = InspectItem(item)
        return action
        

class DropInventoryHandler(InventoryEventHandler):
    def _get_action(self, item):
        action = DropItem(item)
        return action


class EquipInventoryHandler(InventoryEventHandler):
    def _get_action(self, item):
        action = EquipItem(item)
        return action


class UnequipInventoryHandler(InventoryEventHandler):
    def _get_action(self, item):
        action = UnequipItem(item)
        return action


class GameOverEventHandler(EventHandler):
    def dispatch(self, event):
        if event in MENU:
            command = MENU[event]
            if command == 'quit':
                action = QuitAction()
        else:
            action = None
        return action
