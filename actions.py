class Action:
    def __init__(self):
        self.msgs = []

    def perform(self, engine, entity):
        raise NotImplementedError()


class QuitAction(Action):
    def __init__(self):
        super().__init__()

    def perform(self, engine, entity):
        raise SystemExit()


class WaitAction(Action):
    def __init__(self):
        super().__init__()

    def perform(self, engine, entity):
        return []


class DirectedAction(Action):
    def __init__(self, dx, dy):
        super().__init__()
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
            self.msgs.append('Nothing there.')
        else:
            dam = int(entity.combat.att - target.combat.armor)
            if dam > 0:
                self.msgs.append(f'{entity.name} hits {target.name} for {dam} damage.')
                target.combat.set_hp(target.combat.hp - dam)
            else:
                self.msgs.append(f'{entity.name} attacks {target.name} but does no damage.')
        return self.msgs


class MoveAction(DirectedAction):
    def perform(self, engine, entity):
        dest_x, dest_y = self._get_target_xy(entity)
        blocking_ent = engine.get_blocking_entity(dest_x, dest_y)
        if blocking_ent:
            self.msgs.append(f'{blocking_ent.name} is in the way (error)')
        elif not engine.game_map.in_bounds(dest_x, dest_y):
            self.msgs.append('out of bounds (error)')
        elif not engine.game_map.tiles[dest_x, dest_y].walkable:
            self.msgs.append("You can't go there.")
        else:
            entity.move(self.dx, self.dy)
        return self.msgs


class CheckAction(DirectedAction):
    def perform(self, engine, entity):
        dest_x, dest_y = self._get_target_xy(entity)
        if engine.get_blocking_entity(dest_x, dest_y):
            return MeleeAction(self.dx, self.dy).perform(engine, entity)
        else:
            return MoveAction(self.dx, self.dy).perform(engine, entity)
