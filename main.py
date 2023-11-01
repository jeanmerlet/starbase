from bearlibterminal import terminal as blt
# ~/miniconda3/envs/dungeon/lib/python3.11/site-packages/bearlibterminal/terminal.py
from event_handlers import EventHandler
from game_map import Map
from entities import Entity, Actor, Item
from fov import FieldOfView
import config
from display import GUI
import time


class Engine:
    def __init__(self, game_map, player, entities, fov, gui):
        self.game_map = game_map
        self.player = player
        self.event_handler = EventHandler(self, player)
        self.entities = entities
        self.fov = fov
        self._update_fov()
        self.gui = gui
        self.gui.update(self.player)
        self.game_states = ['main']
        self.game_state = 'main'

    def _get_dist_sorted_entities(self, entities):
        key = lambda x: max(abs(self.player.x - x.x), abs(self.player.y - x.y))
        return sorted(entities, key=key)

    def handle_nonplayer_turns(self):
        if self.game_state != 'main': return
        visible = self.game_map.visible
        tiles = self.game_map.tiles
        entities = self.entities - {self.player}
        entities = self._get_dist_sorted_entities(entities)
        for entity in entities:
            if entity.ai:
                target = self.player if self.player.is_alive() else None
                action = entity.ai.get_action(self, target, visible, tiles)
                action.perform(self, entity)

    def _update_fov(self):
        self.game_map.visible[:, :] = False
        self.fov.do_fov(self.player, self.game_map.visible)
        self.game_map.explored |= self.game_map.visible

    def update(self):
        self._update_fov()
        self.player.combat.tick()
        self.gui.update(self.player)

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

    def _update_game_states(self):
        self.game_state = self.game_states[-1]

    def push_game_state(self, game_state):
        self.game_states.append(game_state)
        self._update_game_states()

    def pop_game_state(self):
        self.game_states.pop()
        self._update_game_states()

#TODO: move all engine to engine.py
#TODO: add wizmode for starting game with all entities renderered
# add wizmode for starting game with all entities renderered and
# printing fps, etc.
# also print fps in-game instead of to stdout
def main():
    game_map = Map(config.MAP_WIDTH, config.MAP_HEIGHT)
    game_map.gen_map(config.GRIDW, config.GRIDH, config.BLOCK_SIZE)
    player = game_map.spawn_player()
    entities = {player}
    game_map.populate(entities)
    fov = FieldOfView(game_map.opaque)
    gui = GUI(player.combat.hit_points.hp, player.combat.hit_points.max_hp,
              player.combat.shields.hp, player.combat.shields.max_hp)
    engine = Engine(game_map, player, entities, fov, gui)

    blt.open()
    engine.load_terminal_settings()
    #i = 0
    start_time = time.time()
    while True:
        engine.render()
        if blt.has_input():
            engine.event_handler.handle_event()
            engine.update()
        #print(f'fps: {i // (time.time() - start_time)}')
        #i += 1


if __name__ == "__main__":
    main()
