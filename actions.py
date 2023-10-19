class Action:
    def perform(self, engine, entity):
        raise NotImplementedError()


class QuitAction(Action):
    def perform(self, engine, entity):
        raise SystemExit()


class WaitAction(Action):
    def perform(self, engine, entity):
        pass


class DirectedAction(Action):
    def __init__(self, dx, dy):
        self.dx = dx
        self.dy = dy

    def perform(self, engine, entity):
        raise NotImplementedError()

    def _get_target_xy(self, entity):
        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy
        return dest_x, dest_y


class MeleeAction(DirectedAction):
    def perform(self, engine, entity):
        dest_x, dest_y = self._get_target_xy(entity)
        target = engine.get_blocking_entity(dest_x, dest_y)
        if not target:
            print('nobody there')
        dam = entity.combat.att - target.combat.armor
        if dam > 0:
            print(f'{entity.name} wallops {target.name} for {dam} damage.')
            target.combat.set_hp(target.combat.hp - dam)
        else:
            print(f'{entity.name} attacks {target.name} but does no damage.')


class MoveAction(DirectedAction):
    def perform(self, engine, entity):
        dest_x, dest_y = self._get_target_xy(entity)
        blocking_ent = engine.get_blocking_entity(dest_x, dest_y)
        if blocking_ent:
            print(f'blocking {blocking_ent.name}')
        elif not engine.game_map.in_bounds(dest_x, dest_y):
            print('out of bounds')
        elif not engine.game_map.tiles[dest_x, dest_y].walkable:
            print('not walkable')
        else:
            entity.move(self.dx, self.dy)


class CheckAction(DirectedAction):
    def perform(self, engine, entity):
        dest_x, dest_y = self._get_target_xy(entity)
        if engine.get_blocking_entity(dest_x, dest_y):
            return MeleeAction(self.dx, self.dy).perform(engine, entity)
        else:
            return MoveAction(self.dx, self.dy).perform(engine, entity)
