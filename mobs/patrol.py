# -*- coding: utf-8 -*-
from mobs.base import MobBase

class PatrolMob(MobBase):
    """Ennemi qui patrouille horizontalement ou verticalement."""
    def __init__(self, maze, start_x, start_y, speed=0.08, pattern="horizontal", distance=3):
        super().__init__(maze, start_x, start_y, speed)
        self.pattern = pattern
        self.distance = distance
        self.direction = 1

    def update(self, player_pos=None):
        if self.pattern == "horizontal":
            new_x = self.x + self.speed * self.direction
            if abs(new_x - self.origin_x) > self.distance or not self.maze.is_walkable(int(new_x + (0.5 if self.direction > 0 else 0)), int(self.y)):
                self.direction *= -1
            else:
                self.x = new_x
        elif self.pattern == "vertical":
            new_y = self.y + self.speed * self.direction
            if abs(new_y - self.origin_y) > self.distance or not self.maze.is_walkable(int(self.x), int(new_y + (0.5 if self.direction > 0 else 0))):
                self.direction *= -1
            else:
                self.y = new_y
        
        self.tile_x = int(self.x + 0.5)
        self.tile_y = int(self.y + 0.5)
