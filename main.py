from bearlibterminal import terminal as blt
from input_handlers import EventHandler
from game_map import Map
from entities import Entity, Actor


class Engine:
    def __init__(self, event_handler, game_map, player, entities):
        self.event_handler = event_handler
        self.game_map = game_map
        self.player = player
        self.entities = entities

    def handle_event(self):
        event = blt.read()
        action = self.event_handler.dispatch(event)
        if action is not None:
            action.perform(self, self.player)

    def render(self):
        blt.clear()
        self.game_map.render()
        for ent in self.entities:
            ent.render()
        blt.refresh()


def main():
    screen_width = 80
    screen_height = 55
    map_width = 80
    map_height = 50
    gridw = 7
    gridh = 5
    block_size = 10
    padding = 1

    event_handler = EventHandler()
    game_map = Map(map_width, map_height)
    game_map.gen_map(gridw, gridh, block_size, padding)
    player = Actor(int(map_width / 2), int(map_height / 2), '@', 'blue')
    entities = {player}
    engine = Engine(event_handler, game_map, player, entities)

    blt.open()
    blt.set(f'window.size={screen_width}x{screen_height}')
    blt.set('palette.blue = 0,102,204')
    blt.set('palette.steel_floor = 160,160,160')
    blt.set('palette.steel_wall = 96,96,96')
    while True:
        engine.render()
        while blt.has_input():
            engine.handle_event()

if __name__ == "__main__":
    main()
