# -*- coding: utf-8 -*-
from mobs.patrol import PatrolMob
from mobs.chaser import ChaserMob
from mobs.shooter import ShooterMob

def create_mob(m_data, maze):
    """
    Crée une instance de mob selon les données de configuration.
    
    Args:
        m_data (dict): Données du mob (pos, speed, pattern, etc.)
        maze: L'instance du labyrinthe pour les collisions
    """
    pattern = m_data.get("pattern", "horizontal")
    start_x, start_y = m_data["start_pos"]
    speed = m_data.get("speed", 0.08)
    
    if pattern == "chaser":
        return ChaserMob(maze, start_x, start_y, speed)
    elif pattern == "shooter":
        # Utilise speed comme vitesse du projectile ou délai (ici on garde défaut pour l'instant)
        delay = m_data.get("distance", 120) # On réutilise distance comme délai pour éviter de changer schéma
        return ShooterMob(maze, start_x, start_y, speed, shoot_delay=delay)
    else:
        distance = m_data.get("distance", 3)
        return PatrolMob(maze, start_x, start_y, speed, pattern, distance)
