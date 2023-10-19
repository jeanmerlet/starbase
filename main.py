from bearlibterminal import terminal as blt
from event_handler import EventHandler
from game_map import Map
from entities import Entity, Actor
from fov import FieldOfView as Fov


class Engine:
    def __init__(self, event_handler, game_map, player, entities, fov):
        self.event_handler = event_handler
        self.game_map = game_map
        self.player = player
        self.entities = entities
        self.fov = fov
        self._update_fov()

    def _handle_enemy_turns(self):
        target = self.player
        visible = self.game_map.visible
        tiles = self.game_map.tiles
        for entity in self.entities - {self.player}:
            if entity.ai:
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

    def _get_render_sorted_entities(self):
        return sorted(self.entities, key=lambda x: -x.render_order)

    def render(self):
        blt.clear()
        self.game_map.render(blt)
        for ent in self._get_render_sorted_entities():
            if self.game_map.visible[ent.x, ent.y]:
                ent.render(blt)
        blt.refresh()

    def get_blocking_entity(self, x, y):
        for ent in self.entities:
            if ent.blocking and ent.x == x and ent.y == y:
                return ent
        return None


def main():
    screen_width = 160
    screen_height = 55
    map_width = 160
    map_height = 50
    gridw = 100
    gridh = 40
    block_size = 20
    padding = 1

    event_handler = EventHandler()
    game_map = Map(map_width, map_height)
    game_map.gen_map(gridw, gridh, block_size)
    player = game_map.create_player()
    entities = {player}
    game_map.populate(entities)
    fov = Fov(game_map.opaque)
    engine = Engine(event_handler, game_map, player, entities, fov)

    blt.open()
    blt.set(f'window.size={screen_width}x{screen_height}')
    blt.set('palette.blue = 0,102,204')
    blt.set('palette.l_stl = 160,160,160')
    blt.set('palette.d_stl = 32,32,32')
    while True:
        engine.render()
        while blt.has_input():
            engine.handle_event()


if __name__ == "__main__":
    main()
