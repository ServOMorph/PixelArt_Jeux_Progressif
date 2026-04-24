# -*- coding: utf-8 -*-
from mobs.base import MobBase

class ChaserMob(MobBase):
    """Ennemi qui poursuit activement le joueur."""
    def __init__(self, maze, start_x, start_y, speed=0.04):
        super().__init__(maze, start_x, start_y, speed)

    def update(self, player_pos=None):
        if not player_pos:
            return

        px, py = player_pos
        dx = px - self.x
        dy = py - self.y
        dist = (dx**2 + dy**2)**0.5
        
        if dist > 0.1:
            vx = (dx / dist) * self.speed
            vy = (dy / dist) * self.speed
            
            # Test collision simple
            if self.maze.is_walkable(int(self.x + vx + (0.5 if vx > 0 else -0.1)), int(self.y)):
                self.x += vx
            if self.maze.is_walkable(int(self.x), int(self.y + vy + (0.5 if vy > 0 else -0.1))):
                self.y += vy
        
        self.tile_x = int(self.x + 0.5)
        self.tile_y = int(self.y + 0.5)
