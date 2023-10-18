from bearlibterminal import terminal as blt
from input_handlers import EventHandler
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
        self.update_fov()

    def handle_event(self):
        event = blt.read()
        action = self.event_handler.dispatch(event)
        if action is not None:
            action.perform(self, self.player)
        self.update_fov()

    def render(self):
        blt.clear()
        self.game_map.render(blt)
        for ent in self.entities:
            if self.game_map.visible[ent.x, ent.y]:
                ent.render(blt)
        blt.refresh()

    def update_fov(self):
        self.game_map.visible[:, :] = False
        self.fov.do_fov(self.player, self.game_map.visible)
        self.game_map.explored |= self.game_map.visible

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
    gridw = 10
    gridh = 5
    block_size = 10
    padding = 1

    event_handler = EventHandler()
    game_map = Map(map_width, map_height)
    game_map.gen_map(gridw, gridh, block_size, padding)
    x, y = game_map.get_start()
    player = Actor('player', x, y, '@', 'amber', True, 8)
    entities = [player]
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
