# -*- coding: utf-8 -*-
import pygame
from config import COLORS, TILE_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT
from src.editeur.ui import draw_editor
from src.editeur.events import handle_editor_events

class LevelEditor:
    """Editeur de niveaux interactif et complet (Version Barre Latérale)."""

    def __init__(self, screen, font_manager, data_manager):
        self.screen = screen
        self.fonts = font_manager
        self.data_manager = data_manager
        
        # Paramètres de la grille
        self.grid_w = 20
        self.grid_h = 15
        self.tile_size = 40
        
        # UI Rects
        self.sidebar_width = 300
        self.sidebar_rect = pygame.Rect(0, 0, self.sidebar_width, WINDOW_HEIGHT)
        
        self.offset_x = self.sidebar_width + (WINDOW_WIDTH - self.sidebar_width - self.grid_w * self.tile_size) // 2
        self.offset_y = (WINDOW_HEIGHT - self.grid_h * self.tile_size) // 2
        
        # Données du niveau
        self.maze = [[0 for _ in range(self.grid_w)] for _ in range(self.grid_h)]
        self._add_borders()
        self.start_pos = [1, 1]
        self.exit_pos = [self.grid_w - 2, self.grid_h - 2]
        self.mobs = []
        
        # Outils séparés pour une meilleure lisibilité
        self.tile_tools = ["WALL", "PATH", "START", "EXIT", "TREE"]
        self.mob_tools = ["1 Horizon", "2 Verti", "3 Trackeur", "4 Missile"]
        self.current_tool = "WALL"
        
        # Rects Boutons
        self.save_rect = pygame.Rect(WINDOW_WIDTH - 200, 20, 160, 50)
        self.test_rect = pygame.Rect(WINDOW_WIDTH - 200, 80, 160, 50)
        self.exit_editor_rect = pygame.Rect(WINDOW_WIDTH - 200, 140, 160, 50)
        self.clear_rect = pygame.Rect(WINDOW_WIDTH - 200, 200, 160, 50)
        self.id_input_rect = pygame.Rect(self.sidebar_width + 20, 20, 150, 45)
        self.theme_toggle_rect = pygame.Rect(self.sidebar_width + 180, 20, 160, 45)
        self.render_mode = "CHIADÉ" # "DÉFAUT" ou "CHIADÉ"
        
        self.is_typing_id = False
        self.level_id_str = "101"
        self.level_name = "Nouveau Niveau"
        self.save_message_timer = 0
        
        # Historique
        self.history = []
        self.redo_stack = []
        self.max_history = 30
        
        # Sidebar Scroll
        self.sidebar_scroll_y = 0
        self.max_sidebar_scroll = 0
        self.sidebar_item_h = 70
        
        # Panels Modals
        from src.editeur.mob_editor import MobEditorModal
        self.mob_editor = MobEditorModal(self)
        
        self.show_delete_panel = False
        self.level_to_delete = None
        self.delete_panel_rect = pygame.Rect(WINDOW_WIDTH // 2 - 250, WINDOW_HEIGHT // 2 - 150, 500, 300)
        self.confirm_delete_rect = pygame.Rect(self.delete_panel_rect.x + 50, self.delete_panel_rect.y + 200, 150, 50)
        self.cancel_delete_rect = pygame.Rect(self.delete_panel_rect.x + 300, self.delete_panel_rect.y + 200, 150, 50)

        self.loadable_levels = []
        self._refresh_loadable_levels()

        self.show_save_panel = False
        self.save_panel_rect = pygame.Rect(WINDOW_WIDTH // 2 - 350, WINDOW_HEIGHT // 2 - 250, 700, 500)
        self.confirm_save_rect = pygame.Rect(self.save_panel_rect.x + 100, self.save_panel_rect.y + 400, 200, 60)
        self.cancel_save_rect = pygame.Rect(self.save_panel_rect.x + 400, self.save_panel_rect.y + 400, 200, 60)
        
        # Champs de saisie dans le Save Panel
        self.save_id_rect = pygame.Rect(self.save_panel_rect.x + 50, self.save_panel_rect.y + 100, 200, 60)
        self.save_name_rect = pygame.Rect(self.save_panel_rect.x + 50, self.save_panel_rect.y + 220, 600, 60)
        self.save_focus = "id" # "id" ou "name"
        
        self.show_confirm_save = False
        self.confirm_panel_rect = pygame.Rect(WINDOW_WIDTH // 2 - 250, WINDOW_HEIGHT // 2 - 100, 500, 200)
        
        # Liste des noms utilisés
        self.used_names = []
        self._refresh_used_names()

    def _refresh_loadable_levels(self):
        """Met à jour la liste des niveaux pour la sidebar."""
        from levels.levels_config import ALL_LEVELS
        # On recharge dynamiquement le module pour avoir les dernières modifs
        import importlib
        import levels.levels_config
        importlib.reload(levels.levels_config)
        self.loadable_levels = levels.levels_config.ALL_LEVELS
        self.max_sidebar_scroll = max(0, len(self.loadable_levels) * self.sidebar_item_h - (WINDOW_HEIGHT - 120))

    def _refresh_used_names(self):
        """Récupère tous les noms de niveaux existants."""
        self._refresh_loadable_levels()
        self.used_names = [lvl["name"] for lvl in self.loadable_levels]

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
        if len(self.history) > self.max_history: self.history.pop(0)
        self.redo_stack = []

    def undo(self):
        if self.history:
            self.redo_stack.append({"maze": [row[:] for row in self.maze], "start_pos": self.start_pos[:], "exit_pos": self.exit_pos[:], "mobs": [m.copy() for m in self.mobs]})
            s = self.history.pop()
            self.maze, self.start_pos, self.exit_pos, self.mobs = s["maze"], s["start_pos"], s["exit_pos"], s["mobs"]

    def redo(self):
        if self.redo_stack:
            self.history.append({"maze": [row[:] for row in self.maze], "start_pos": self.start_pos[:], "exit_pos": self.exit_pos[:], "mobs": [m.copy() for m in self.mobs]})
            s = self.redo_stack.pop()
            self.maze, self.start_pos, self.exit_pos, self.mobs = s["maze"], s["start_pos"], s["exit_pos"], s["mobs"]

    def handle_events(self):
        return handle_editor_events(self)

    def draw(self):
        draw_editor(self)

    def save_level(self):
        """Sauvegarde le niveau et synchronise levels_config.py."""
        self._refresh_loadable_levels()
        all_levels = self.loadable_levels
        
        # Convertir ID str -> int
        try: lid = int(self.level_id_str)
        except ValueError: lid = 999 
            
        # Dico pour merge
        full_sync_dict = {lvl["id"]: lvl for lvl in all_levels}
        
        new_level = {
            "id": lid, 
            "name": self.level_name, 
            "maze": [row[:] for row in self.maze],
            "start_pos": self.start_pos[:], 
            "exit_pos": self.exit_pos[:], 
            "mobs": [m.copy() for m in self.mobs],
            "colors": {"wall": (100, 100, 100), "wall_border": (150, 150, 150), "path": (30, 30, 30), "exit": (255, 20, 147)}
        }
        
        full_sync_dict[lid] = new_level
        sorted_levels = [full_sync_dict[k] for k in sorted(full_sync_dict.keys())]
        
        self.data_manager.sync_to_python_config(sorted_levels)
        self.data_manager.save_custom_levels([lvl for lvl in sorted_levels if lvl["id"] >= 100])
        
        self.save_message_timer = 90
        self._refresh_loadable_levels()
        self._refresh_used_names()
        return True

    def delete_level(self, lid):
        """Supprime un niveau."""
        self._refresh_loadable_levels()
        all_levels = [l for l in self.loadable_levels if l["id"] != lid]
        
        self.data_manager.sync_to_python_config(all_levels)
        self.data_manager.save_custom_levels([l for l in all_levels if l["id"] >= 100])
        
        self._refresh_loadable_levels()
        self._refresh_used_names()

    def get_current_level_data(self):
        """Retourne les données du niveau actuel sous forme de dictionnaire."""
        try: lid = int(self.level_id_str)
        except: lid = 999
        return {
            "id": lid,
            "name": self.level_name,
            "maze": [row[:] for row in self.maze],
            "start_pos": self.start_pos[:],
            "exit_pos": self.exit_pos[:],
            "mobs": [m.copy() for m in self.mobs],
            "colors": {"wall": (100, 100, 100), "wall_border": (150, 150, 150), "path": (30, 30, 30), "exit": (255, 20, 147)}
        }

    def load_level_data(self, data):
        self.save_snapshot()
        self.level_id_str = str(data.get("id", 101))
        self.level_name = data.get("name", "Nouveau Niveau")
        self.maze = [row[:] for row in data.get("maze")]
        self.grid_h, self.grid_w = len(self.maze), len(self.maze[0])
        
        # Recalculer offset
        self.offset_x = self.sidebar_width + (WINDOW_WIDTH - self.sidebar_width - self.grid_w * self.tile_size) // 2
        self.offset_y = (WINDOW_HEIGHT - self.grid_h * self.tile_size) // 2
        
        self.start_pos, self.exit_pos = data.get("start_pos", [1,1])[:], data.get("exit_pos", [1,1])[:]
        self.mobs = [m.copy() for m in data.get("mobs", [])]

    def _get_tool_rect(self, category, index):
        palette_y, spacing = WINDOW_HEIGHT - 100, 120
        available_w = WINDOW_WIDTH - self.sidebar_width
        
        if category == "tile":
            # Section gauche de la palette
            start_x = self.sidebar_width + 50
            return pygame.Rect(start_x + index * spacing, palette_y, 110, 80)
        else:
            # Section droite de la palette (mobs)
            start_x = self.sidebar_width + available_w - (len(self.mob_tools) * spacing) - 50
            return pygame.Rect(start_x + index * spacing, palette_y, 110, 80)
