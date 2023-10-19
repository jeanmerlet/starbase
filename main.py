from bearlibterminal import terminal as blt
from event_handlers import *
from game_map import Map
from entities import Entity, Actor
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
        self.gui.update(self.player)

    def _get_render_sorted_entities(self):
        return sorted(self.entities, key=lambda x: -x.render_order)

    def _handle_enemy_turns(self):
        visible = self.game_map.visible
        tiles = self.game_map.tiles
        for entity in self.entities - {self.player}:
            if entity.ai:
                target = self.player if self.player.combat.is_alive() else None
                action = entity.ai.get_action(target, visible, tiles)
                action.perform(self, entity)

    def _update_fov(self):
        self.game_map.visible[:, :] = False
        self.fov.do_fov(self.player, self.game_map.visible)
        self.game_map.explored |= self.game_map.visible

    def handle_event(self):
        event = blt.read()
        action = self.event_handler.dispatch(event)
        if action is None: return
        action.perform(self, self.player)
        self._handle_enemy_turns()
        self._update_fov()
        self.gui.update(self.player)

    def render(self):
        blt.clear()
        self.game_map.render(blt)
        for ent in self._get_render_sorted_entities():
            if self.game_map.visible[ent.x, ent.y]:
                ent.render(blt)
        self.gui.render()
        blt.refresh()

    def get_blocking_entity(self, x, y):
        for ent in self.entities:
            if ent.blocking and ent.x == x and ent.y == y:
                return ent
        return None

    def load_terminal_settings(self):
        self.settings = config.TerminalSettings()


def main():
    event_handler = MainGameEventHandler()
    game_map = Map(config.MAP_WIDTH, config.MAP_HEIGHT)
    game_map.gen_map(config.GRIDW, config.GRIDH, config.BLOCK_SIZE)
    player = game_map.create_player()
    entities = {player}
    game_map.populate(entities)
    fov = Fov(game_map.opaque)
    gui = GUI(player.combat.hp, player.combat.max_hp)
    engine = Engine(event_handler, game_map, player, entities, fov, gui)

    blt.open()
    engine.load_terminal_settings()
    while True:
        engine.render()
        engine.handle_event()
        #while blt.has_input():
            #engine.handle_event()


if __name__ == "__main__":
    main()
