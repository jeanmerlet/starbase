from actions import MeleeAction, MoveAction, WaitAction


class BaseAI:
    def get_action(self):
        NotImplementedError()

    def get_path_to_target(self, dest_x, dest_y):
        pass


class HostileEnemy(BaseAI):
    def __init__(self):
        self.path = []
        self.turns_since_player_seen = 0

    def get_action(self, engine, target, visible, tiles):
        if not visible[self.entity.x, self.entity.y]:
            if not self.path:
                return WaitAction()
            elif self.turns_since_player_seen > 0:
                self.turns_since_player_seen -= 1
                targetx, targety = self.path.pop(0)
                dx = targetx - self.entity.x
                dy = targety - self.entity.y
                return MoveAction(dx, dy)
        elif target:
            return self._move_towards(engine, target, tiles)
        else:
            return WaitAction()

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
                return MoveAction(dx, dy)
            elif (tiles[dest_x, self.entity.y].walkable and not
                engine.get_blocking_entity_at_xy(dest_x, self.entity.y)):
                return MoveAction(dx, 0)
            elif (tiles[self.entity.x, dest_y].walkable and not
                engine.get_blocking_entity_at_xy(self.entity.x, dest_y)):
                return MoveAction(0, dy)
            else:
                return WaitAction()
        else:
            return self._melee_attack(dx, dy)

    def _melee_attack(self, dx, dy):
        return MeleeAction(dx, dy)
