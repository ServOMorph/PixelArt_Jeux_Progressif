# -*- coding: utf-8 -*-
import pygame
from config import COLORS, TILE_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT
from src.editeur.ui import draw_editor
from src.editeur.events import handle_editor_events

class LevelEditor:
    """Editeur de niveaux interactif et complet (Version Refactorisée)."""

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
        self.id_input_rect = pygame.Rect(WINDOW_WIDTH // 2 - 250, 20, 200, 50)
        self.load_rect = pygame.Rect(WINDOW_WIDTH // 2, 20, 160, 50)
        self.clear_rect = pygame.Rect(WINDOW_WIDTH // 2 + 170, 20, 160, 50)
        
        self.is_typing_id = False
        self.level_id_str = "101"
        self.level_name = "Nouveau Niveau"
        self.save_message_timer = 0
        
        # Historique
        self.history = []
        self.redo_stack = []
        self.max_history = 30
        
        # Panels Modals
        self.show_load_panel = False
        self.loadable_levels = []
        self.load_panel_rect = pygame.Rect(WINDOW_WIDTH // 2 - 300, WINDOW_HEIGHT // 2 - 300, 600, 600)

        self.show_save_panel = False
        self.save_panel_rect = pygame.Rect(WINDOW_WIDTH // 2 - 350, WINDOW_HEIGHT // 2 - 250, 700, 500)
        self.confirm_save_rect = pygame.Rect(self.save_panel_rect.x + 100, self.save_panel_rect.y + 400, 200, 60)
        self.cancel_save_rect = pygame.Rect(self.save_panel_rect.x + 400, self.save_panel_rect.y + 400, 200, 60)
        
        # Champs de saisie dans le Save Panel
        self.save_id_rect = pygame.Rect(self.save_panel_rect.x + 50, self.save_panel_rect.y + 100, 200, 60)
        self.save_name_rect = pygame.Rect(self.save_panel_rect.x + 50, self.save_panel_rect.y + 220, 600, 60)
        self.save_focus = "id" # "id" ou "name"
        
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
        custom_levels = self.data_manager.load_custom_levels()
        
        # Convertir ID str -> int
        try:
            lid = int(self.level_id_str)
        except ValueError:
            lid = 999 # Fallback si vide
            
        custom_levels = [l for l in custom_levels if l["id"] != lid]
        new_level = {
            "id": lid, "name": self.level_name, "maze": self.maze,
            "start_pos": self.start_pos, "exit_pos": self.exit_pos, "mobs": self.mobs,
            "colors": {"wall": (100, 100, 100), "wall_border": (150, 150, 150), "path": (30, 30, 30), "exit": (255, 20, 147)}
        }
        custom_levels.append(new_level)
        self.data_manager.save_custom_levels(custom_levels)
        self.save_message_timer = 90
        self._refresh_used_names()
        return True

    def open_load_panel(self):
        from levels.levels_config import ALL_LEVELS
        customs = self.data_manager.load_custom_levels()
        self.loadable_levels = ALL_LEVELS + customs
        self.show_load_panel = True

    def load_level_data(self, data):
        self.save_snapshot()
        self.level_id_str = str(data.get("id", 101))
        self.level_name = data.get("name", "Nouveau Niveau")
        self.maze = [row[:] for row in data.get("maze")]
        self.grid_h, self.grid_w = len(self.maze), len(self.maze[0])
        self.offset_x = (WINDOW_WIDTH - (self.grid_w * self.tile_size)) // 2
        self.start_pos, self.exit_pos = data.get("start_pos", [1,1])[:], data.get("exit_pos", [1,1])[:]
        self.mobs = [m.copy() for m in data.get("mobs", [])]

    def _get_tool_rect(self, index):
        palette_y, spacing = WINDOW_HEIGHT - 100, 150
        start_x = (WINDOW_WIDTH - (len(self.tools) * spacing)) // 2
        return pygame.Rect(start_x + index * spacing, palette_y, 140, 80)
