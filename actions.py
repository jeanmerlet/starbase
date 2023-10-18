class Action:
    def perform(self, engine, entity):
        pass


class QuitAction(Action):
    def perform(self, engine, entity):
        raise SystemExit()


class MoveAction(Action):
    def __init__(self, dx, dy):
        self.dx = dx
        self.dy = dy

    def perform(self, engine, entity):
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy
        blocking_ent = engine.get_blocking_entity(dest_x, dest_y)
        if not engine.game_map.in_bounds(dest_x, dest_y):
            print('out of bounds')
        elif not engine.game_map.tiles[dest_x, dest_y].walkable:
            print('not walkable')
        elif blocking_ent:
            print(f'{blocking_ent.name} in the way')
        else:
            entity.move(self.dx, self.dy)
