# -*- coding: utf-8 -*-
"""
Standalone launcher for the Level Editor.
Allows creating and saving levels without running the full game.
"""
import pygame
import sys
from config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from src.constants import GameState
from src.data_manager import DataManager
from src.ui import FontManager
from src.editeur.core import LevelEditor

def run_editor():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Pixel Art Maze Editor")
    clock = pygame.time.Clock()

    data_manager = DataManager()
    font_manager = FontManager()
    editor = LevelEditor(screen, font_manager, data_manager)

    running = True
    while running:
        res = editor.handle_events()
        if res == "QUIT":
            running = False
        elif res == "MENU":
            # On quitte l'éditeur (mais ici on ferme l'app)
            running = False
        
        editor.draw()
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run_editor()
