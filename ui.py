# -*- coding: utf-8 -*-
import pygame
from config import WINDOW_WIDTH, WINDOW_HEIGHT, TILE_SIZE, COLORS


class FontManager:
    """Gere les polices du jeu."""

    def __init__(self):
        self.fonts = {
            'large':      pygame.font.Font(None, 120),
            'title':      pygame.font.Font(None, 140),
            'medium':     pygame.font.Font(None, 70),
            'subtitle':   pygame.font.Font(None, 60),
            'small':      pygame.font.Font(None, 45),
            'controls':   pygame.font.Font(None, 28),
            'menu_small': pygame.font.Font(None, 40),
        }

    def get(self, key):
        """Retourne une police."""
        return self.fonts.get(key)


class UIRenderer:
    """Gere le rendu de l'interface utilisateur."""

    def __init__(self, screen, font_manager):
        self.screen = screen
        self.fonts = font_manager

    def draw_text(self, font, text, color, center_x, y):
        """Dessine du texte centre horizontalement."""
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(center_x, y))
        self.screen.blit(surface, rect)

    def draw_menu(self):
        """Dessine l'ecran du menu."""
        self.screen.fill(COLORS["menu_bg"])

        self.draw_text(self.fonts.get('large'), "MAZE GAME", COLORS["exit"],
                       WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 200)
        self.draw_text(self.fonts.get('subtitle'), "Niveau 1", COLORS["player"],
                       WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 80)

        self.draw_text(self.fonts.get('menu_small'), "Appuyez sur 1 pour jouer", COLORS["white"],
                       WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60)
        self.draw_text(self.fonts.get('menu_small'), "Q pour quitter", COLORS["white"],
                       WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 130)
        self.draw_text(self.fonts.get('menu_small'), "ESC pour quitter", COLORS["white"],
                       WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 190)

    def draw_win(self, current_level):
        """Dessine l'ecran de victoire."""
        self.screen.fill(COLORS["menu_bg"])

        self.draw_text(self.fonts.get('title'), "VOUS AVEZ GAGNE!", COLORS["exit"],
                       WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 150)
        self.draw_text(self.fonts.get('medium'), f"Niveau {current_level} complete!",
                       COLORS["player"], WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20)

        self.draw_text(self.fonts.get('small'),
                       "Appuyez sur ESPACE pour retourner au menu", COLORS["white"],
                       WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 150)
        self.draw_text(self.fonts.get('small'), "Q pour quitter", COLORS["white"],
                       WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 220)


class GameRenderer:
    """Gere le rendu du jeu en cours."""

    def __init__(self, screen, font_manager, level):
        self.screen = screen
        self.fonts = font_manager
        self.level = level
        self._calculate_offsets()

    def _calculate_offsets(self):
        """Calcule les offsets pour centrer le labyrinthe."""
        maze_width, maze_height = self.level.get_pixel_dimensions()
        self.offset_x = (WINDOW_WIDTH - maze_width) // 2
        self.offset_y = (WINDOW_HEIGHT - maze_height) // 2

    def draw_maze(self):
        """Dessine le labyrinthe."""
        width, height = self.level.get_dimensions()

        for y in range(height):
            for x in range(width):
                tile = self.level.get_tile(x, y)
                self._draw_tile(x, y, tile)

    def _draw_tile(self, x, y, tile):
        """Dessine une tuile."""
        rect = pygame.Rect(
            self.offset_x + x * TILE_SIZE,
            self.offset_y + y * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE
        )

        if tile == 1:
            pygame.draw.rect(self.screen, COLORS["wall"], rect)
            pygame.draw.rect(self.screen, COLORS["wall_border"], rect, 2)
        else:
            pygame.draw.rect(self.screen, COLORS["path"], rect)

    def draw_exit(self):
        """Dessine la sortie."""
        exit_rect = pygame.Rect(
            self.offset_x + self.level.exit_x * TILE_SIZE,
            self.offset_y + self.level.exit_y * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE
        )
        pygame.draw.rect(self.screen, COLORS["exit"], exit_rect)
        pygame.draw.rect(self.screen, COLORS["exit_border"], exit_rect, 3)

    def draw_player(self, player):
        """Dessine le joueur."""
        player_rect = pygame.Rect(
            self.offset_x + int(player.x) * TILE_SIZE + 5,
            self.offset_y + int(player.y) * TILE_SIZE + 5,
            TILE_SIZE - 10,
            TILE_SIZE - 10
        )
        pygame.draw.rect(self.screen, COLORS["player"], player_rect)
        pygame.draw.circle(self.screen, COLORS["player_eye"], player_rect.center, 8)

    def draw_controls(self):
        """Dessine les controles."""
        controls_text = "Z=Haut  Q=Gauche  S=Bas  D=Droite  ESC=Menu"
        self.screen.blit(
            self.fonts.get('controls').render(controls_text, True, COLORS["white"]),
            (20, 20)
        )

    def draw_game(self, player):
        """Dessine le jeu complet."""
        self.screen.fill(COLORS["black"])
        self.draw_maze()
        self.draw_exit()
        self.draw_player(player)
        self.draw_controls()
