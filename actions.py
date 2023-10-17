class Action:
    def perform(self, engine, entity):
        pass


class QuitAction(Action):
    def perform(self, engine, entity):
        raise SystemExit()


class MoveAction(Action):
    def __init__(self, dx, dy):
        super().__init__()
        self.dx = dx
        self.dy = dy

    def perform(self, engine, entity):
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy
        if not engine.game_map.in_bounds(dest_x, dest_y):
            print('out of bounds')
        elif not engine.game_map.tiles[dest_x, dest_y].walkable:
            print('not walkable')
        else:
            entity.move(self.dx, self.dy)
            
