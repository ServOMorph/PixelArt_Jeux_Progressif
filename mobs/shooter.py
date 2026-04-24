# -*- coding: utf-8 -*-
import math
import pygame
from mobs.base import MobBase

class Projectile:
    """Projectile tiré par un ShooterMob."""
    def __init__(self, maze, x, y, target_x, target_y, speed=0.1):
        self.maze = maze
        self.x = x
        self.y = y
        self.speed = speed
        
        # Calcul de la direction vers le joueur
        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 0:
            self.vx = (dx / dist) * speed
            self.vy = (dy / dist) * speed
        else:
            self.vx, self.vy = 0, 0
            
        self.alive = True

    def update(self):
        self.x += self.vx
        self.y += self.vy
        
        # Collision murs
        if not self.maze.is_walkable(int(self.x + 0.5), int(self.y + 0.5)):
            self.alive = False

    def collides_with(self, player):
        dist = math.sqrt((self.x - player.x)**2 + (self.y - player.y)**2)
        return dist < 0.6

class ShooterMob(MobBase):
    """Ennemi statique qui tire des missiles."""
    def __init__(self, maze, start_x, start_y, speed=0.08, shoot_delay=120):
        # Ici speed ne sert pas au mouvement mais peut être passé
        super().__init__(maze, start_x, start_y, speed)
        self.shoot_delay = shoot_delay
        self.timer = 0

    def update(self, player_pos=None):
        if not player_pos:
            return None
            
        self.timer += 1
        if self.timer >= self.shoot_delay:
            self.timer = 0
            px, py = player_pos
            return Projectile(self.maze, self.x, self.y, px, py)
        
        return None
