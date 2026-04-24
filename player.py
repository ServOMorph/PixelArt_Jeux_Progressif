# -*- coding: utf-8 -*-
from config import TILE_SIZE


class Player:
    """Gere l'etat et le mouvement du joueur."""

    def __init__(self, maze, start_x=1, start_y=1, speed=0.15):
        self.maze = maze
        self.x = float(start_x)
        self.y = float(start_y)
        self.speed = speed
        self.tile_x = start_x
        self.tile_y = start_y
        self.start_x = start_x
        self.start_y = start_y

    def move(self, dx, dy):
        """Calcule la nouvelle position avec detection de collision."""
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed

        tile_x = int(new_x)
        tile_y = int(new_y)

        if self.maze.is_walkable(tile_x, tile_y):
            self.x = new_x
            self.y = new_y
            self.tile_x = tile_x
            self.tile_y = tile_y
            return True
        return False

    def reset(self):
        """Reinitialise la position du joueur."""
        self.x = float(self.start_x)
        self.y = float(self.start_y)
        self.tile_x = self.start_x
        self.tile_y = self.start_y

    def get_pixel_position(self):
        """Retourne la position en pixels."""
        return int(self.x) * TILE_SIZE, int(self.y) * TILE_SIZE

    def is_at(self, exit_x, exit_y):
        """Verifie si le joueur est a une position donnee."""
        return self.tile_x == exit_x and self.tile_y == exit_y
