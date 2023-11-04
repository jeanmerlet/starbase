from event_handlers import *
from entities import Item, Actor
from tiles import AutoDoor


class Engine:
    def __init__(self, event_handler, game_map, player, entities, fov,
                 viewport, gui):
        self.event_handler = event_handler
        self.event_handlers = [event_handler]
        self.game_map = game_map
        self.player = player
        self.entities = entities
        self.fov = fov 
        self.viewport = viewport
        self.gui = gui 
        self.gui.update(self.player)
        self._update()

    def get_dist_sorted_entities(self, entities):
        key = lambda x: max(abs(self.player.x - x.x), abs(self.player.y - x.y))
        return sorted(entities, key=key)

    def handle_nonplayer_turns(self):
        visible = self.game_map.visible
        tiles = self.game_map.tiles
        entities = self.entities - {self.player}
        entities = self.get_dist_sorted_entities(entities)
        for entity in entities:
            if entity.ai: 
                target = self.player if self.player.is_alive() else None
                action = entity.ai.get_action(self, target, visible, tiles)
                action.perform(self, entity)
        self._update()

    def _update_fov(self):
        self.game_map.visible[:, :] = False
        self.fov.do_fov(self.player, self.game_map.visible)
        self.game_map.explored |= self.game_map.visible

    def _update(self):
        for tile in self.game_map.tiles_with_ai:
            tile.ai.update(self)
        self._update_fov()
        self.player.combat.tick()
        self.gui.update(self.player)

    def _get_render_sorted_entities(self, entities):
        return sorted(entities, key=lambda x: -x.render_order)

    def render(self):
        entities = self._get_render_sorted_entities(self.entities)
        self.viewport.render(self.game_map, entities, self.player)
        self.gui.render()
        blt.refresh()

    def get_entities_at_xy(self, x, y, visible=False):
        entities = []
        for ent in self.entities:
            if ent.x == x and ent.y == y:
                if visible:
                    if self.game_map.visible[x, y]:
                        entities.append(ent)
                else:
                    entities.append(ent)
        return entities

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

    def get_hostile_ents_visible_from_xy(self, x, y):
        ents = []
        for ent in self.entities:
            if self.game_map.visible[ent.x, ent.y]:
                if (isinstance(ent, Actor) and ent.ai and
                    isinstance(ent.ai, HostileEnemy)):
                    ents.append(ent)
        return ents

    def is_adjacent_live_actor(self, x, y):
        coord_pairs = {(x+i, y+j) for i in range(-1, 2) for j in range(-1, 2)}
        actors = []
        for ent in self.entities:
            if (isinstance(ent, Actor) and ent.is_alive() and
                (ent.x, ent.y) in coord_pairs):
                return True
        return False

    def get_adjacent_autodoors(self, x, y):
        coords = {(x+i, y+j) for i in range(-1, 2) for j in range(-1, 2)}
        autodoors = []
        for coord in coords - {x, y}:
            tile = self.game_map.tiles[coord]
            if isinstance(tile, AutoDoor):
                autodoors.append(tile)
        return autodoors

    def _update_event_handlers(self):
        self.event_handler = self.event_handlers[-1]

    def push_event_handler(self, event_handler):
        self.event_handlers.append(event_handler)
        self._update_event_handlers()

    def pop_event_handler(self):
        self.event_handlers.pop()
        self._update_event_handlers()
