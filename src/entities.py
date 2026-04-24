# -*- coding: utf-8 -*-
import pygame
from config import TILE_SIZE

class Entity:
    """Classe de base pour les entites mobiles."""
    def __init__(self, maze, start_x, start_y, speed):
        self.maze = maze
        self.x = float(start_x)
        self.y = float(start_y)
        self.speed = speed
        self.tile_x = int(start_x)
        self.tile_y = int(start_y)

    def get_pixel_position(self, offset_x=0, offset_y=0):
        """Retourne la position en pixels pour le rendu."""
        return (
            offset_x + self.x * TILE_SIZE,
            offset_y + self.y * TILE_SIZE
        )

class Player(Entity):
    """Gere l'etat et le mouvement du joueur."""
    def __init__(self, maze, start_x=1, start_y=1, speed=0.15):
        super().__init__(maze, start_x, start_y, speed)
        self.start_x = start_x
        self.start_y = start_y

    def move(self, dx, dy):
        """Calcule la nouvelle position avec detection de collision."""
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed

        # Verifier les coins pour une collision plus fluide
        # On verifie les 4 coins de la boîte de collision du joueur (un peu plus petite que la tuile)
        margin = 0.2
        checks = [
            (new_x + margin, new_y + margin),
            (new_x + 1 - margin, new_y + margin),
            (new_x + margin, new_y + 1 - margin),
            (new_x + 1 - margin, new_y + 1 - margin)
        ]

        if all(self.maze.is_walkable(int(cx), int(cy)) for cx, cy in checks):
            self.x = new_x
            self.y = new_y
            self.tile_x = int(self.x + 0.5)
            self.tile_y = int(self.y + 0.5)
            return True
        return False

    def reset(self):
        self.x = float(self.start_x)
        self.y = float(self.start_y)
        self.tile_x = int(self.x)
        self.tile_y = int(self.y)

    def is_at(self, target_x, target_y):
        return int(self.x + 0.5) == target_x and int(self.y + 0.5) == target_y
