from actions import Action, QuitAction, MoveAction
from bearlibterminal import terminal as blt

class EventHandler():

    def dispatch(self, event):
        # movement
        if event == blt.TK_KP_1:
            action = MoveAction(dx=-1, dy=1)
        elif event == blt.TK_KP_2:
            action = MoveAction(dx=0, dy=1)
        elif event == blt.TK_KP_3:
            action = MoveAction(dx=1, dy=1)
        elif event == blt.TK_KP_4:
            action = MoveAction(dx=-1, dy=0)
        elif event == blt.TK_KP_5:
            action = MoveAction(dx=0, dy=0)
        elif event == blt.TK_KP_6:
            action = MoveAction(dx=1, dy=0)
        elif event == blt.TK_KP_7:
            action = MoveAction(dx=-1, dy=-1)
        elif event == blt.TK_KP_8:
            action = MoveAction(dx=0, dy=-1)
        elif event == blt.TK_KP_9:
            action = MoveAction(dx=1, dy=-1)
        # quit
        elif event == blt.TK_Q:
            action = QuitAction()
        # unmapped input
        else:
            action = None

        return action
