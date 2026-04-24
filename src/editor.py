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
        self.load_rect = pygame.Rect(WINDOW_WIDTH // 2, 20, 160, 50)
        self.clear_rect = pygame.Rect(WINDOW_WIDTH // 2 + 170, 20, 160, 50)
        
        self.is_typing_id = False
        self.is_typing_name = False
        self.level_name = "Nouveau Niveau"
        self.save_message_timer = 0
        
        # Historique
        self.history = []
        self.redo_stack = []
        self.max_history = 30
        
        # Panel de chargement
        self.show_load_panel = False
        self.loadable_levels = []
        self.load_panel_rect = pygame.Rect(WINDOW_WIDTH // 2 - 300, WINDOW_HEIGHT // 2 - 300, 600, 600)

        # Panel de sauvegarde
        self.show_save_panel = False
        self.save_panel_rect = pygame.Rect(WINDOW_WIDTH // 2 - 350, WINDOW_HEIGHT // 2 - 250, 700, 500)
        self.confirm_save_rect = pygame.Rect(self.save_panel_rect.x + 100, self.save_panel_rect.y + 400, 200, 60)
        self.cancel_save_rect = pygame.Rect(self.save_panel_rect.x + 400, self.save_panel_rect.y + 400, 200, 60)
        self.save_input_rect = pygame.Rect(self.save_panel_rect.x + 50, self.save_panel_rect.y + 150, 600, 60)
        
        # Liste des noms utilisés
        self.used_names = []
        self._refresh_used_names()

    def _refresh_used_names(self):
        """Récupère tous les noms de niveaux existants."""
        from levels.levels_config import ALL_LEVELS
        customs = self.data_manager.load_custom_levels()
        self.used_names = [lvl["name"] for lvl in (ALL_LEVELS + customs)]

    def _add_borders(self):
        """Ajoute des murs sur le bord du labyrinthe."""
        for x in range(self.grid_w):
            self.maze[0][x] = 1
            self.maze[self.grid_h-1][x] = 1
        for y in range(self.grid_h):
            self.maze[y][0] = 1
            self.maze[y][self.grid_w-1] = 1

    def save_snapshot(self):
        """Enregistre l'état actuel pour l'historique."""
        snapshot = {
            "maze": [row[:] for row in self.maze],
            "start_pos": self.start_pos[:],
            "exit_pos": self.exit_pos[:],
            "mobs": [m.copy() for m in self.mobs]
        }
        self.history.append(snapshot)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        self.redo_stack = [] # On vide la redo stack après une nouvelle action

    def undo(self):
        """Annule la dernière action."""
        if self.history:
            # Sauvegarder l'état actuel pour le redo
            current = {
                "maze": [row[:] for row in self.maze],
                "start_pos": self.start_pos[:],
                "exit_pos": self.exit_pos[:],
                "mobs": [m.copy() for m in self.mobs]
            }
            self.redo_stack.append(current)
            
            # Restaurer le snapshot
            snapshot = self.history.pop()
            self.maze = snapshot["maze"]
            self.start_pos = snapshot["start_pos"]
            self.exit_pos = snapshot["exit_pos"]
            self.mobs = snapshot["mobs"]

    def redo(self):
        """Rétablit l'action annulée."""
        if self.redo_stack:
            # Sauvegarder pour undo
            current = {
                "maze": [row[:] for row in self.maze],
                "start_pos": self.start_pos[:],
                "exit_pos": self.exit_pos[:],
                "mobs": [m.copy() for m in self.mobs]
            }
            self.history.append(current)
            
            # Restaurer
            snapshot = self.redo_stack.pop()
            self.maze = snapshot["maze"]
            self.start_pos = snapshot["start_pos"]
            self.exit_pos = snapshot["exit_pos"]
            self.mobs = snapshot["mobs"]

    def handle_events(self):
        """Gere les clics et touches dans l'editeur."""
        if self.save_message_timer > 0:
            self.save_message_timer -= 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            
            if event.type == pygame.KEYDOWN:
                # Saisie ID
                if self.is_typing_id:
                    if event.key == pygame.K_RETURN: self.is_typing_id = False
                    elif event.key == pygame.K_BACKSPACE:
                        s = str(self.level_id)
                        self.level_id = int(s[:-1]) if len(s) > 1 else 0
                    elif event.unicode.isdigit():
                        self.level_id = int(str(self.level_id) + event.unicode)
                    return "EDITOR"
                
                # Saisie Nom (Modal Save)
                if self.show_save_panel:
                    if event.key == pygame.K_RETURN:
                        self.save_level()
                        self.show_save_panel = False
                    elif event.key == pygame.K_BACKSPACE: self.level_name = self.level_name[:-1]
                    elif event.key == pygame.K_ESCAPE: self.show_save_panel = False
                    else: self.level_name += event.unicode
                    return "EDITOR"

                # Shortcuts Généraux
                if event.key == pygame.K_ESCAPE:
                    if self.show_load_panel: self.show_load_panel = False
                    elif self.show_save_panel: self.show_save_panel = False
                    else: return "MENU"
                
                if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    self.show_save_panel = True

                # Undo / Redo
                if (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    if event.key == pygame.K_z: self.undo()
                    if event.key == pygame.K_y: self.redo()
                
                # Raccourcis outils
                shortcuts = {pygame.K_1: "WALL", pygame.K_2: "PATH", pygame.K_3: "START", 
                             pygame.K_4: "EXIT", pygame.K_5: "MOB_H", pygame.K_6: "MOB_V"}
                if event.key in shortcuts:
                    self.current_tool = shortcuts[event.key]

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                
                # Si le panel de sauvegarde est ouvert
                if self.show_save_panel:
                    if self.confirm_save_rect.collidepoint(mx, my):
                        self.save_level()
                        self.show_save_panel = False
                    elif self.cancel_save_rect.collidepoint(mx, my):
                        self.show_save_panel = False
                    return "EDITOR"

                # Si le panel de chargement est ouvert
                if self.show_load_panel:
                    if not self.load_panel_rect.collidepoint(mx, my):
                        self.show_load_panel = False
                    else:
                        header_h = 60
                        item_h = 50
                        for i, lvl in enumerate(self.loadable_levels):
                            item_rect = pygame.Rect(self.load_panel_rect.x + 20, self.load_panel_rect.y + header_h + i * item_h, 560, 40)
                            if item_rect.collidepoint(mx, my):
                                self.load_level_data(lvl)
                                self.show_load_panel = False
                    return "EDITOR"

                # Clic sur les inputs
                self.is_typing_id = self.id_input_rect.collidepoint(mx, my)

                # Boutons
                if self.save_rect.collidepoint(mx, my): self.show_save_panel = True
                if self.load_rect.collidepoint(mx, my): self.open_load_panel()
                if self.exit_editor_rect.collidepoint(mx, my): return "MENU"
                if self.clear_rect.collidepoint(mx, my):
                    self.save_snapshot()
                    self.maze = [[0 for _ in range(self.grid_w)] for _ in range(self.grid_h)]
                    self._add_borders()
                    self.mobs = []

                # Palette
                for i, tool in enumerate(self.tools):
                    if self._get_tool_rect(i).collidepoint(mx, my):
                        self.current_tool = tool

            # Dessin continu sur la grille (G=Dessin, D=Effaçage)
            mouse_pressed = pygame.mouse.get_pressed()
            if mouse_pressed[0] or mouse_pressed[2]: # Clic Gauche ou Droit
                mx, my = pygame.mouse.get_pos()
                if self.offset_x <= mx < self.offset_x + self.grid_w * self.tile_size and \
                   self.offset_y <= my < self.offset_y + self.grid_h * self.tile_size:
                    gx = (mx - self.offset_x) // self.tile_size
                    gy = (my - self.offset_y) // self.tile_size
                    
                    is_erase = mouse_pressed[2]
                    self.apply_tool(gx, gy, is_erase)

        return "EDITOR"

    def apply_tool(self, x, y, erase=False):
        """Applique l'outil selectionne ou efface a la case (x, y)."""
        # Vérifier si changement réel pour l'historique
        old_val = self.maze[y][x]
        
        if erase:
            if self.maze[y][x] == 0 and not any(m["start_pos"] == [x,y] for m in self.mobs) and [x,y] != self.start_pos and [x,y] != self.exit_pos:
                return # Pas de changement
            self.save_snapshot()
            self.maze[y][x] = 0
            self.mobs = [m for m in self.mobs if m["start_pos"] != [x, y]]
            return

        # Avant changement, save snapshot
        self.save_snapshot()

        if self.current_tool == "WALL":
            self.maze[y][x] = 1
        elif self.current_tool == "PATH":
            self.maze[y][x] = 0
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
            "name": self.level_name,
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
        print(f"Niveau {self.level_id} ({self.level_name}) sauvegardé !")
        self.save_message_timer = 90
        self._refresh_used_names()
        return True

    def open_load_panel(self):
        """Prépare et affiche la liste des niveaux chargeables."""
        from levels.levels_config import ALL_LEVELS
        customs = self.data_manager.load_custom_levels()
        self.loadable_levels = ALL_LEVELS + customs
        self.show_load_panel = True

    def load_level_data(self, data):
        """Charge les données d'un niveau dans l'éditeur."""
        self.save_snapshot()
        self.level_id = data.get("id", 101)
        self.level_name = data.get("name", "Nouveau Niveau")
        self.maze = [row[:] for row in data.get("maze")]
        
        # Mettre à jour les dimensions pour correspondre au niveau chargé
        self.grid_h = len(self.maze)
        self.grid_w = len(self.maze[0])
        self.offset_x = (WINDOW_WIDTH - (self.grid_w * self.tile_size)) // 2
        
        self.start_pos = data.get("start_pos", [1,1])[:]
        self.exit_pos = data.get("exit_pos", [1,1])[:]
        self.mobs = [m.copy() for m in data.get("mobs", [])]
        print(f"Niveau {self.level_id} ({self.level_name}) chargé !")

    def _draw_load_panel(self):
        """Affiche le panel de chargement."""
        # Overlay sombre
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Panel
        pygame.draw.rect(self.screen, (30, 30, 50), self.load_panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLORS["player"], self.load_panel_rect, 2, border_radius=10)
        
        # Titre panel
        title = self.fonts.get('medium').render("CHARGER UN NIVEAU", True, COLORS["white"])
        self.screen.blit(title, (self.load_panel_rect.centerx - title.get_width()//2, self.load_panel_rect.y + 10))

        # Liste des niveaux
        header_h = 70
        item_h = 50
        for i, lvl in enumerate(self.loadable_levels):
            if i > 9: break # Limite d'affichage simple
            rect = pygame.Rect(self.load_panel_rect.x + 20, self.load_panel_rect.y + header_h + i * item_h, 560, 40)
            col = (50, 50, 80) if rect.collidepoint(pygame.mouse.get_pos()) else (40, 40, 60)
            pygame.draw.rect(self.screen, col, rect, border_radius=5)
            
            txt = f"ID {lvl['id']} - {lvl['name']}"
            surf = self.fonts.get('small').render(txt, True, COLORS["white"])
            self.screen.blit(surf, (rect.x + 10, rect.y + 5))

    def _draw_save_panel(self):
        """Affiche le panel de sauvegarde."""
        # Overlay sombre
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Panel
        pygame.draw.rect(self.screen, (30, 30, 50), self.save_panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLORS["player"], self.save_panel_rect, 2, border_radius=10)
        
        # Titre
        title = self.fonts.get('medium').render("SAUVEGARDER LE NIVEAU", True, COLORS["white"])
        self.screen.blit(title, (self.save_panel_rect.centerx - title.get_width()//2, self.save_panel_rect.y + 20))

        # Input Nom
        txt_label = self.fonts.get('small').render("Entrez le nom du niveau :", True, COLORS["white"])
        self.screen.blit(txt_label, (self.save_input_rect.x, self.save_input_rect.y - 40))
        
        pygame.draw.rect(self.screen, (50, 50, 70), self.save_input_rect, border_radius=5)
        is_duplicate = self.level_name in self.used_names
        border_col = (255, 0, 0) if is_duplicate else COLORS["player"]
        pygame.draw.rect(self.screen, border_col, self.save_input_rect, 2, border_radius=5)
        
        name_surf = self.fonts.get('medium').render(self.level_name + "|", True, COLORS["white"])
        self.screen.blit(name_surf, (self.save_input_rect.x + 15, self.save_input_rect.y + 5))
        
        if is_duplicate:
            warn = self.fonts.get('controls').render("NOM DEJA UTILISE !", True, (255, 0, 0))
            self.screen.blit(warn, (self.save_input_rect.x, self.save_input_rect.bottom + 5))

        # Boutons Valider / Annuler
        pygame.draw.rect(self.screen, (0, 150, 0), self.confirm_save_rect, border_radius=5)
        txt_v = self.fonts.get('small').render("VALIDER", True, COLORS["white"])
        self.screen.blit(txt_v, (self.confirm_save_rect.centerx - txt_v.get_width()//2, self.confirm_save_rect.centery - txt_v.get_height()//2))

        pygame.draw.rect(self.screen, (150, 0, 0), self.cancel_save_rect, border_radius=5)
        txt_a = self.fonts.get('small').render("ANNULER", True, COLORS["white"])
        self.screen.blit(txt_a, (self.cancel_save_rect.centerx - txt_a.get_width()//2, self.cancel_save_rect.centery - txt_a.get_height()//2))

        # Rappel des noms existants
        side_x = self.save_panel_rect.right - 250
        title_list = self.fonts.get('controls').render("Noms déjà pris :", True, (150, 150, 150))
        self.screen.blit(title_list, (side_x, self.save_panel_rect.y + 100))
        for i, name in enumerate(self.used_names[:8]):
            txt = self.fonts.get('controls').render(f"- {name}", True, (120, 120, 120))
            self.screen.blit(txt, (side_x, self.save_panel_rect.y + 130 + i * 25))

    def _get_tool_rect(self, index):
        """Calcule le rectangle d'un outil dans la palette."""
        palette_y = WINDOW_HEIGHT - 100
        spacing = 150
        start_x = (WINDOW_WIDTH - (len(self.tools) * spacing)) // 2
        return pygame.Rect(start_x + index * spacing, palette_y, 140, 80)

    def draw(self):
        """Rendu de l'editeur."""
        self.screen.fill(COLORS["menu_bg"])
        
        # Titre
        title_surf = self.fonts.get('medium').render("EDITEUR DE NIVEAU", True, COLORS["player"])
        self.screen.blit(title_surf, (200, 20))
        
        # Input ID
        pygame.draw.rect(self.screen, (50, 50, 70), self.id_input_rect, border_radius=5)
        border_id = COLORS["player"] if self.is_typing_id else COLORS["white"]
        pygame.draw.rect(self.screen, border_id, self.id_input_rect, 2, border_radius=5)
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
            
            # Nom de l'outil
            txt = self.fonts.get('controls').render(tool, True, COLORS["white"])
            self.screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.y + 5))
            
            # Dessin de la tuile sous le nom
            preview_rect = pygame.Rect(rect.centerx - 15, rect.y + 35, 30, 30)
            if tool == "WALL":
                pygame.draw.rect(self.screen, COLORS["wall"], preview_rect)
                pygame.draw.rect(self.screen, COLORS["wall_border"], preview_rect, 1)
            elif tool == "PATH":
                pygame.draw.rect(self.screen, COLORS["path"], preview_rect)
                pygame.draw.rect(self.screen, (100, 100, 100), preview_rect, 1)
            elif tool == "START":
                pygame.draw.rect(self.screen, COLORS["player"], preview_rect)
            elif tool == "EXIT":
                pygame.draw.rect(self.screen, COLORS["exit"], preview_rect)
            elif tool == "MOB_H":
                pygame.draw.circle(self.screen, (255, 100, 0), preview_rect.center, 12)
            elif tool == "MOB_V":
                pygame.draw.circle(self.screen, (255, 0, 255), preview_rect.center, 12)

        # Boutons
        save_col = (0, 180, 0) if self.save_message_timer == 0 else (0, 255, 0)
        save_text = "SAVE" if self.save_message_timer == 0 else f"OK: {self.level_name}"
        
        for r, text, col in [(self.save_rect, save_text, save_col), 
                              (self.load_rect, "LOAD", (0, 100, 200)),
                              (self.exit_editor_rect, "BACK", (180, 0, 0)),
                              (self.clear_rect, "CLEAR", (100, 100, 100))]:
            pygame.draw.rect(self.screen, col, r, border_radius=5)
            surf = self.fonts.get('small').render(text, True, COLORS["white"])
            self.screen.blit(surf, (r.centerx - surf.get_width() // 2, r.centery - surf.get_height() // 2))

        if self.show_load_panel:
            self._draw_load_panel()
        elif self.show_save_panel:
            self._draw_save_panel()
