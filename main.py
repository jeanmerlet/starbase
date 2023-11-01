from bearlibterminal import terminal as blt
# /home/jeanmerlet/miniconda3/envs/dungeon/lib/python3.11/site-packages/bearlibterminal
from event_handlers import MainEventHandler
from game_map import Map
from fov import FieldOfView
from display import GUI
from engine import Engine
import config


#TODO: add wizmode for starting game with all entities renderered
class Game:
    def __init__(self):
        event_handler = MainEventHandler()
        game_map = Map(config.MAP_WIDTH, config.MAP_HEIGHT)
        game_map.gen_map(config.GRIDW, config.GRIDH, config.BLOCK_SIZE)
        player = game_map.spawn_player()
        entities = {player}
        game_map.populate(entities)
        fov = FieldOfView(game_map.opaque)
        gui = GUI(player.combat.hit_points.hp, player.combat.hit_points.max_hp,
                  player.combat.shields.hp, player.combat.shields.max_hp)
        self.engine = Engine(event_handler, game_map, player, entities, fov,
                             gui)

    def initialize(self):
        blt.open()
        config.set_blt_settings()

    def run(self):
        while True:
            self.engine.render()
            if blt.has_input():
                self.engine.event_handler.handle_event(self.engine)
                self.engine.update()


if __name__ == "__main__":
    game = Game()
    game.initialize()
    game.run()
