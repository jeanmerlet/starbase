import numpy as np
import pandas as pd
from procgen import Grid, RectRoom, Hallway
from entities import Actor, HealingConsumable, Equippable
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
    ENT_DATA = pd.read_csv('./data/entities.tsv', sep='\t', index_col=0,
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

    def _roll_entities(self):
        #TODO: get sets of entities larger than size 1
        # (e.g. multiple skitterlings or robot and kevlar)
        # make another csv table for these sets
        # Use a rarity property for items.
        if np.random.rand() < 0.25: return None
        dist = [0.35, 0.15, 0, 0.1, 0.2, 0, 0.2]
        idx = np.arange(len(dist))
        name_set = np.random.choice(self.ENT_DATA.index, size=1, p=dist)
        return name_set

    def _roll_entity_xy(self, room, entities):
        x = np.random.randint(room.x1+1, room.x2)
        y = np.random.randint(room.y1+1, room.y2)
        if np.any([ent.x == x and ent.y == y for ent in entities]):
            return self._roll_entity_xy(room, entities)
        else:
            return x, y

    def _get_entity_properties(self, name):
        props = {}
        for col in self.ENT_DATA.columns:
            if col == 'class':
                ent_class = self.ENT_DATA.loc[name, col]
            else:
                props[col] = self.ENT_DATA.loc[name, col]
        return ent_class, props

    def _get_actor_attacks(self, props):
        names = props['attacks'].split(',')
        dice = props['damage'].split(',')
        types = props['dam_type'].split(',')
        attacks = []
        for i in range(len(names)):
            attack = Attack(names[i], dice[i], types[i])
            attacks.append(attack)
        return attacks

    def _spawn_actor(self, name, props, x, y):
        hp = HitPoints(props['hp'], props['regen_rate'])
        shields = Shields(props['base_shp'], props['base_scr'],
                          props['base_scd'])
        attacks = self._get_actor_attacks(props)
        combat = Combat(hp, shields, attacks)
        ai = HostileEnemy()
        fov_radius = None
        inventory = Inventory()
        equipment = Equipment(None, None, None)
        entity = Actor(name, x, y, props['char'], props['color'],
                       props['graphic'], combat, ai, fov_radius, inventory,
                       equipment)
        entity.ai.entity = entity
        entity.equipment.entity = entity
        entity.equipment.update_actor_stats()
        return entity

    def _spawn_consumable(self, name, props, x, y):
        subclass = props['subclass']
        if subclass == 'healing':
            entity = HealingConsumable(name, x, y, props['char'],
                                       props['color'], props['graphic'],
                                       props['heal_amount'])
        return entity

    def _spawn_equippable(self, name, props, x, y):
        entity = Equippable(name, x, y, props['char'], props['color'],
                            props['graphic'], props['damage'],
                            props['dam_type'], props['shp_bonus'],
                            props['scr_bonus'], props['scd_bonus'],
                            props['slot_type'])
        return entity

    def _spawn_entity(self, entities, room, name):
        x, y = self._roll_entity_xy(room, entities)
        ent_class, props = self._get_entity_properties(name)
        if ent_class == 'actor':
            entity = self._spawn_actor(name, props, x, y)
        if ent_class == 'consumable':
            entity = self._spawn_consumable(name, props, x, y)
        elif ent_class == 'equippable':
            entity = self._spawn_equippable(name, props, x, y)
        entities.add(entity)

    def populate(self, entities):
        #TODO: modify size parameter
        for room in self.rooms:
            if isinstance(room, Hallway): continue
            name_set = self._roll_entities()
            if name_set is not None:
                for name in name_set:
                    self._spawn_entity(entities, room, name)

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
        attacks = [Attack('punch', '3d4', 'kinetic')]
        combat = Combat(hit_points, shields, attacks)
        ai = BaseAI()
        inventory = Inventory()
        equipment = Equipment(None, None, None)
        player = Actor(name='player', x=startx, y=starty, char='@',
                       color='amber', graphic=None, combat=combat, ai=ai,
                       fov_radius=7, inventory=inventory, equipment=equipment)
        player.ai.entity = player
        player.inventory.entity = player
        player.equipment.entity = player
        player.equipment.update_actor_stats()
        return player
