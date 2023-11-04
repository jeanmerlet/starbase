import actions
import numpy as np


class BaseAI:
    def get_action(self):
        NotImplementedError()


class DoorAI(BaseAI):
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.closed = True
        self.close_delay = np.random.randint(1, 4)
        self.turns_until_closed = 0

    def update(self, engine):
        if engine.is_adjacent_live_actor(self.x, self.y):
            self.open(engine)
        elif not self.closed:
            if self.turns_until_closed > 0:
                self.turns_until_closed -= 1
            else:
                entities = engine.get_entities_at_xy(self.x, self.y)
                if not entities:
                    self.close(engine)
        
    def open(self, engine):
        self.closed = False
        self.door.walkable = True
        self.door.tile = self.door.open_tile
        engine.game_map.opaque[self.x, self.y] = False
        self.turns_until_closed = self.close_delay

    def close(self, engine):
        self.closed = True
        self.door.walkable = False
        self.door.tile = self.door.closed_tile
        engine.game_map.opaque[self.x, self.y] = True


class HostileEnemy(BaseAI):
    def __init__(self):
        self.path = []
        self.turns_since_player_seen = 0

    def get_action(self, engine, target, visible, tiles):
        if not visible[self.entity.x, self.entity.y]:
            if not self.path:
                return actions.WaitAction()
            elif self.turns_since_player_seen > 0:
                self.turns_since_player_seen -= 1
                targetx, targety = self.path.pop(0)
                dx = targetx - self.entity.x
                dy = targety - self.entity.y
                return actions.MoveAction(dx, dy)
        elif target:
            return self._move_towards(engine, target, tiles)
        else:
            return actions.WaitAction()

    def _move_towards(self, engine, target, tiles):
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        distance = max(abs(dx), abs(dy))
        if distance > 1:
            #self.get_path_to_target(target.x, target.y)
            dx = 0 if dx == 0 else (1 if dx > 0 else -1)
            dy = 0 if dy == 0 else (1 if dy > 0 else -1)
            dest_x, dest_y = self.entity.x + dx, self.entity.y + dy
            if (tiles[dest_x, dest_y].walkable and not
                engine.get_blocking_entity_at_xy(dest_x, dest_y)):
                return actions.MoveAction(dx, dy)
            elif (tiles[dest_x, self.entity.y].walkable and not
                engine.get_blocking_entity_at_xy(dest_x, self.entity.y)):
                return actions.MoveAction(dx, 0)
            elif (tiles[self.entity.x, dest_y].walkable and not
                engine.get_blocking_entity_at_xy(self.entity.x, dest_y)):
                return actions.MoveAction(0, dy)
            else:
                return actions.WaitAction()
        else:
            return self._melee_attack(dx, dy)

    def _melee_attack(self, dx, dy):
        return actions.MeleeAction(dx, dy)
