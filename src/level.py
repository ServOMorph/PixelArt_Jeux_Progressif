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

    def __init__(self, custom_levels=[]):
        self.levels = {}
        self.current_level_id = 1
        self._load_levels(custom_levels)

    def _load_levels(self, custom_levels=[]):
        """Charge tous les niveaux depuis config et niveaux personnalisés."""
        # Niveaux par défaut
        for level_data in ALL_LEVELS:
            level_id = level_data.get("id")
            if level_id:
                self.levels[level_id] = Level(level_data)

        # Niveaux personnalisés (IDs commencent à 100 pour éviter conflits)
        for level_data in custom_levels:
            level_id = level_data.get("id")
            if level_id:
                self.levels[level_id] = Level(level_data)

        if not self.levels:
            print("Attention: Aucun niveau trouvé")

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
        """Verifie s'il existe un niveau suivant."""
        return (self.current_level_id + 1) in self.levels

    def get_next_level_id(self):
        """Retourne l'ID du niveau suivant."""
        return self.current_level_id + 1

    def get_all_levels_ids(self):
        """Retourne la liste des IDs de niveaux triés."""
        return sorted(self.levels.keys())

