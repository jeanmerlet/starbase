from bearlibterminal import terminal as blt
from commands import *
from actions import *


class EventHandler:
    def __init__(self, engine, player):
        self.engine = engine
        self.player = player
        self.commands = [MAIN]
        self.active_commands = MAIN

    def handle_event(self):
        event = blt.read()
        action = None
        for cmd_domain in self.active_commands:
            if event in cmd_domain:
                action = self._dispatch(cmd_domain, event)
        if action is None: return
        self.actions = [action]
        for action in self.actions:
            action.perform(self.engine, self.player)
        self.engine.handle_nonplayer_turns()

    def _dispatch(self, cmd_domain, event):
        if cmd_domain == MOVE_CMDS:
            dx, dy = cmd_domain[event]
            action = CheckAction(dx, dy)
        elif cmd_domain == WAIT_CMDS:
            action = WaitAction()
        elif cmd_domain == MAIN_CMDS:
            if event == blt.TK_D:
                action = DropMenu()
            elif event == blt.TK_E:
                action = EquipMenu()
            elif event == blt.TK_G:
                action = PickupAction()
            elif event == blt.TK_I:
                action = InventoryMenu()
            elif event == blt.TK_U:
                action = UnequipMenu()
        elif cmd_domain == MENU_CMDS:
            if event == blt.TK_ESCAPE:
                action = CloseMenuAction()
            elif event in range(4, 30):
                selection = chr(event + 93)
                game_state = self.engine.game_state
                if game_state == 'inventory_menu':
                    action = InspectItem(selection)
                elif game_state == 'drop_menu':
                    action = DropItem(selection)
                elif game_state == 'equip_menu':
                    action = EquipItem(selection)
                elif game_state == 'unequip_menu':
                    action = UnequipItem(selection)
        elif cmd_domain == QUIT_CMD:
            action = QuitAction()
        return action

    def _update_cmds(self):
        self.active_commands = self.commands[-1]

    def push_cmds(self, cmd_set):
        self.commands.append(cmd_set)
        self._update_cmds()

    def pop_cmds(self):
        self.commands.pop()
        self._update_cmds()

    def insert_action(self, action, idx):
        self.actions.insert(idx, action)

    def clear_action(self, action):
        self.actions.remove(action)
