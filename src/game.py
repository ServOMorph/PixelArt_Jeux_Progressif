# -*- coding: utf-8 -*-
import pygame
import sys
from config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, DEV_MODE
from src.constants import GameState
from src.level import LevelManager
from src.entities import Player
from mobs import create_mob
from src.data_manager import DataManager
from src.ui import FontManager, UIRenderer, GameRenderer
from src.input_handler import InputHandler
from src.editeur.core import LevelEditor

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
        self.game_renderer = None
        self.animation_frame = 0
        self.is_testing = False
        self.projectiles = []

        if DEV_MODE:
            self.pseudo = "Morpheus"
            self.player_stats = self.data_manager.get_player_stats(self.pseudo)
            self.state = GameState.MENU
        else:
            self.state = GameState.LOGIN
            self.pseudo = ""

    def start_level(self, level_id: int):
        """Initializes and starts a specific level with error handling."""
        try:
            if self.level_manager.set_current_level(level_id):
                self.current_level = level_id
                level = self.level_manager.get_current_level()
                if not level or not level.maze:
                    print(f"Erreur: Données du niveau {level_id} invalides")
                    self.state = GameState.MENU
                    return

                pygame.display.set_caption(f"Pixel Art Maze Game - {level.name}")
                
                # Init Player
                self.player = Player(level, start_x=level.start_x, start_y=level.start_y)
                
                # Init Mobs
                self.mobs = []
                for m_data in level.mobs_data:
                    mob = create_mob(m_data, level)
                    self.mobs.append(mob)
                    
                self.projectiles = []
                self.game_renderer = GameRenderer(self.screen, self.font_manager, level)
                self.state = GameState.PLAYING
            else:
                print(f"Erreur: Niveau {level_id} non trouvé")
                self.state = GameState.MENU
        except Exception as e:
            print(f"CRASH lors du chargement du niveau {level_id}: {e}")
            import traceback
            traceback.print_exc()
            self.state = GameState.MENU

    def handle_events(self):
        """Gère les événements."""
        # 1. Gestion spécifique pour l'ÉDITEUR
        if self.state == GameState.EDITOR:
            res = self.editor.handle_events()
            if res == "QUIT":
                return False
            elif res == "MENU":
                # Recharger les niveaux (y compris ceux de levels_config.py rafraîchis)
                all_levels = self.data_manager.load_custom_levels()
                self.level_manager.refresh_levels(all_levels)
                self.state = GameState.MENU
            elif res == "TEST":
                data = self.editor.get_current_level_data()
                self.start_test_level(data)
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
            # S'assurer que les niveaux sont à jour au login
            self.level_manager.refresh_levels(self.data_manager.load_custom_levels())
            self.state = GameState.MENU
        elif next_state == GameState.PLAYING and self.state == GameState.MENU:
            # On lance le premier niveau disponible
            all_ids = self.level_manager.get_all_levels_ids()
            if all_ids:
                self.start_level(all_ids[0])
            else:
                self.state = GameState.MENU
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
                spawn = mob.update(player_pos=(self.player.x, self.player.y))
                if spawn:
                    self.projectiles.append(spawn)

                # Collision mob direct
                if mob.collides_with(self.player):
                    self._handle_player_death()

            # Mouvement projectiles
            for p in self.projectiles[:]:
                p.update()
                if not p.alive:
                    self.projectiles.remove(p)
                elif p.collides_with(self.player):
                    self.projectiles.remove(p)
                    self._handle_player_death()

            # Victoire
            level = self.player.maze # En mode test, c'est l'objet Level passé directement
            if self.player.is_at(level.exit_x, level.exit_y):
                self.data_manager.update_stats(self.pseudo, level_won=self.current_level)
                self.player_stats = self.data_manager.get_player_stats(self.pseudo)
                
                if self.is_testing:
                    self.state = GameState.EDITOR
                    self.is_testing = False
                else:
                    self.state = GameState.WIN
        
        elif self.state == GameState.GAME_OVER:
            self.animation_frame += 1
            if self.animation_frame > 60: # ~1 seconde
                self.state = GameState.MENU

    def start_test_level(self, level_data):
        """Lance le mode test avec les données brutes de l'éditeur."""
        from src.level import Level
        test_level = Level(level_data)
        self.current_level = level_data["id"]
        
        # Init Player
        self.player = Player(test_level, start_x=test_level.start_x, start_y=test_level.start_y)
        
        # Init Mobs
        self.mobs = []
        for m_data in test_level.mobs_data:
            mob = create_mob(m_data, test_level)
            self.mobs.append(mob)
            
        self.game_renderer = GameRenderer(self.screen, self.font_manager, test_level)
        self.state = GameState.PLAYING
        self.is_testing = True
        self.projectiles = []

    def _handle_player_death(self):
        """Gère la mort du joueur."""
        self.data_manager.update_stats(self.pseudo, deaths=1)
        self.player_stats = self.data_manager.get_player_stats(self.pseudo)
        
        if self.is_testing:
            self.state = GameState.EDITOR
            self.is_testing = False
        else:
            self.state = GameState.GAME_OVER
            self.animation_frame = 0

    def draw(self):
        """Rendu du jeu."""
        if self.state == GameState.LOGIN:
            self.ui_renderer.draw_login(self.pseudo)
        elif self.state == GameState.MENU:
            self.ui_renderer.draw_menu(self.pseudo, self.player_stats)
        elif self.state == GameState.LEVEL_SELECT:
            self.ui_renderer.draw_level_select(self.level_manager.get_all_levels_ids())
        elif self.state == GameState.STATS:
            self.ui_renderer.draw_stats(self.pseudo, self.player_stats)
        elif self.state == GameState.PLAYING and self.game_renderer and self.player:
            self.game_renderer.draw_game(self.player, self.mobs, self.projectiles)
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
