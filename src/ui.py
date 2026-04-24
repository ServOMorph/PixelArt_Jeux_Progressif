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
        self.splash_img = None
        self._load_assets()

    def _load_assets(self):
        """Charge les assets graphiques (images)."""
        import os
        self.sprites = {}
        assets_to_load = {
            "splash": "splash.png",
            "player": "player.png",
            "wall": "wall.png",
            "path": "path.png",
            "mob_h": "mob_h.png",
            "mob_v": "mob_v.png",
            "exit": "exit.png", # Pas encore généré mais prévu
        }
        
        for key, filename in assets_to_load.items():
            path = os.path.join("assets", filename)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    if key == "splash":
                        self.splash_img = img
                    else:
                        # Redimensionner à la taille des tuiles
                        self.sprites[key] = pygame.transform.smoothscale(img, (TILE_SIZE, TILE_SIZE))
                except Exception as e:
                    print(f"Erreur chargement asset {key}: {e}")

    def draw_text(self, font, text, color, center_x, y):
        """Dessine du texte centre horizontalement et retourne son Rect."""
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(center_x, y))
        self.screen.blit(surface, rect)
        return rect

    def draw_splash(self, alpha=255):
        """Dessine l'ecran de splash."""
        self.screen.fill((0, 0, 0))
        if self.splash_img:
            if alpha < 255:
                # Gérer la transparence si besoin pour un fade-in/out
                self.splash_img.set_alpha(alpha)
            
            # Centrer l'image
            rect = self.splash_img.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(self.splash_img, rect)
        else:
            self.draw_text(self.fonts.get('large'), "PIXEL ADVENTURE", (0, 255, 255),
                           WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
            self.draw_text(self.fonts.get('medium'), "Chargement...", (255, 255, 255),
                           WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100)

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
            ("4. Options", "OPTIONS"),
            ("5. Test de Niveau IA", "IA_TEST"),
            ("Q. Quitter", "QUIT")
        ]
        
        for i, (text, action) in enumerate(options):
            color = COLORS["white"]
            if action == "PLAY": color = COLORS["player"] # Action principale en Cyan
            elif action == "QUIT": color = COLORS["exit"]  # Quitter en Magenta
            
            rect = self.draw_text(self.fonts.get('medium'), text, color,
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
        # Fond qui utilise la couleur de mort de la charte
        color = list(COLORS["death_bg"])
        factor = min(1.0, animation_frame / 60)
        final_color = tuple(int(c * factor) for c in color)
        self.screen.fill(final_color)
        
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

    def draw_options(self, render_mode):
        """Dessine l'ecran des options."""
        self.screen.fill(COLORS["menu_bg"])
        self.click_areas = {}
        
        self.draw_text(self.fonts.get('large'), "OPTIONS", COLORS["player"],
                       WINDOW_WIDTH // 2, 150)
        
        self.draw_text(self.fonts.get('medium'), "Modèle Graphique :", COLORS["white"],
                       WINDOW_WIDTH // 2, 300)
        
        # Bouton Toggle
        mode_text = f"MODE : {render_mode}"
        rect_mode = self.draw_text(self.fonts.get('large'), mode_text, (0, 255, 255),
                                   WINDOW_WIDTH // 2, 400)
        self.click_areas["TOGGLE_RENDER"] = rect_mode
        
        desc = "CHIADÉ = Pixel Art détaillé | DÉFAUT = Géométrique simple"
        self.draw_text(self.fonts.get('small'), desc, (150, 150, 150),
                       WINDOW_WIDTH // 2, 480)
        
        rect_back = self.draw_text(self.fonts.get('small'), "Appuyez sur ESC pour retour", COLORS["exit"],
                                   WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100)
        self.click_areas["BACK"] = rect_back


class GameRenderer:
    """Gere le rendu du jeu en cours."""

    def __init__(self, screen, font_manager, level, render_mode="CHIADÉ", ui_renderer=None):
        self.screen = screen
        self.fonts = font_manager
        self.level = level
        self.render_mode = render_mode
        self.ui_renderer = ui_renderer # Accès aux sprites chargés
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

        if self.render_mode == "CHIADÉ":
            self._draw_tile_chiade(x, y, tile, rect)
        else:
            self._draw_tile_defaut(x, y, tile, rect)

    def _draw_tile_defaut(self, x, y, tile, rect):
        """Rendu simple géométrique."""
        wall_color = self.level.colors.get("wall", COLORS["wall"])
        border_color = self.level.colors.get("wall_border", COLORS["wall_border"])
        path_color = self.level.colors.get("path", COLORS["path"])
        tree_color = self.level.colors.get("tree", COLORS["tree"])

        if tile == 1: # WALL
            pygame.draw.rect(self.screen, wall_color, rect)
            pygame.draw.rect(self.screen, border_color, rect, 2)
        elif tile == 2: # TREE
            pygame.draw.rect(self.screen, tree_color, rect, border_radius=10)
            pygame.draw.rect(self.screen, COLORS["tree_top"], rect.inflate(-16, -16), border_radius=5)
        else: # PATH
            pygame.draw.rect(self.screen, path_color, rect)

    def _draw_tile_chiade(self, x, y, tile, rect):
        """Rendu Pixel Art Premium avec Sprites."""
        if tile == 1: # MUR
            if self.ui_renderer and "wall" in self.ui_renderer.sprites:
                self.screen.blit(self.ui_renderer.sprites["wall"], rect)
            else:
                pygame.draw.rect(self.screen, (60, 60, 80), rect)
                # ... (fallback drawing)
        elif tile == 2: # ARBRE
            pygame.draw.circle(self.screen, (34, 139, 34), rect.center, 18)
            pygame.draw.circle(self.screen, (50, 160, 50), rect.center, 12)
            pygame.draw.rect(self.screen, (101, 67, 33), (rect.centerx-3, rect.centery, 6, 15))
        else: # SOL
            if self.ui_renderer and "path" in self.ui_renderer.sprites:
                self.screen.blit(self.ui_renderer.sprites["path"], rect)
            else:
                pygame.draw.rect(self.screen, (25, 25, 35), rect)

    def draw_exit(self):
        """Dessine la sortie."""
        exit_rect = pygame.Rect(
            self.offset_x + self.level.exit_x * TILE_SIZE,
            self.offset_y + self.level.exit_y * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE
        )
        if self.render_mode == "CHIADÉ":
            pygame.draw.circle(self.screen, (255, 20, 147), exit_rect.center, 15, 3)
            pygame.draw.circle(self.screen, (255, 255, 255), exit_rect.center, 5)
        else:
            exit_color = self.level.colors.get("exit", COLORS["exit"])
            pygame.draw.rect(self.screen, exit_color, exit_rect)
            pygame.draw.rect(self.screen, COLORS["exit_border"], exit_rect, 3)

    def draw_player(self, player):
        """Dessine le joueur."""
        pos_x, pos_y = player.get_pixel_position(self.offset_x, self.offset_y)
        player_rect = pygame.Rect(pos_x + 5, pos_y + 5, TILE_SIZE - 10, TILE_SIZE - 10)
        
        if self.render_mode == "CHIADÉ" and self.ui_renderer and "player" in self.ui_renderer.sprites:
            self.screen.blit(self.ui_renderer.sprites["player"], player_rect)
        elif self.render_mode == "CHIADÉ":
            pygame.draw.circle(self.screen, (0, 255, 255), player_rect.center, 15, 2)
            pygame.draw.circle(self.screen, (0, 255, 255), player_rect.center, 8)
        else:
            pygame.draw.rect(self.screen, COLORS["player"], player_rect)
            pygame.draw.circle(self.screen, COLORS["player_eye"], player_rect.center, 8)

    def draw_mobs(self, mobs):
        """Dessine les ennemis."""
        for mob in mobs:
            pos_x, pos_y = mob.get_pixel_position(self.offset_x, self.offset_y)
            rect = pygame.Rect(pos_x, pos_y, TILE_SIZE, TILE_SIZE)
            cx, cy = rect.center
            
            if self.render_mode == "CHIADÉ":
                sprite_key = None
                pattern = getattr(mob, 'pattern', None)
                if pattern == "horizontal": sprite_key = "mob_h"
                elif pattern == "vertical": sprite_key = "mob_v"
                
                if sprite_key and self.ui_renderer and sprite_key in self.ui_renderer.sprites:
                    self.screen.blit(self.ui_renderer.sprites[sprite_key], rect)
                elif pattern == "horizontal": # SLIME (fallback)
                    pygame.draw.ellipse(self.screen, (255, 140, 0), (cx-15, cy-10, 30, 25))
                elif pattern == "vertical": # SPECTRE (fallback)
                    pygame.draw.polygon(self.screen, (150, 0, 200), [(cx, cy-18), (cx-15, cy+10), (cx+15, cy+10)])
                elif pattern == "chaser": # OEIL
                    pygame.draw.circle(self.screen, (200, 200, 0), (cx, cy), 16)
                    pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), 10)
                    pygame.draw.circle(self.screen, (255, 0, 0), (cx, cy), 5)
                else: # SHOOTER
                    pygame.draw.rect(self.screen, (0, 180, 100), (cx-12, cy-12, 24, 24), border_radius=4)
                    pygame.draw.rect(self.screen, (200, 255, 200), (cx-4, cy-4, 8, 8))
            else:
                mob_rect = pygame.Rect(pos_x + 8, pos_y + 8, TILE_SIZE - 16, TILE_SIZE - 16)
                pygame.draw.rect(self.screen, COLORS["mob"], mob_rect)
                pygame.draw.rect(self.screen, COLORS["mob_eye"], (mob_rect.x + 5, mob_rect.y + 8, 6, 6))
                pygame.draw.rect(self.screen, COLORS["mob_eye"], (mob_rect.right - 11, mob_rect.y + 8, 6, 6))

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

