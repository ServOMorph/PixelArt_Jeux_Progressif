# -*- coding: utf-8 -*-

class TileType:
    PATH = 0
    WALL = 1
    TREE = 2

TILE_PROPERTIES = {
    TileType.PATH: {
        "name": "Path",
        "walkable": True,
        "destructible": False,
        "color_key": "path"
    },
    TileType.WALL: {
        "name": "Wall",
        "walkable": False,
        "destructible": False,
        "color_key": "wall"
    },
    TileType.TREE: {
        "name": "Tree",
        "walkable": False,
        "destructible": True,
        "hp": 3,
        "color_key": "tree"
    }
}
