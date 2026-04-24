# -*- coding: utf-8 -*-
"""
Global configuration constants for the game.
Includes screen dimensions, colors, and developer flags.
"""

DEV_MODE = True

WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
TILE_SIZE = 60
FPS = 60

COLORS = {
    "black":        (0, 0, 0),
    "bg":           (0, 0, 0),
    "white":        (255, 255, 255),
    "wall":         (138, 43, 226),
    "wall_border":  (255, 100, 255),
    "path":         (25, 25, 112),
    "player":       (0, 255, 255),
    "player_eye":   (255, 255, 0),
    "exit":         (255, 20, 147),
    "exit_border":  (255, 255, 255),
    "menu_bg":      (10, 10, 30),
    "mob":          (255, 69, 0),
    "mob_eye":      (255, 255, 255),
    "death_bg":     (50, 0, 0),
    "tree":         (34, 139, 34),
    "tree_top":     (0, 100, 0),
}
