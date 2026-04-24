# -*- coding: utf-8 -*-
import pygame
from config import COLORS, TILE_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT

def draw_editor(editor):
    """Rendu principal de l'editeur."""
    editor.screen.fill(COLORS["menu_bg"])
    
    # Titre
    title_surf = editor.fonts.get('medium').render("EDITEUR DE NIVEAU", True, COLORS["player"])
    editor.screen.blit(title_surf, (200, 20))
    
    # Input ID (Global)
    pygame.draw.rect(editor.screen, (50, 50, 70), editor.id_input_rect, border_radius=5)
    border_id = COLORS["player"] if editor.is_typing_id else COLORS["white"]
    pygame.draw.rect(editor.screen, border_id, editor.id_input_rect, 2, border_radius=5)
    id_text = editor.fonts.get('small').render(f"ID: {editor.level_id_str}", True, COLORS["white"])
    editor.screen.blit(id_text, (editor.id_input_rect.x + 10, editor.id_input_rect.y + 10))

    # Grille
    for y in range(editor.grid_h):
        for x in range(editor.grid_w):
            rect = pygame.Rect(editor.offset_x + x * editor.tile_size, editor.offset_y + y * editor.tile_size, editor.tile_size, editor.tile_size)
            
            if editor.maze[y][x] == 1:
                pygame.draw.rect(editor.screen, COLORS["wall"], rect)
                pygame.draw.rect(editor.screen, COLORS["wall_border"], rect, 1)
            else:
                pygame.draw.rect(editor.screen, COLORS["path"], rect)
                pygame.draw.rect(editor.screen, (40, 40, 60), rect, 1)
            
            if [x, y] == editor.start_pos:
                pygame.draw.rect(editor.screen, COLORS["player"], rect.inflate(-12, -12))
            elif [x, y] == editor.exit_pos:
                pygame.draw.rect(editor.screen, COLORS["exit"], rect.inflate(-12, -12))
            
            for mob in editor.mobs:
                if mob["start_pos"] == [x, y]:
                    color = (255, 100, 0) if mob["pattern"] == "horizontal" else (255, 0, 255)
                    pygame.draw.circle(editor.screen, color, rect.center, editor.tile_size // 3)

    # Palette
    for i, tool in enumerate(editor.tools):
        rect = editor._get_tool_rect(i)
        bg_col = (70, 70, 100) if editor.current_tool == tool else (30, 30, 50)
        pygame.draw.rect(editor.screen, bg_col, rect, border_radius=8)
        pygame.draw.rect(editor.screen, COLORS["white"], rect, 2, border_radius=8)
        
        # Nom de l'outil
        txt = editor.fonts.get('controls').render(tool, True, COLORS["white"])
        editor.screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.y + 5))
        
        # Dessin de la tuile sous le nom
        preview_rect = pygame.Rect(rect.centerx - 15, rect.y + 35, 30, 30)
        if tool == "WALL":
            pygame.draw.rect(editor.screen, COLORS["wall"], preview_rect)
            pygame.draw.rect(editor.screen, COLORS["wall_border"], preview_rect, 1)
        elif tool == "PATH":
            pygame.draw.rect(editor.screen, COLORS["path"], preview_rect)
            pygame.draw.rect(editor.screen, (100, 100, 100), preview_rect, 1)
        elif tool == "START":
            pygame.draw.rect(editor.screen, COLORS["player"], preview_rect)
        elif tool == "EXIT":
            pygame.draw.rect(editor.screen, COLORS["exit"], preview_rect)
        elif tool == "MOB_H":
            pygame.draw.circle(editor.screen, (255, 100, 0), preview_rect.center, 12)
        elif tool == "MOB_V":
            pygame.draw.circle(editor.screen, (255, 0, 255), preview_rect.center, 12)

    # Boutons
    save_col = (0, 180, 0) if editor.save_message_timer == 0 else (0, 255, 0)
    save_text = "SAVE" if editor.save_message_timer == 0 else f"OK: {editor.level_name}"
    
    buttons = [
        (editor.save_rect, save_text, save_col), 
        (editor.load_rect, "LOAD", (0, 100, 200)),
        (editor.exit_editor_rect, "BACK", (180, 0, 0)),
        (editor.clear_rect, "CLEAR", (100, 100, 100))
    ]
    for r, text, col in buttons:
        pygame.draw.rect(editor.screen, col, r, border_radius=5)
        surf = editor.fonts.get('small').render(text, True, COLORS["white"])
        editor.screen.blit(surf, (r.centerx - surf.get_width() // 2, r.centery - surf.get_height() // 2))

    if editor.show_load_panel:
        draw_load_panel(editor)
    elif editor.show_save_panel:
        draw_save_panel(editor)

def draw_load_panel(editor):
    """Affiche le panel de chargement."""
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    editor.screen.blit(overlay, (0, 0))

    pygame.draw.rect(editor.screen, (30, 30, 50), editor.load_panel_rect, border_radius=10)
    pygame.draw.rect(editor.screen, COLORS["player"], editor.load_panel_rect, 2, border_radius=10)
    
    title = editor.fonts.get('medium').render("CHARGER UN NIVEAU", True, COLORS["white"])
    editor.screen.blit(title, (editor.load_panel_rect.centerx - title.get_width()//2, editor.load_panel_rect.y + 10))

    header_h = 70
    item_h = 50
    for i, lvl in enumerate(editor.loadable_levels):
        if i > 9: break
        rect = pygame.Rect(editor.load_panel_rect.x + 20, editor.load_panel_rect.y + header_h + i * item_h, 560, 40)
        col = (50, 50, 80) if rect.collidepoint(pygame.mouse.get_pos()) else (40, 40, 60)
        pygame.draw.rect(editor.screen, col, rect, border_radius=5)
        
        txt = f"ID {lvl['id']} - {lvl['name']}"
        surf = editor.fonts.get('small').render(txt, True, COLORS["white"])
        editor.screen.blit(surf, (rect.x + 10, rect.y + 5))

def draw_save_panel(editor):
    """Affiche le panel de sauvegarde."""
    # Overlay sombre
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    editor.screen.blit(overlay, (0, 0))

    # Panel
    pygame.draw.rect(editor.screen, (30, 30, 50), editor.save_panel_rect, border_radius=10)
    pygame.draw.rect(editor.screen, COLORS["player"], editor.save_panel_rect, 2, border_radius=10)
    
    # Titre
    title = editor.fonts.get('medium').render("SAUVEGARDER LE NIVEAU", True, COLORS["white"])
    editor.screen.blit(title, (editor.save_panel_rect.centerx - title.get_width()//2, editor.save_panel_rect.y + 15))

    # Input ID
    lbl_id = editor.fonts.get('small').render("ID (ex: 105) :", True, COLORS["white"])
    editor.screen.blit(lbl_id, (editor.save_id_rect.x, editor.save_id_rect.y - 35))
    pygame.draw.rect(editor.screen, (50, 50, 70), editor.save_id_rect, border_radius=5)
    border_id = COLORS["player"] if editor.save_focus == "id" else COLORS["white"]
    pygame.draw.rect(editor.screen, border_id, editor.save_id_rect, 2, border_radius=5)
    txt_id = editor.fonts.get('medium').render(editor.level_id_str + ("|" if editor.save_focus == "id" else ""), True, COLORS["white"])
    editor.screen.blit(txt_id, (editor.save_id_rect.x + 10, editor.save_id_rect.y + 5))

    # Input Nom
    lbl_name = editor.fonts.get('small').render("Nom du niveau :", True, COLORS["white"])
    editor.screen.blit(lbl_name, (editor.save_name_rect.x, editor.save_name_rect.y - 35))
    pygame.draw.rect(editor.screen, (50, 50, 70), editor.save_name_rect, border_radius=5)
    is_duplicate = editor.level_name in editor.used_names
    border_name = (255, 0, 0) if is_duplicate else (COLORS["player"] if editor.save_focus == "name" else COLORS["white"])
    pygame.draw.rect(editor.screen, border_name, editor.save_name_rect, 2, border_radius=5)
    txt_name = editor.fonts.get('medium').render(editor.level_name + ("|" if editor.save_focus == "name" else ""), True, COLORS["white"])
    editor.screen.blit(txt_name, (editor.save_name_rect.x + 10, editor.save_name_rect.y + 5))
    
    if is_duplicate:
        warn = editor.fonts.get('controls').render("NOM DEJA UTILISE !", True, (255, 0, 0))
        editor.screen.blit(warn, (editor.save_name_rect.x, editor.save_name_rect.bottom + 5))

    # Boutons Valider / Annuler
    pygame.draw.rect(editor.screen, (0, 150, 0), editor.confirm_save_rect, border_radius=5)
    txt_v = editor.fonts.get('small').render("VALIDER", True, COLORS["white"])
    editor.screen.blit(txt_v, (editor.confirm_save_rect.centerx - txt_v.get_width()//2, editor.confirm_save_rect.centery - txt_v.get_height()//2))

    pygame.draw.rect(editor.screen, (150, 0, 0), editor.cancel_save_rect, border_radius=5)
    txt_a = editor.fonts.get('small').render("ANNULER", True, COLORS["white"])
    editor.screen.blit(txt_a, (editor.cancel_save_rect.centerx - txt_a.get_width()//2, editor.cancel_save_rect.centery - txt_a.get_height()//2))

    # Rappel des noms
    side_x = editor.save_panel_rect.right - 250
    title_list = editor.fonts.get('controls').render("Noms déjà pris :", True, (150, 150, 150))
    editor.screen.blit(title_list, (side_x, editor.save_panel_rect.y + 100))
    for i, name in enumerate(editor.used_names[:8]):
        txt = editor.fonts.get('controls').render(f"- {name}", True, (120, 120, 120))
        editor.screen.blit(txt, (side_x, editor.save_panel_rect.y + 130 + i * 25))
