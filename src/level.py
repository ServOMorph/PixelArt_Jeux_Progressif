import os
import json
import glob
from config import TILE_SIZE
from levels.levels_config import ALL_LEVELS


class Level:
    """Gere un niveau du jeu (labyrinthe)."""

    def __init__(self, data):
        self.id = data.get("id")
        self.name = data.get("name", f"Niveau {self.id}")
        self.maze = data.get("maze")
        self.width = len(self.maze[0])
        self.height = len(self.maze)
        self.start_x, self.start_y = data.get("start_pos", [1, 1])
        self.exit_x, self.exit_y = data.get("exit_pos", [self.width - 1, self.height - 1])
        self.mobs_data = data.get("mobs", [])
        self.colors = data.get("colors", {})

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

    def __init__(self, all_levels_data=None):
        self.levels = {}
        self.current_level_id = 1
        if all_levels_data:
            self.refresh_levels(all_levels_data)
        else:
            # Fallback sur l'import si rien n'est fourni (compatibilité)
            from levels.levels_config import ALL_LEVELS
            self.refresh_levels(ALL_LEVELS)

    def refresh_levels(self, all_levels_data):
        """Recharge tous les niveaux depuis une liste de dictionnaires."""
        self.levels = {}
        for level_data in all_levels_data:
            level_id = level_data.get("id")
            if level_id is not None:
                self.levels[level_id] = Level(level_data)

        if not self.levels:
            print("Attention: Aucun niveau trouvé lors du rafraîchissement")

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
        return self.levels.get(self.current_level_id)

    def has_next_level(self):
        """Verifie s'il existe un niveau suivant dans la liste triée."""
        sorted_ids = self.get_all_levels_ids()
        try:
            idx = sorted_ids.index(self.current_level_id)
            return idx < len(sorted_ids) - 1
        except ValueError:
            return False

    def get_next_level_id(self):
        """Retourne l'ID du niveau suivant dans la liste triée."""
        sorted_ids = self.get_all_levels_ids()
        try:
            idx = sorted_ids.index(self.current_level_id)
            if idx < len(sorted_ids) - 1:
                return sorted_ids[idx + 1]
        except ValueError:
            pass
        return self.current_level_id

    def get_all_levels_ids(self):
        """Retourne la liste des IDs de niveaux triés."""
        return sorted(self.levels.keys())

