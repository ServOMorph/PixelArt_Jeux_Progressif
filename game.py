# -*- coding: utf-8 -*-
import pygame
import sys
from config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from constants import GameState
from level import LevelManager
from player import Player
from ui import FontManager, UIRenderer, GameRenderer
from input_handler import InputHandler

pygame.init()


class Game:
    """Controleur principal du jeu."""

    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pixel Art Maze Game - Niveau 1")
        self.clock = pygame.time.Clock()

        self.level_manager = LevelManager()
        self.input_handler = InputHandler()
        self.font_manager = FontManager()
        self.ui_renderer = UIRenderer(self.screen, self.font_manager)

        self.state = GameState.MENU
        self.current_level = 1
        self.player = None
        self.game_renderer = None

    def start_level(self, level_id):
        """Demarre un niveau."""
        if self.level_manager.set_current_level(level_id):
            self.current_level = level_id
            level = self.level_manager.get_current_level()
            self.player = Player(level, start_x=1, start_y=1)
            self.game_renderer = GameRenderer(self.screen, self.font_manager, level)
            self.state = GameState.PLAYING

    def handle_events(self):
        """Gere les evenements."""
        running, new_state = self.input_handler.handle_events(self.state)

        if new_state == GameState.PLAYING and self.state == GameState.MENU:
            self.start_level(1)
        elif new_state == GameState.MENU and self.state == GameState.WIN:
            self.state = GameState.MENU
        else:
            self.state = new_state

        return running

    def handle_continuous_input(self):
        """Gere le mouvement continu."""
        if self.state == GameState.PLAYING and self.player:
            self.input_handler.handle_continuous_input(self.player)

            level = self.level_manager.get_current_level()
            if self.player.is_at(level.exit_x, level.exit_y):
                self.state = GameState.WIN

    def draw(self):
        """Rendu du jeu."""
        if self.state == GameState.MENU:
            self.ui_renderer.draw_menu()
        elif self.state == GameState.PLAYING and self.game_renderer and self.player:
            self.game_renderer.draw_game(self.player)
        elif self.state == GameState.WIN:
            self.ui_renderer.draw_win(self.current_level)

        pygame.display.flip()

    def run(self):
        """Boucle principale."""
        running = True
        while running:
            running = self.handle_events()
            self.handle_continuous_input()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
