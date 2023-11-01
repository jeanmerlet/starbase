from bearlibterminal import terminal as blt
from commands import *
from actions import *


class EventHandler:
    def __init__(self):
        pass

    def handle_event(self, engine, player):
        event = blt.read()
        action = self._dispatch(event, engine)
        if action is None: return
        self.actions = [action]
        for action in self.actions:
            action.perform(engine, player)
        engine.handle_nonplayer_turns()

    def _dispatch(self, event, engine):
        raise NotImplementedError()


class MainEventHandler(EventHandler):
    def _dispatch(self, event, engine):
        action = None
        if event in MOVE_CMDS:
            dx, dy = MOVE_CMDS[event]
            action = CheckAction(dx, dy)
        elif event in WAIT_CMDS:
            action = WaitAction()
        elif event in MAIN_CMDS:
            if event == blt.TK_D:
                action = DropMenu()
            elif event == blt.TK_E:
                action = EquipMenu()
            elif event == blt.TK_F:
                action = TargetAction()
            elif event == blt.TK_G:
                action = PickupAction()
            elif event == blt.TK_I:
                action = InventoryMenu()
            elif event == blt.TK_U:
                action = UnequipMenu()
        elif event in QUIT_CMD:
            action = QuitAction()
        return action


class MenuEventHandler(EventHandler):
    def _dispatch(self, event, engine):
        action = None
        if event in MENU_CMDS:
            if event == blt.TK_ESCAPE:
                action = CloseMenuAction()
            elif event in range(4, 30):
                selection = chr(event + 93)
                action = self._get_action(selection)
        return action


class InspectItemHandler(MenuEventHandler):
    def _get_action(self, selection):
        return None


class DropMenuHandler(MenuEventHandler):
    def _get_action(self, selection):
        return DropItem(selection)


class EquipMenuHandler(MenuEventHandler):
    def _get_action(self, selection):
        return EquipItem(selection)


class InventoryMenuHandler(MenuEventHandler):
    def _get_action(self, selection):
        return InspectItem(selection)


class UnequipMenuHandler(MenuEventHandler):
    def _get_action(self, selection):
        return UnequipItem(selection)


class TargettingEventHandler(EventHandler):
    def _dispatch(self, event, engine):
        action = None
        if event in TARGET_CMDS:
            if event == blt.TK_TAB:
                action = NextTargetAction()
            elif (event == blt.TK_F or event == blt.TK_ENTER or
                 event == blt.TK_KP_ENTER):
                action = ConfirmTargetAction()
        elif event in MOVE_CMDS:
            dx, dy = MOVE_CMDS[event]
            action = MoveTargetAction(dx, dy)
        return action


class GameOverEventHandler(EventHandler):
    def _dispatch(self, event, engine):
        action = None
        if event in QUIT_CMD:
            action = QuitAction()
        return action
