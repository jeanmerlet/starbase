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
        self.gui.update(self.player, [])

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
        if action is None: return
        msgs = []
        msgs += action.perform(self, self.player)
        msgs += self._handle_enemy_turns()
        self._update_all(msgs)

    def _update_fov(self):
        self.game_map.visible[:, :] = False
        self.fov.do_fov(self.player, self.game_map.visible)
        self.game_map.explored |= self.game_map.visible

    def _update_all(self, msgs):
        self._update_fov()
        self.gui.update(self.player, msgs)

    def _get_render_sorted_entities(self):
        return sorted(self.entities, key=lambda x: -x.render_order)

    def render(self):
        blt.clear_area(0, 0, config.MAP_WIDTH, config.MAP_HEIGHT)
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

    def game_over(self):
        self.event_handler = GameOverEventHandler()


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


if __name__ == "__main__":
    main()
