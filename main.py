from bearlibterminal import terminal as blt
# ~/miniconda3/envs/dungeon/lib/python3.11/site-packages/bearlibterminal/terminal.py
from event_handlers import *
from game_map import Map
from entities import Entity, Actor, Item
from fov import FieldOfView as Fov
import config
from display import GUI


class Engine:
    def __init__(self, event_handler, game_map, player, entities, fov, gui):
        self.event_handler = event_handler
        self.game_map = game_map
        self.player = player
        self.entities = entities
        self.fov = fov
        self._update_fov()
        self.gui = gui
        self.gui.update(self.player, [])
        self.skip_enemy_turn = False

    def _get_dist_sorted_entities(self, entities):
        key = lambda x: max(abs(self.player.x - x.x), abs(self.player.y - x.y))
        return sorted(entities, key=key)

    def _handle_enemy_turns(self):
        visible = self.game_map.visible
        tiles = self.game_map.tiles
        msgs = []
        entities = self.entities - {self.player}
        entities = self._get_dist_sorted_entities(entities)
        for entity in entities:
            if entity.ai:
                target = self.player if self.player.combat.is_alive() else None
                action = entity.ai.get_action(self, target, visible, tiles)
                msgs += action.perform(self, entity)
        return msgs

    def handle_event(self):
        event = blt.read()
        action = self.event_handler.dispatch(event)
        if action is None:
            return
        elif isinstance(action, InstantAction):
            action.perform(self, self.player)
            return
        msgs = action.perform(self, self.player)
        msgs += self._handle_enemy_turns()
        self._update_all(msgs)

    def _update_fov(self):
        self.game_map.visible[:, :] = False
        self.fov.do_fov(self.player, self.game_map.visible)
        self.game_map.explored |= self.game_map.visible

    def _update_all(self, msgs):
        self.gui.update(self.player, msgs)
        self._update_fov()
        self.player.combat.shields.charge()

    def _get_render_sorted_entities(self):
        return sorted(self.entities, key=lambda x: -x.render_order)

    def render(self):
        blt.clear_area(0, 0, config.MAP_WIDTH, config.MAP_HEIGHT)
        self.game_map.render(blt)
        for ent in self._get_render_sorted_entities():
            #if self.game_map.visible[ent.x, ent.y]:
            if True:
                ent.render(blt)
        self.gui.render()
        blt.refresh()

    def get_blocking_entity_at_xy(self, x, y):
        for ent in self.entities:
            if ent.blocking and ent.x == x and ent.y == y:
                return ent
        return None

    def get_items_at_xy(self, x, y):
        items = []
        for ent in self.entities:
            if isinstance(ent, Item) and ent.x == x and ent.y == y:
                items.append(ent)
        return items

    def load_terminal_settings(self):
        self.settings = config.TerminalSettings()

    def set_event_handler(self, event_handler, **kwargs):
        if 'inventory' in kwargs:
            inventory = kwargs['inventory']
        if 'valid_items' in kwargs:
            valid_items = kwargs['valid_items']
        if event_handler == 'main_game':
            self.event_handler = MainGameEventHandler()
        elif event_handler == 'game_over':
            self.event_handler = GameOverEventHandler()
        elif event_handler == 'inspect_inventory':
            self.event_handler = InspectInventoryHandler(inventory, valid_items)
        elif event_handler == 'drop_inventory':
            self.event_handler = DropInventoryHandler(inventory, valid_items)
        elif event_handler == 'equip_inventory':
            self.event_handler = EquipInventoryHandler(inventory, valid_items)
        elif event_handler == 'unequip_inventory':
            self.event_handler = UnequipInventoryHandler(inventory, valid_items)
            


def main():
    event_handler = MainGameEventHandler()
    game_map = Map(config.MAP_WIDTH, config.MAP_HEIGHT)
    game_map.gen_map(config.GRIDW, config.GRIDH, config.BLOCK_SIZE)
    player = game_map.spawn_player()
    entities = {player}
    game_map.populate(entities)
    fov = Fov(game_map.opaque)
    gui = GUI(player.combat.hp, player.combat.max_hp, 0, 0)
    engine = Engine(event_handler, game_map, player, entities, fov, gui)

    blt.open()
    engine.load_terminal_settings()
    while True:
        engine.render()
        engine.handle_event()


if __name__ == "__main__":
    main()
