from bearlibterminal import terminal as blt
from actions import QuitAction, CheckAction, WaitAction


MOVE_KEYS = {
    blt.TK_KP_1: (-1, 1),
    blt.TK_KP_2: (0, 1),
    blt.TK_KP_3: (1, 1),
    blt.TK_KP_4: (-1, 0),
    blt.TK_KP_6: (1, 0),
    blt.TK_KP_7: (-1, -1),
    blt.TK_KP_8: (0, -1),
    blt.TK_KP_9: (1, -1)
}

WAIT_KEYS = {
    blt.TK_KP_5,
    blt.TK_PERIOD
}

MENU_KEYS = {
    blt.TK_Q,
    blt.TK_ESCAPE
}


class EventHandler():
    def dispatch(self, event):
        raise NotImplementedError()


class GameOverEventHandler(EventHandler):
    def dispatch(self, event):
        if event in MENU_KEYS:
            action = QuitAction()
        else:
            action = None
        return action


class MainGameEventHandler(EventHandler):
    def dispatch(self, event):
        if event in MOVE_KEYS:
            dx, dy = MOVE_KEYS[event]
            action = CheckAction(dx, dy)
        elif event in WAIT_KEYS:
            action = WaitAction()
        elif event in MENU_KEYS:
            action = QuitAction()
        else:
            action = None
        return action



