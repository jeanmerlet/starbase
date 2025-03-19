from bearlibterminal import terminal as blt
# /home/jeanmerlet/miniconda3/envs/dungeon/lib/python3.11/site-packages/bearlibterminal/terminal.py
from event_handlers import MainEventHandler
from game_map import Map
from fov import FieldOfView
from display import DisplayManager, Viewport, GUI
from animation import AnimationManager
from engine import Engine
import config


#TODO: add wizmode (view entire map, spawn entities, etc.)
class Game:
    def __init__(self):
        event_handler = MainEventHandler()
        game_map = Map(config.MAP_WIDTH, config.MAP_HEIGHT)
        game_map.gen_map(config.GRIDW, config.GRIDH, config.BLOCK_SIZE)
        player = game_map.spawn_player()
        entities = {player}
        game_map.populate(entities)
        fov = FieldOfView(game_map.opaque)
        viewport = Viewport(0, 0, config.VIEWPORT_WIDTH, config.VIEWPORT_HEIGHT)
        gui = GUI(player.combat.hit_points.hp, player.combat.hit_points.max_hp,
                  player.combat.shields.hp, player.combat.shields.max_hp)
        animation_manager = AnimationManager()
        display_manager = DisplayManager(viewport, gui, animation_manager)
        self.engine = Engine(event_handler, game_map, player, entities, fov,
                             display_manager)
        blt.open()
        config.set_blt_settings()

    def run(self):
        self.engine.running = True
        while self.engine.running:
            self.engine.render()
            if blt.has_input():
                self.engine.event_handler.handle_event(self.engine)
        blt.close()
        Raise SystemExit()


if __name__ == "__main__":
    game = Game()
    game.run()
