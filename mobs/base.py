# -*- coding: utf-8 -*-
from src.entities import Entity

class MobBase(Entity):
    """Classe de base pour tous les types de mobs."""
    def __init__(self, maze, start_x, start_y, speed):
        super().__init__(maze, start_x, start_y, speed)
        self.origin_x = start_x
        self.origin_y = start_y

    def update(self, player_pos=None):
        """À implémenter dans les sous-classes."""
        pass

    def collides_with(self, player):
        """Vérifie la collision avec le joueur."""
        dist = ((self.x - player.x)**2 + (self.y - player.y)**2)**0.5
        return dist < 0.7
