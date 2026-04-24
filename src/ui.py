# -*- coding: utf-8 -*-
import pygame
from config import WINDOW_WIDTH, WINDOW_HEIGHT, TILE_SIZE, COLORS


class FontManager:
    """Gere les polices du jeu."""

    def __init__(self):
        self.fonts = {
            'large':      pygame.font.Font(None, 80),
            'title':      pygame.font.Font(None, 100),
            'medium':     pygame.font.Font(None, 40),
            'subtitle':   pygame.font.Font(None, 35),
            'small':      pygame.font.Font(None, 26),
            'controls':   pygame.font.Font(None, 20),
            'menu_small': pygame.font.Font(None, 28),
        }

    def get(self, key):
        """Retourne une police."""
        return self.fonts.get(key)


class UIRenderer:
    """Gere le rendu de l'interface utilisateur."""

    def __init__(self, screen, font_manager):
        self.screen = screen
        self.fonts = font_manager
        self.click_areas = {} # { "action_name": pygame.Rect }

    def draw_text(self, font, text, color, center_x, y):
        """Dessine du texte centre horizontalement et retourne son Rect."""
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(center_x, y))
        self.screen.blit(surface, rect)
        return rect

    def draw_login(self, pseudo):
        """Dessine l'ecran de saisie du pseudo."""
        self.screen.fill(COLORS["menu_bg"])
        self.draw_text(self.fonts.get('large'), "PIXEL ADVENTURE", COLORS["player"],
                       WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 150)
        self.draw_text(self.fonts.get('medium'), "Entrez votre Pseudo:", COLORS["white"],
                       WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        
        # Champ de saisie
        input_rect = pygame.Rect(WINDOW_WIDTH // 2 - 200, WINDOW_HEIGHT // 2 + 50, 400, 60)
        pygame.draw.rect(self.screen, COLORS["path"], input_rect)
        pygame.draw.rect(self.screen, COLORS["player"], input_rect, 2)
        
        self.draw_text(self.fonts.get('medium'), pseudo + "_", COLORS["white"],
                       WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80)
        
        self.draw_text(self.fonts.get('small'), "Appuyez sur ENTRÉE pour valider", COLORS["exit"],
                       WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 200)

    def draw_menu(self, pseudo, stats):
        """Dessine l'ecran du menu principal."""
        self.screen.fill(COLORS["menu_bg"])
        self.click_areas = {}

        self.draw_text(self.fonts.get('large'), "MAZE GAME", COLORS["exit"],
                       WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 250)
        
        # Affichage des Stats (En haut à droite)
        if stats:
            stats_rect = pygame.Rect(WINDOW_WIDTH - 300, 20, 280, 140)
            pygame.draw.rect(self.screen, (40, 40, 60), stats_rect, border_radius=10)
            pygame.draw.rect(self.screen, COLORS["player"], stats_rect, 2, border_radius=10)
            
            # Titre / Pseudo
            p_text = self.fonts.get('menu_small').render(f"Profil: {pseudo}", True, COLORS["player"])
            self.screen.blit(p_text, (stats_rect.x + 15, stats_rect.y + 10))
            
            # Détails
            s_font = self.fonts.get('controls')
            self.screen.blit(s_font.render(f"Niveaux: {stats['levels_completed']}", True, COLORS["white"]), (stats_rect.x + 15, stats_rect.y + 50))
            self.screen.blit(s_font.render(f"Morts: {stats['deaths']}", True, COLORS["white"]), (stats_rect.x + 15, stats_rect.y + 80))
            self.screen.blit(s_font.render(f"Record: Lvl {stats['best_level']}", True, COLORS["white"]), (stats_rect.x + 15, stats_rect.y + 110))

        options = [
            ("1. Jouer (Niveau 1)", "PLAY"),
            ("2. Choisir un Niveau", "LEVEL_SELECT"),
            ("3. Editeur de Niveau", "EDITOR"),
            ("Q. Quitter", "QUIT")
        ]
        
        for i, (text, action) in enumerate(options):
            rect = self.draw_text(self.fonts.get('medium'), text, COLORS["white"],
                                  WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50 + i * 80)
            self.click_areas[action] = rect

    def draw_level_select(self, levels_ids):
        """Dessine l'ecran de selection de niveau sous forme de grille."""
        self.screen.fill(COLORS["menu_bg"])
        self.click_areas = {}
        
        self.draw_text(self.fonts.get('large'), "CHOIX DU NIVEAU", COLORS["player"],
                       WINDOW_WIDTH // 2, 150)
        
        # Grille de niveaux (4 colonnes)
        cols = 4
        spacing_x = 400
        spacing_y = 100
        start_x = (WINDOW_WIDTH - (cols - 1) * spacing_x) // 2
        start_y = 300
        
        for i, lvl_id in enumerate(levels_ids):
            col = i % cols
            row = i // cols
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            
            rect = self.draw_text(self.fonts.get('medium'), f"Niveau {lvl_id}", COLORS["white"],
                                  x, y)
            self.click_areas[f"LEVEL_{lvl_id}"] = rect
        
        rect_back = self.draw_text(self.fonts.get('small'), "Appuyez sur ESC pour retour", COLORS["exit"],
                                   WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100)
        self.click_areas["BACK"] = rect_back

    def draw_stats(self, pseudo, stats):
        """Dessine l'ecran des statistiques."""
        self.screen.fill(COLORS["menu_bg"])
        self.draw_text(self.fonts.get('large'), f"STATS: {pseudo}", COLORS["player"],
                       WINDOW_WIDTH // 2, 150)
        
        lines = [
            f"Niveaux terminés: {stats['levels_completed']}",
            f"Nombre de morts: {stats['deaths']}",
            f"Meilleur niveau: {stats['best_level']}"
        ]
        
        for i, line in enumerate(lines):
            self.draw_text(self.fonts.get('medium'), line, COLORS["white"],
                           WINDOW_WIDTH // 2, 350 + i * 100)
            
        self.draw_text(self.fonts.get('small'), "Appuyez sur n'importe quelle touche pour retour", COLORS["exit"],
                       WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100)

    def draw_game_over(self, animation_frame=0):
        """Dessine l'ecran de Game Over avec animation."""
        # Fond qui devient de plus en plus rouge
        red_val = min(255, animation_frame * 10)
        self.screen.fill((red_val, 0, 0))
        
        self.draw_text(self.fonts.get('title'), "MORT !", COLORS["white"],
                       WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        
        if animation_frame > 30:
            self.draw_text(self.fonts.get('medium'), "Retour à l'accueil...", COLORS["white"],
                           WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100)

    def draw_win(self, current_level, has_next=False):
        """Dessine l'ecran de victoire."""
        self.screen.fill(COLORS["menu_bg"])
        self.click_areas = {}

        self.draw_text(self.fonts.get('title'), "VOUS AVEZ GAGNE!", COLORS["exit"],
                       WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 150)
        self.draw_text(self.fonts.get('medium'), f"Niveau {current_level} complete!",
                       COLORS["player"], WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20)

        if has_next:
            rect = self.draw_text(self.fonts.get('small'),
                                  "Appuyez sur ESPACE pour le NIVEAU SUIVANT", COLORS["white"],
                                  WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 150)
            self.click_areas["NEXT"] = rect
        else:
            self.draw_text(self.fonts.get('small'),
                           "Félicitations! Vous avez fini tous les niveaux.", COLORS["white"],
                           WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 120)
            rect = self.draw_text(self.fonts.get('small'),
                                  "Appuyez sur ESPACE pour retourner au menu", COLORS["white"],
                                  WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 180)
            self.click_areas["MENU"] = rect

        rect_quit = self.draw_text(self.fonts.get('small'), "Q pour quitter", COLORS["white"],
                                   WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 250)
        self.click_areas["QUIT"] = rect_quit


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

        # Couleurs spécifiques au niveau ou défaut
        wall_color = self.level.colors.get("wall", COLORS["wall"])
        border_color = self.level.colors.get("wall_border", COLORS["wall_border"])
        path_color = self.level.colors.get("path", COLORS["path"])

        if tile == 1:
            pygame.draw.rect(self.screen, wall_color, rect)
            if self.level.id == 2:
                # Style forêt : ajout d'un petit "feuillage" interne
                pygame.draw.rect(self.screen, border_color, rect.inflate(-12, -12))
            else:
                pygame.draw.rect(self.screen, border_color, rect, 2)
        else:
            pygame.draw.rect(self.screen, path_color, rect)

    def draw_exit(self):
        """Dessine la sortie."""
        exit_rect = pygame.Rect(
            self.offset_x + self.level.exit_x * TILE_SIZE,
            self.offset_y + self.level.exit_y * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE
        )
        exit_color = self.level.colors.get("exit", COLORS["exit"])
        pygame.draw.rect(self.screen, exit_color, exit_rect)
        pygame.draw.rect(self.screen, COLORS["exit_border"], exit_rect, 3)

    def draw_player(self, player):
        """Dessine le joueur."""
        pos_x, pos_y = player.get_pixel_position(self.offset_x, self.offset_y)
        player_rect = pygame.Rect(pos_x + 5, pos_y + 5, TILE_SIZE - 10, TILE_SIZE - 10)
        pygame.draw.rect(self.screen, COLORS["player"], player_rect)
        pygame.draw.circle(self.screen, COLORS["player_eye"], player_rect.center, 8)

    def draw_mobs(self, mobs):
        """Dessine les ennemis."""
        for mob in mobs:
            pos_x, pos_y = mob.get_pixel_position(self.offset_x, self.offset_y)
            mob_rect = pygame.Rect(pos_x + 8, pos_y + 8, TILE_SIZE - 16, TILE_SIZE - 16)
            pygame.draw.rect(self.screen, COLORS["mob"], mob_rect)
            # Yeux de mob
            eye_w = 6
            pygame.draw.rect(self.screen, COLORS["mob_eye"], (mob_rect.x + 5, mob_rect.y + 8, eye_w, eye_w))
            pygame.draw.rect(self.screen, COLORS["mob_eye"], (mob_rect.right - 5 - eye_w, mob_rect.y + 8, eye_w, eye_w))

    def draw_projectiles(self, projectiles):
        """Dessine les projectiles."""
        for p in projectiles:
            px = self.offset_x + p.x * TILE_SIZE
            py = self.offset_y + p.y * TILE_SIZE
            # Missile rouge avec petit halo
            pygame.draw.circle(self.screen, (255, 0, 0), (int(px + TILE_SIZE//2), int(py + TILE_SIZE//2)), 8)
            pygame.draw.circle(self.screen, (255, 200, 200), (int(px + TILE_SIZE//2), int(py + TILE_SIZE//2)), 4)

    def draw_game(self, player, mobs, projectiles=[]):
        """Effectue le rendu complet d'une frame de jeu."""
        self.screen.fill(COLORS["bg"])
        self.draw_maze()
        self.draw_exit()
        self.draw_mobs(mobs)
        self.draw_projectiles(projectiles)
        self.draw_player(player)
        self.draw_controls()

    def draw_controls(self):
        """Dessine les controles."""
        controls_text = "Z=Haut  Q=Gauche  S=Bas  D=Droite  ESC=Menu"
        self.screen.blit(
            self.fonts.get('controls').render(controls_text, True, COLORS["white"]),
            (20, 20)
        )

