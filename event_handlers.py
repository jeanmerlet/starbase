from bearlibterminal import terminal as blt
from commands import *
from actions import *


class EventHandler:
    def __init__(self):
        self.timer = 0

    def handle_event(self, engine):
        player = engine.player
        event = blt.read()
        action = self._dispatch(event, engine)
        if action is None: return
        self.actions = [action]
        for action in self.actions:
            action.perform(engine, player)
            self.timer += action.time_units
        while self.timer >= 1000:
            engine.handle_nonplayer_turns()
            self.timer -= 1000

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
                action = CreateWeaponReticule()
            elif event == blt.TK_G:
                action = PickupAction()
            elif event == blt.TK_I:
                action = InventoryMenu()
            elif event == blt.TK_T:
                action = ThrowMenu()
            elif event == blt.TK_Q:
                if blt.check(blt.TK_CONTROL):
                    action = QuitAction()
                else:
                    action = InjectMenu()
            elif event == blt.TK_R:
                action = UnequipMenu()
            elif event == blt.TK_X:
                action = CreateInspectReticule()
            elif event == blt.TK_GRAVE:
                action = FPSToggle()
        return action


class MenuEventHandler(EventHandler):
    def _dispatch(self, event, engine):
        action = None
        if event in CANCEL_CMD:
            action = CloseMenuAction()
        elif event in MENU_CMDS:
            if event in range(4, 30):
                selection = chr(event + 93)
                action = self._get_action(selection)
        return action


class InspectEntityHandler(MenuEventHandler):
    def _get_action(self, selection):
        return None


class InjectMenuHandler(MenuEventHandler):
    def _get_action(self, selection):
        return InjectItem(selection)


class ThrowMenuHandler(MenuEventHandler):
    def _get_action(self, selection):
        return ThrowItem(selection)


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


class RangedAttackEventHandler(EventHandler):
    def _dispatch(self, event, engine):
        action = None
        if event in CANCEL_CMD:
            action = CancelTargetAction()
        elif event in TARGET_CMDS:
            if event == blt.TK_TAB:
                action = NextTargetAction()
            elif (event == blt.TK_F or event == blt.TK_ENTER or
                 event == blt.TK_KP_ENTER):
                action = RangedAction()
        elif event in MOVE_CMDS:
            dx, dy = MOVE_CMDS[event]
            action = MoveReticule(dx, dy)
        return action


class ThrowEventHandler(EventHandler):
    def __init__(self, item):
        super().__init__()
        self.item = item

    def _dispatch(self, event, engine):
        action = None
        if event in CANCEL_CMD:
            action = CancelTargetAction()
        elif event in TARGET_CMDS:
            if event == blt.TK_TAB:
                action = NextTargetAction()
            elif event == blt.TK_ENTER or event == blt.TK_KP_ENTER:
                action = ThrowAction(self.item)
        elif event in MOVE_CMDS:
            dx, dy = MOVE_CMDS[event]
            action = MoveReticule(dx, dy)
        return action


class InspectEventHandler(EventHandler):
    def _dispatch(self, event, engine):
        action = None
        if event in CANCEL_CMD:
            action = CancelTargetAction()
        elif event in TARGET_CMDS:
            if event == blt.TK_TAB:
                action = NextTargetAction()
            elif event == blt.TK_ENTER or event == blt.TK_KP_ENTER:
                action = InspectUnderReticuleAction()
        elif event in MOVE_CMDS:
            dx, dy = MOVE_CMDS[event]
            action = MoveReticule(dx, dy)
        return action


class GameOverEventHandler(EventHandler):
    def _dispatch(self, event, engine):
        action = None
        if event in QUIT_CMD:
            if blt.check(blt.TK_CONTROL):
                action = QuitAction()
        return action
