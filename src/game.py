# -*- coding: utf-8 -*-
import pygame
import sys
from config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, DEV_MODE
from src.constants import GameState
from src.level import LevelManager
from src.entities import Player, Mob
from src.data_manager import DataManager
from src.ui import FontManager, UIRenderer, GameRenderer
from src.input_handler import InputHandler
from src.editor import LevelEditor

pygame.init()


class Game:
    """Main Game Controller.
    
    Coordinates between input handling, logic updates, and rendering.
    Manages the overall GameState and player progression.
    """

    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pixel Art Maze Game")
        self.clock = pygame.time.Clock()

        self.data_manager = DataManager()
        self.level_manager = LevelManager(self.data_manager.load_custom_levels())
        self.input_handler = InputHandler()
        self.font_manager = FontManager()
        self.ui_renderer = UIRenderer(self.screen, self.font_manager)
        self.editor = LevelEditor(self.screen, self.font_manager, self.data_manager)

        self.player_stats = None
        self.current_level = 1
        self.player = None
        self.mobs = []
        self.game_renderer = None
        self.animation_frame = 0

        if DEV_MODE:
            self.pseudo = "Morpheus"
            self.player_stats = self.data_manager.get_player_stats(self.pseudo)
            self.state = GameState.MENU
        else:
            self.state = GameState.LOGIN
            self.pseudo = ""

    def start_level(self, level_id: int):
        """Initializes and starts a specific level.
        
        Args:
            level_id (int): The unique identifier of the level to load.
        """
        if self.level_manager.set_current_level(level_id):
            self.current_level = level_id
            level = self.level_manager.get_current_level()
            pygame.display.set_caption(f"Pixel Art Maze Game - {level.name}")
            
            # Init Player
            self.player = Player(level, start_x=level.start_x, start_y=level.start_y)
            
            # Init Mobs
            self.mobs = []
            for m_data in level.mobs_data:
                mob = Mob(
                    level, 
                    m_data["start_pos"][0], 
                    m_data["start_pos"][1], 
                    speed=m_data.get("speed", 0.05),
                    pattern=m_data.get("pattern", "horizontal"),
                    distance=m_data.get("distance", 3)
                )
                self.mobs.append(mob)
                
            self.game_renderer = GameRenderer(self.screen, self.font_manager, level)
            self.state = GameState.PLAYING

    def handle_events(self):
        """Gère les événements."""
        # 1. Gestion spécifique pour l'ÉDITEUR
        if self.state == GameState.EDITOR:
            res = self.editor.handle_events()
            if res == "QUIT":
                return False
            elif res == "MENU":
                # Recharger les niveaux pour inclure les nouveaux
                self.level_manager = LevelManager(self.data_manager.load_custom_levels())
                self.state = GameState.MENU
            return True

        # 2. Gestion pour les autres états via InputHandler
        running, next_state, updated_pseudo = self.input_handler.handle_events(self.state, self.pseudo, self.ui_renderer)
        self.pseudo = updated_pseudo

        if not running:
            return False

        # 3. Traitement des transitions d'état spéciales
        if isinstance(next_state, tuple) and next_state[0] == "START_LEVEL":
            self.start_level(next_state[1])
        elif next_state == GameState.MENU and self.state == GameState.LOGIN:
            # Premier login
            self.player_stats = self.data_manager.get_player_stats(self.pseudo)
            self.state = GameState.MENU
        elif next_state == GameState.PLAYING and self.state == GameState.MENU:
            self.start_level(1)
        elif next_state == GameState.MENU and self.state == GameState.WIN:
            if self.level_manager.has_next_level():
                self.start_level(self.level_manager.get_next_level_id())
            else:
                self.state = GameState.MENU
        else:
            self.state = next_state

        return True

    def handle_game_logic(self):
        """Gere la logique du jeu (mouvements, collisions)."""
        if self.state == GameState.PLAYING and self.player:
            # Mouvement joueur
            self.input_handler.handle_continuous_input(self.player)

            # Mouvement mobs
            for mob in self.mobs:
                mob.update()
                # Collision mob
                if mob.collides_with(self.player):
                    self.state = GameState.GAME_OVER
                    self.animation_frame = 0
                    self.data_manager.update_stats(self.pseudo, deaths=1)
                    self.player_stats = self.data_manager.get_player_stats(self.pseudo)

            # Victoire
            level = self.level_manager.get_current_level()
            if self.player.is_at(level.exit_x, level.exit_y):
                self.state = GameState.WIN
                self.data_manager.update_stats(self.pseudo, level_won=self.current_level)
                self.player_stats = self.data_manager.get_player_stats(self.pseudo)
        
        elif self.state == GameState.GAME_OVER:
            self.animation_frame += 1
            if self.animation_frame > 60: # ~1 seconde
                self.state = GameState.MENU

    def draw(self):
        """Rendu du jeu."""
        if self.state == GameState.LOGIN:
            self.ui_renderer.draw_login(self.pseudo)
        elif self.state == GameState.MENU:
            self.ui_renderer.draw_menu()
        elif self.state == GameState.LEVEL_SELECT:
            self.ui_renderer.draw_level_select(self.level_manager.get_all_levels_ids())
        elif self.state == GameState.STATS:
            self.ui_renderer.draw_stats(self.pseudo, self.player_stats)
        elif self.state == GameState.PLAYING and self.game_renderer and self.player:
            self.game_renderer.draw_game(self.player, self.mobs)
        elif self.state == GameState.WIN:
            has_next = self.level_manager.has_next_level()
            self.ui_renderer.draw_win(self.current_level, has_next)
        elif self.state == GameState.GAME_OVER:
            self.ui_renderer.draw_game_over(self.animation_frame)
        elif self.state == GameState.EDITOR:
            self.editor.draw()

        pygame.display.flip()

    def run(self):
        """Boucle principale."""
        running = True
        while running:
            running = self.handle_events()
            self.handle_game_logic()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
