# -*- coding: utf-8 -*-
import pygame
from config import COLORS, TILE_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT

class LevelEditor:
    """Editeur de niveaux interactif et complet."""

    def __init__(self, screen, font_manager, data_manager):
        self.screen = screen
        self.fonts = font_manager
        self.data_manager = data_manager
        
        # Paramètres de la grille
        self.grid_w = 20
        self.grid_h = 15
        self.tile_size = 40
        
        self.offset_x = (WINDOW_WIDTH - (self.grid_w * self.tile_size)) // 2
        self.offset_y = 120
        
        # Données du niveau
        self.level_id = 101
        self.maze = [[0 for _ in range(self.grid_w)] for _ in range(self.grid_h)]
        self._add_borders()
        
        self.start_pos = [1, 1]
        self.exit_pos = [self.grid_w - 2, self.grid_h - 2]
        self.mobs = []
        
        # Outils
        self.tools = ["WALL", "PATH", "START", "EXIT", "MOB_H", "MOB_V"]
        self.current_tool = "WALL"
        
        # UI Rects
        self.save_rect = pygame.Rect(WINDOW_WIDTH - 180, 20, 160, 50)
        self.exit_editor_rect = pygame.Rect(20, 20, 160, 50)
        self.clear_rect = pygame.Rect(WINDOW_WIDTH // 2 + 100, 20, 160, 50)
        self.id_input_rect = pygame.Rect(WINDOW_WIDTH // 2 - 250, 20, 200, 50)
        
        self.is_typing_id = False

    def _add_borders(self):
        """Ajoute des murs sur le bord du labyrinthe."""
        for x in range(self.grid_w):
            self.maze[0][x] = 1
            self.maze[self.grid_h-1][x] = 1
        for y in range(self.grid_h):
            self.maze[y][0] = 1
            self.maze[y][self.grid_w-1] = 1

    def handle_events(self):
        """Gere les clics et touches dans l'editeur."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            
            if event.type == pygame.KEYDOWN:
                if self.is_typing_id:
                    if event.key == pygame.K_RETURN:
                        self.is_typing_id = False
                    elif event.key == pygame.K_BACKSPACE:
                        s = str(self.level_id)
                        self.level_id = int(s[:-1]) if len(s) > 1 else 0
                    elif event.unicode.isdigit():
                        self.level_id = int(str(self.level_id) + event.unicode)
                    return "EDITOR"

                if event.key == pygame.K_ESCAPE:
                    return "MENU"
                if event.key == pygame.K_s:
                    self.save_level()
                
                # Raccourcis outils
                shortcuts = {pygame.K_1: "WALL", pygame.K_2: "PATH", pygame.K_3: "START", 
                             pygame.K_4: "EXIT", pygame.K_5: "MOB_H", pygame.K_6: "MOB_V"}
                if event.key in shortcuts:
                    self.current_tool = shortcuts[event.key]

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                
                # Clic sur l'input ID
                if self.id_input_rect.collidepoint(mx, my):
                    self.is_typing_id = True
                else:
                    self.is_typing_id = False

                # Boutons
                if self.save_rect.collidepoint(mx, my):
                    if self.save_level(): return "MENU"
                if self.exit_editor_rect.collidepoint(mx, my):
                    return "MENU"
                if self.clear_rect.collidepoint(mx, my):
                    self.maze = [[0 for _ in range(self.grid_w)] for _ in range(self.grid_h)]
                    self._add_borders()
                    self.mobs = []

                # Palette
                for i, tool in enumerate(self.tools):
                    if self._get_tool_rect(i).collidepoint(mx, my):
                        self.current_tool = tool

            # Dessin continu sur la grille
            if pygame.mouse.get_pressed()[0]:
                mx, my = pygame.mouse.get_pos()
                if self.offset_x <= mx < self.offset_x + self.grid_w * self.tile_size and \
                   self.offset_y <= my < self.offset_y + self.grid_h * self.tile_size:
                    gx = (mx - self.offset_x) // self.tile_size
                    gy = (my - self.offset_y) // self.tile_size
                    self.apply_tool(gx, gy)

        return "EDITOR"

    def apply_tool(self, x, y):
        """Applique l'outil selectionne a la case (x, y)."""
        if self.current_tool == "WALL":
            self.maze[y][x] = 1
        elif self.current_tool == "PATH":
            self.maze[y][x] = 0
            # Supprimer mob si present
            self.mobs = [m for m in self.mobs if m["start_pos"] != [x, y]]
        elif self.current_tool == "START":
            self.maze[y][x] = 0
            self.start_pos = [x, y]
        elif self.current_tool == "EXIT":
            self.maze[y][x] = 0
            self.exit_pos = [x, y]
        elif self.current_tool.startswith("MOB"):
            self.maze[y][x] = 0
            pattern = "horizontal" if self.current_tool == "MOB_H" else "vertical"
            # Eviter doublons
            self.mobs = [m for m in self.mobs if m["start_pos"] != [x, y]]
            self.mobs.append({
                "type": "Mob1", 
                "start_pos": [x, y], 
                "pattern": pattern, 
                "distance": 4, 
                "speed": 0.08
            })

    def save_level(self):
        """Sauvegarde le niveau dans le fichier JSON."""
        custom_levels = self.data_manager.load_custom_levels()
        
        # Supprimer l'ancien niveau avec le meme ID si present
        custom_levels = [l for l in custom_levels if l["id"] != self.level_id]
            
        new_level = {
            "id": self.level_id,
            "name": f"Niveau {self.level_id}",
            "maze": self.maze,
            "start_pos": self.start_pos,
            "exit_pos": self.exit_pos,
            "mobs": self.mobs,
            "colors": {
                "wall": (100, 100, 100),
                "wall_border": (150, 150, 150),
                "path": (30, 30, 30),
                "exit": (255, 20, 147)
            }
        }
        
        custom_levels.append(new_level)
        self.data_manager.save_custom_levels(custom_levels)
        print(f"Niveau {self.level_id} sauvegardé !")
        return True

    def _get_tool_rect(self, index):
        """Calcule le rectangle d'un outil dans la palette."""
        palette_y = WINDOW_HEIGHT - 90
        spacing = 150
        start_x = (WINDOW_WIDTH - (len(self.tools) * spacing)) // 2
        return pygame.Rect(start_x + index * spacing, palette_y, 140, 70)

    def draw(self):
        """Rendu de l'editeur."""
        self.screen.fill(COLORS["menu_bg"])
        
        # Titre
        title_surf = self.fonts.get('medium').render("EDITEUR DE NIVEAU", True, COLORS["player"])
        self.screen.blit(title_surf, (200, 20))
        
        # Input ID
        pygame.draw.rect(self.screen, (50, 50, 70), self.id_input_rect, border_radius=5)
        border_col = COLORS["player"] if self.is_typing_id else COLORS["white"]
        pygame.draw.rect(self.screen, border_col, self.id_input_rect, 2, border_radius=5)
        id_text = self.fonts.get('small').render(f"ID: {self.level_id}", True, COLORS["white"])
        self.screen.blit(id_text, (self.id_input_rect.x + 10, self.id_input_rect.y + 10))

        # Grille
        for y in range(self.grid_h):
            for x in range(self.grid_w):
                rect = pygame.Rect(self.offset_x + x * self.tile_size, self.offset_y + y * self.tile_size, self.tile_size, self.tile_size)
                
                if self.maze[y][x] == 1:
                    pygame.draw.rect(self.screen, COLORS["wall"], rect)
                    pygame.draw.rect(self.screen, COLORS["wall_border"], rect, 1)
                else:
                    pygame.draw.rect(self.screen, COLORS["path"], rect)
                    pygame.draw.rect(self.screen, (40, 40, 60), rect, 1)
                
                if [x, y] == self.start_pos:
                    pygame.draw.rect(self.screen, COLORS["player"], rect.inflate(-12, -12))
                elif [x, y] == self.exit_pos:
                    pygame.draw.rect(self.screen, COLORS["exit"], rect.inflate(-12, -12))
                
                for mob in self.mobs:
                    if mob["start_pos"] == [x, y]:
                        color = (255, 100, 0) if mob["pattern"] == "horizontal" else (255, 0, 255)
                        pygame.draw.circle(self.screen, color, rect.center, self.tile_size // 3)

        # Palette
        for i, tool in enumerate(self.tools):
            rect = self._get_tool_rect(i)
            bg_col = (70, 70, 100) if self.current_tool == tool else (30, 30, 50)
            pygame.draw.rect(self.screen, bg_col, rect, border_radius=8)
            pygame.draw.rect(self.screen, COLORS["white"], rect, 2, border_radius=8)
            
            txt = self.fonts.get('small').render(tool, True, COLORS["white"])
            self.screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

        # Boutons
        for r, text, col in [(self.save_rect, "SAVE", (0, 180, 0)), 
                              (self.exit_editor_rect, "BACK", (180, 0, 0)),
                              (self.clear_rect, "CLEAR", (100, 100, 100))]:
            pygame.draw.rect(self.screen, col, r, border_radius=5)
            surf = self.fonts.get('small').render(text, True, COLORS["white"])
            self.screen.blit(surf, (r.centerx - surf.get_width() // 2, r.centery - surf.get_height() // 2))
