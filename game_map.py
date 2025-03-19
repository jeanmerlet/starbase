import numpy as np
import pandas as pd
from procgen import Grid, RectRoom, Hallway
from entities import Actor, ThrownConsumable, InjectedConsumable, Equippable
from components import *
from ai import BaseAI, HostileEnemy, DoorAI
from tiles import *


class Map:
    TILE_ID = {
        0: Wall,
        1: Floor,
        2: AutoDoor,
        3: AutoDoor
    }
    ACTOR_DATA = pd.read_csv('./data/actors.tsv', sep='\t', index_col=0,
                             header=0)
    ITEM_DATA = pd.read_csv('./data/items.tsv', sep='\t', index_col=0,
                             header=0)

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = np.empty((width, height), dtype=object)
        self.opaque = np.full((width, height), fill_value=False)
        self.visible = np.full((width, height), fill_value=False)
        self.explored = np.full((width, height), fill_value=False)
        self.tiles_with_ai = []
        self.rooms = []

    def _get_start_xy(self):
        x = np.random.randint(self.width)
        y = np.random.randint(self.height)
        if isinstance(self.tiles[x, y], Floor):
            return x, y
        else:
            return self._get_start_xy()

    def in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self. height

    def is_adjacent(self, x1y1_coords, x2y2_coords):
        x1, y1 = x1y1_coords
        x2, y2 = x2y2_coords
        if abs(x1-x2) <= 1 and abs(y1-y2) <= 1:
            return True
        return False

    def _convert_grid_idx_to_tiles(self, x1, x2, y1, y2, grid_idx):
        for x in range(x1, x2):
            for y in range(y1, y2):
                idx = grid_idx[x - x1, y - y1]
                tile_class = self.TILE_ID[idx]
                tile = tile_class()
                if isinstance(tile, AutoDoor):
                    tile.ai = DoorAI(x, y)
                    tile.ai.door = tile
                    self.tiles_with_ai.append(tile)
                self.tiles[x, y] = tile
                if tile.opaque:
                    self.opaque[x, y] = True

    def _add_map_edge(self):
        self.tiles[:, 0] = MapEdge()
        self.tiles[:, self.height - 1] = MapEdge()
        self.tiles[0, :] = MapEdge()
        self.tiles[self.width - 1, :] = MapEdge()

    def _gen_tiles(self, gridx, gridy, grid_idx):
        for x in range(self.width):
            for y in range(self.height):
                self.tiles[x, y] = Space()
        self._add_map_edge()
        x1 = gridx
        y1 = gridy
        x2 = gridx + grid_idx.shape[0]
        y2 = gridy + grid_idx.shape[1]
        self._convert_grid_idx_to_tiles(x1, x2, y1, y2, grid_idx)

    def _define_room(self, x, y, checked):
        """(Rect)Rooms and hallways are defined by the top left
        and bottom right corners of their wall tiles. Hallways
        are rooms with width or height 1.
        """
        x1, y1 = x - 1, y - 1
        x2 = x + 1
        while not isinstance(self.tiles[x2, y], (Wall, Door)):
            x2 += 1
        y2 = y + 1
        while not isinstance(self.tiles[x, y2], (Wall, Door)):
            y2 += 1
        if x2 - x1 == 2 or y2 - y1 == 2:
            self.rooms.append(Hallway(x1, y1, x2, y2))
        else:
            self.rooms.append(RectRoom(x1, y1, x2, y2))
        checked[x1:x2+1, y1:y2+1] = True

    def _find_rooms(self):
        checked = np.full((self.width, self.height), fill_value=False)
        for x in range(self.width):
            for y in range(self.height):
                if checked[x, y]: continue
                if isinstance(self.tiles[x, y], Floor):
                    self._define_room(x, y, checked)
                else:
                    checked[x, y] = True

    #TODO: get sets of entities larger than size 1
    # (e.g. multiple skitterlings or robot and kevlar)
    # make another csv table for these sets
    # Use a rarity property for items.
    def _roll_actors(self):
        num_dist = [(1, 3), (1, 1)]
        dist = [0.8, 0.2]
        idx = np.random.choice(np.arange(len(dist)), p=dist)
        num_range = num_dist[idx]
        if num_range != 0:
            min_num, max_num = num_range
            num = np.random.randint(min_num, max_num + 1)
        else:
            num = 1
        name_set = [self.ACTOR_DATA.index[idx]] * num
        return name_set

    def _roll_items(self):
        dist = [0, 0, 1, 0, 0, 0]
        idx = np.random.choice(np.arange(len(dist)), p=dist)
        name_set = [self.ITEM_DATA.index[idx]]
        return name_set

    def _roll_entity_xy(self, room, entities):
        x = np.random.randint(room.x1+1, room.x2)
        y = np.random.randint(room.y1+1, room.y2)
        if np.any([ent.x == x and ent.y == y for ent in entities]):
            return self._roll_entity_xy(room, entities)
        else:
            return x, y

    def _get_empty_adjacent_xy(self, room, entities, x, y):
        adj_x = x + np.random.randint(-1, 2)
        adj_y = y + np.random.randint(-1, 2)
        if (isinstance(self.tiles[adj_x, adj_y], Wall) or
            np.any([ent.x == adj_x and ent.y == adj_y for ent in entities])):
                return self._get_empty_adjacent_xy(room, entities, x, y)
        else:
            return adj_x, adj_y

    def _get_entity_properties(self, name, data):
        props = {}
        for col in data.columns:
            props[col] = data.loc[name, col]
        return props

    def _get_actor_attacks(self, props):
        names = props['attacks'].split(',')
        max_ranges = props['range'].split(',')
        areas = props['area'].split(',')
        dice = props['damage'].split(',')
        att_types = props['att_type'].split(',')
        dam_types = props['dam_type'].split(',')
        melee_attacks, ranged_attacks = [], []
        for i in range(len(names)):
            if att_types[i] == 'melee':
                attack = MeleeAttack(names[i], dice[i], dam_types[i],
                                     max_ranges[i], areas[i])
                melee_attacks.append(attack)
            else:
                attack = RangedAttack(names[i], dice[i], dam_types[i],
                                      max_ranges[i], areas[i])
                ranged_attacks.append(attack)
        return melee_attacks, ranged_attacks

    def _create_actor_attributes(self, strength, agility, intellect, willpower):
        attributes = {
            'strength': strength,
            'agility': agility,
            'intellect': intellect,
            'willpower': willpower
        }
        return attributes

    def _create_actor_skills(self, melee, ranged, evasion):
        melee_skill = Skill('melee', melee, 'strength', 2, 'agility', 1)
        ranged_skill = Skill('ranged', ranged, 'agility', 2, 'intellect', 1)
        evasion = Skill('evasion', evasion, 'agility', 2, 'intellect', 1)
        skills = {
            'melee': melee_skill,
            'ranged': ranged_skill,
            'evasion': evasion
        }
        return skills

    def _spawn_actor(self, entities, name, props, x, y):
        hp = HitPoints(props['hp'], props['regen_rate'])
        shields = Shields(props['base_shp'], props['base_scr'],
                          props['base_scd'])
        melee_attacks, ranged_attacks = self._get_actor_attacks(props)
        combat = Combat(hp, shields, melee_attacks, ranged_attacks)
        ai = HostileEnemy()
        fov_radius = None
        inventory = Inventory()
        equipment = Equipment(None, None, None)
        strength, agility = props['strength'], props['agility']
        intellect, willpower = props['intellect'], props['willpower']
        attributes = self._create_actor_attributes(strength, agility,
                                                   intellect, willpower)
        melee, ranged = props['melee'], props['ranged']
        evasion = props['evasion']
        skills = self._create_actor_skills(melee, ranged, evasion)
        if pd.isna(props['corpse_graphic']):
            corpse_graphic = None
        else:
            corpse_graphic = props['corpse_graphic']
        xp = props['xp']
        entity = Actor(name, x, y, props['char'], props['color'],
                       props['graphic'], combat, ai, fov_radius, inventory,
                       equipment, attributes, skills, corpse_graphic, xp)
        entity.ai.entity = entity
        entity.combat.entity = entity
        entity.equipment.entity = entity
        entity.equipment.update_actor_stats()
        for name, skill in entity.skills.items():
            skill.entity = entity
        entities.add(entity)

    def _spawn_item(self, entities, name, props, x, y):
        if props['class'] == 'equippable':
            entity = Equippable(name, x, y, props['char'], props['color'],
                                props['graphic'], props['att_type'],
                                props['range'], props['area'],
                                props['damage'], props['dam_type'],
                                props['shp_bonus'], props['scr_bonus'],
                                props['scd_bonus'], props['slot_type'])
        elif props['class'] == 'consumable':
            subclass = props['subclass']
            if subclass == 'injected':
                entity = InjectedConsumable(name, x, y, props['char'],
                                           props['color'], props['graphic'],
                                           props['heal_amount'], props['verb'])
            elif subclass == 'thrown':
                entity = ThrownConsumable(name, x, y, props['char'],
                                          props['color'], props['graphic'],
                                          props['damage'], props['dam_type'],
                                          props['range'], props['area'],
                                          props['verb'])
        entities.add(entity)

    def _spawn_actors(self, entities, room, actors):
        for i, actor in enumerate(actors):
            props = self._get_entity_properties(actor, self.ACTOR_DATA)
            if i == 0:
                x, y = self._roll_entity_xy(room, entities)
            else:
                x, y = self._get_empty_adjacent_xy(room, entities, x, y)
            self._spawn_actor(entities, actor, props, x, y)

    def _spawn_items(self, entities, room, items):
        for item in items:
            props = self._get_entity_properties(item, self.ITEM_DATA)
            x, y = self._roll_entity_xy(room, entities)
            self._spawn_item(entities, item, props, x, y)

    def populate(self, entities):
        #TODO: modify size parameter
        for room in self.rooms:
            if isinstance(room, Hallway): continue
            if np.random.rand() > 0.25:
                actor_set = self._roll_actors()
                self._spawn_actors(entities, room, actor_set)
            if np.random.rand() > 0.5:
                item_set = self._roll_items()
                self._spawn_items(entities, room, item_set)

    def gen_map(self, gridw, gridh, block_size):
        grid = Grid(gridw, gridh, block_size)
        grid.create_blocks()
        gridx = (self.width - gridw) // 2
        gridy = (self.height - gridh) // 2
        self._gen_tiles(gridx, gridy, grid.tile_idx)
        self._find_rooms()

    def spawn_player(self):
        startx, starty = self._get_start_xy()
        hit_points = HitPoints(30, 0.1)
        shields = Shields(0, 0, 0)
        melee_attacks = [MeleeAttack('punch', '3d4', 'kinetic', 1, 0)]
        ranged_attacks = []
        combat = Combat(hit_points, shields, melee_attacks, ranged_attacks)
        ai = BaseAI()
        inventory = Inventory()
        equipment = Equipment(None, None, None)
        attributes = self._create_actor_attributes(5, 5, 5, 5)
        skills = self._create_actor_skills(50, 50, 10)
        player = Actor(name='player', x=startx, y=starty, char='@',
                       color='amber', graphic='[0xE009]', combat=combat, ai=ai,
                       fov_radius=7, inventory=inventory, equipment=equipment,
                       attributes=attributes, skills=skills,
                       corpse_graphic=None, xp=0)
        player.ai.entity = player
        player.combat.entity = player
        player.inventory.entity = player
        player.equipment.entity = player
        player.equipment.update_actor_stats()
        for name, skill in player.skills.items():
            skill.entity = player
        level = Level(1, 10, 0, 1000, 1.5)
        player.level = level
        return player
