from event_handlers import *
from entities import Item


class Engine:
    def __init__(self, event_handler, game_map, player, entities, fov, gui):
        self.event_handler = event_handler
        self.event_handlers = [event_handler]
        self.game_map = game_map
        self.player = player
        self.entities = entities
        self.fov = fov 
        self._update_fov()
        self.gui = gui 
        self.gui.update(self.player)

    def get_dist_sorted_entities(self, entities):
        key = lambda x: max(abs(self.player.x - x.x), abs(self.player.y - x.y))
        return sorted(entities, key=key)

    def handle_nonplayer_turns(self):
        if not isinstance(self.event_handler, MainEventHandler):
            return 
        visible = self.game_map.visible
        tiles = self.game_map.tiles
        entities = self.entities - {self.player}
        entities = self.get_dist_sorted_entities(entities)
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

    def get_ents_visible_from_xy(self, x, y):
        ents = []
        for ent in self.entities:
            if self.game_map.visible[ent.x, ent.y]:
                if not (x == ent.x and y == ent.y):
                    ents.append[ent]
        return ents

    def _update_event_handlers(self):
        self.event_handler = self.event_handlers[-1]

    def push_event_handler(self, event_handler):
        self.event_handlers.append(event_handler)
        self._update_event_handlers()

    def pop_event_handler(self):
        self.event_handlers.pop()
        self._update_event_handlers()
