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
    blt.TK_KP_2: 'scroll_up',
    blt.TK_KP_8: 'scroll_down',
}

MENU = {
    blt.TK_Q: 'quit'
}

MAIN = {
    blt.TK_I: 'open_inventory',
    blt.TK_G: 'get_item',
    blt.TK_COMMA: 'get_item',
    blt.TK_D: 'drop_item'
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
                action = OpenInventoryAction()
            elif command == 'drop_item':
                action = None
        elif event in MENU:
            command = MENU[event]
            if command == 'quit':
                action = QuitAction()
        else:
            action = None
        return action


class InventoryEventHandler(EventHandler):
    def dispatch(self, event):
        if event in INVENTORY:
            action = None
        elif event in list(range(4, 30)):
            letter = chr(event + 93)
            action = DropAction(letter)
        else:
            action = None
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
