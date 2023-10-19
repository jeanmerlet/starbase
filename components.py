import numpy as np
from actions import Action, MeleeAction, MoveAction, WaitAction


class Combat:
    def __init__(self, hp, armor, att):
        self.max_hp = hp
        self.hp = hp
        self.armor = armor
        self.att = att

    def set_hp(self, value):
        self.hp = min(value, self.max_hp)


class BaseAI(Action):
    def perform(self):
        pass

    def get_path_to_target(self, dest_x, dest_y):
        pass


class HostileEnemy(BaseAI):
    def __init__(self):
        self.path = []
        self.turns_since_player_seen = 0

    def perform(self, target, visible, tiles):
        if not visible[self.entity.x, self.entity.y]:
            if not self.path:
                return WaitAction()
            elif self.turns_since_player_seen > 0:
                self.turns_since_player_seen -= 1
                targetx, targety = self.path.pop(0)
                dx = targetx - self.entity.x
                dy = targety - self.entity.y
                return MoveAction(dx, dy)
        else:
            return self._move_towards(target, tiles)

    def _move_towards(self, target, tiles):
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        distance = max(abs(dx), abs(dy))
        if distance > 1:
            #self.get_path_to_target(target.x, target.y)
            dx = 0 if dx == 0 else (1 if dx > 0 else -1)
            dy = 0 if dy == 0 else (1 if dy > 0 else -1)
            if tiles[self.entity.x + dx, self.entity.y + dy].walkable:
                return MoveAction(dx, dy)
            elif tiles[self.entity.x + dx, self.entity.y].walkable:
                return MoveAction(dx, 0)
            elif tiles[self.entity.x, self.entity.y + dy].walkable:
                return MoveAction(0, dy)
            else:
                return WaitAction()
        else:
            return self._melee_attack(dx, dy)

    def _melee_attack(self, dx, dy):
        return MeleeAction(dx, dy)




