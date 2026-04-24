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
    "black":        (5, 5, 16),      # Noir Cobalt
    "bg":           (10, 10, 30),    # Bleu Abysse
    "white":        (255, 255, 255),
    "wall":         (138, 43, 226),  # Violet Profond
    "wall_border":  (255, 100, 255),
    "path":         (15, 15, 45),    # Chemin plus sombre
    "player":       (0, 255, 255),   # Cyan
    "player_eye":   (255, 255, 0),   # Jaune
    "exit":         (255, 20, 147),  # Magenta
    "exit_border":  (255, 255, 255),
    "menu_bg":      (10, 10, 30),    # Bleu Abysse
    "mob":          (255, 140, 0),   # Orange Slime
    "mob_eye":      (255, 255, 0),   # Jaune
    "death_bg":     (80, 0, 40),     # Plus Magenta/Rouge
    "tree":         (34, 139, 34),
    "tree_top":     (0, 100, 0),
}
