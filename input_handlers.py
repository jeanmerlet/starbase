from actions import Action, QuitAction, CheckAction
from bearlibterminal import terminal as blt


class EventHandler():
    def dispatch(self, event):
        # movement
        if event == blt.TK_KP_1:
            action = CheckAction(dx=-1, dy=1)
        elif event == blt.TK_KP_2:
            action = CheckAction(dx=0, dy=1)
        elif event == blt.TK_KP_3:
            action = CheckAction(dx=1, dy=1)
        elif event == blt.TK_KP_4:
            action = CheckAction(dx=-1, dy=0)
        elif event == blt.TK_KP_5:
            action = CheckAction(dx=0, dy=0)
        elif event == blt.TK_KP_6:
            action = CheckAction(dx=1, dy=0)
        elif event == blt.TK_KP_7:
            action = CheckAction(dx=-1, dy=-1)
        elif event == blt.TK_KP_8:
            action = CheckAction(dx=0, dy=-1)
        elif event == blt.TK_KP_9:
            action = CheckAction(dx=1, dy=-1)
        # quit
        elif event == blt.TK_Q:
            action = QuitAction()
        # unmapped
        else:
            action = None

        return action
