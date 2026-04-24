# -*- coding: utf-8 -*-
from config import TILE_SIZE


class Level:
    """Gere un niveau du jeu (labyrinthe)."""

    def __init__(self, maze_data, exit_x, exit_y):
        self.maze = maze_data
        self.width = len(maze_data[0])
        self.height = len(maze_data)
        self.exit_x = exit_x
        self.exit_y = exit_y

    def is_walkable(self, x, y):
        """Verifie si une tuile est accessible."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return self.maze[y][x] == 0

    def get_dimensions(self):
        """Retourne les dimensions du labyrinthe."""
        return self.width, self.height

    def get_pixel_dimensions(self):
        """Retourne les dimensions en pixels."""
        return self.width * TILE_SIZE, self.height * TILE_SIZE

    def get_tile(self, x, y):
        """Retourne la tuile a une position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.maze[y][x]
        return None


class LevelManager:
    """Gere les niveaux du jeu."""

    def __init__(self):
        self.levels = {}
        self._init_levels()
        self.current_level_id = 1

    def _init_levels(self):
        """Initialise tous les niveaux disponibles."""
        maze_1 = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]
        self.levels[1] = Level(maze_1, exit_x=15, exit_y=13)

    def get_level(self, level_id):
        """Retourne un niveau par son ID."""
        return self.levels.get(level_id)

    def set_current_level(self, level_id):
        """Definit le niveau actuel."""
        if level_id in self.levels:
            self.current_level_id = level_id
            return True
        return False

    def get_current_level(self):
        """Retourne le niveau actuel."""
        return self.levels[self.current_level_id]
