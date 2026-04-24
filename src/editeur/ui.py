# -*- coding: utf-8 -*-
import pygame
from config import COLORS, TILE_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT

def draw_editor(editor):
    """Rendu principal de l'editeur."""
    editor.screen.fill(COLORS["menu_bg"])
    
    # Sidebar
    draw_sidebar(editor)
    
    # Titre
    title_surf = editor.fonts.get('medium').render("EDITEUR DE NIVEAU", True, COLORS["player"])
    workspace_center_x = editor.sidebar_width + (WINDOW_WIDTH - editor.sidebar_width) // 2
    editor.screen.blit(title_surf, (workspace_center_x - title_surf.get_width() // 2, 20))
    
    # Input ID (Global)
    pygame.draw.rect(editor.screen, (50, 50, 70), editor.id_input_rect, border_radius=5)
    border_id = COLORS["player"] if editor.is_typing_id else COLORS["white"]
    pygame.draw.rect(editor.screen, border_id, editor.id_input_rect, 2, border_radius=5)
    display_id = editor.level_id_str + ("|" if editor.is_typing_id else "")
    id_text = editor.fonts.get('small').render(f"ID: {display_id}", True, COLORS["white"])
    editor.screen.blit(id_text, (editor.id_input_rect.x + 10, editor.id_input_rect.y + 10))

    # Bouton Toggle Thème
    bg_theme = (0, 200, 200) if editor.render_mode == "CHIADÉ" else (60, 60, 80)
    pygame.draw.rect(editor.screen, bg_theme, editor.theme_toggle_rect, border_radius=5)
    pygame.draw.rect(editor.screen, COLORS["white"], editor.theme_toggle_rect, 1, border_radius=5)
    theme_text = editor.fonts.get('small').render(f"Mode: {editor.render_mode}", True, COLORS["white"])
    editor.screen.blit(theme_text, (editor.theme_toggle_rect.centerx - theme_text.get_width()//2, editor.theme_toggle_rect.centery - theme_text.get_height()//2))

    # Grille
    for y in range(editor.grid_h):
        for x in range(editor.grid_w):
            rect = pygame.Rect(editor.offset_x + x * editor.tile_size, editor.offset_y + y * editor.tile_size, editor.tile_size, editor.tile_size)
            
            if editor.render_mode == "CHIADÉ":
                _draw_tile_chiade(editor, x, y, rect)
            else:
                _draw_tile_defaut(editor, x, y, rect)
            
            # Dessin des mobs sur la grille
            for mob in editor.mobs:
                if mob["start_pos"] == [x, y]:
                    if editor.render_mode == "CHIADÉ":
                        _draw_mob_chiade(editor, mob, rect)
                    else:
                        _draw_mob_defaut(editor, mob, rect)
                    
                    # Bouton Réglages sur le mob
                    settings_rect = pygame.Rect(rect.right - 15, rect.y + 2, 12, 12)
                    pygame.draw.rect(editor.screen, (255, 255, 255), settings_rect, border_radius=2)
                    txt = editor.fonts.get('controls').render("G", True, (0, 0, 0))
                    editor.screen.blit(txt, (settings_rect.x + 2, settings_rect.y - 2))

    # Palette Tuiles
    tile_label = editor.fonts.get('controls').render("TUILES", True, (150, 150, 150))
    editor.screen.blit(tile_label, (editor.sidebar_width + 50, WINDOW_HEIGHT - 125))
    for i, tool in enumerate(editor.tile_tools):
        rect = editor._get_tool_rect("tile", i)
        bg_col = (70, 70, 100) if editor.current_tool == tool else (30, 30, 50)
        pygame.draw.rect(editor.screen, bg_col, rect, border_radius=8)
        pygame.draw.rect(editor.screen, COLORS["white"], rect, 2, border_radius=8)
        txt = editor.fonts.get('controls').render(tool, True, COLORS["white"])
        editor.screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.y + 5))
        _draw_tool_preview(editor, tool, rect)

    # Palette Mobs
    mob_label = editor.fonts.get('controls').render("ENNEMIS", True, (150, 150, 150))
    editor.screen.blit(mob_label, (WINDOW_WIDTH - 350, WINDOW_HEIGHT - 125))
    for i, tool in enumerate(editor.mob_tools):
        rect = editor._get_tool_rect("mob", i)
        bg_col = (70, 70, 100) if editor.current_tool == tool else (30, 30, 50)
        pygame.draw.rect(editor.screen, bg_col, rect, border_radius=8)
        pygame.draw.rect(editor.screen, COLORS["white"], rect, 2, border_radius=8)
        txt = editor.fonts.get('controls').render(tool, True, COLORS["white"])
        editor.screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.y + 5))
        _draw_tool_preview(editor, tool, rect)

def _draw_tool_preview(editor, tool, rect):
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
    elif tool == "TREE":
        pygame.draw.rect(editor.screen, COLORS["tree"], preview_rect, border_radius=5)
        pygame.draw.rect(editor.screen, COLORS["tree_top"], preview_rect.inflate(-10, -10), border_radius=3)
    elif tool == "1 Horizon":
        pygame.draw.circle(editor.screen, (255, 165, 0), preview_rect.center, 12)
    elif tool == "2 Verti":
        pygame.draw.circle(editor.screen, (180, 0, 255), preview_rect.center, 12)
    elif tool == "3 Trackeur":
        pygame.draw.circle(editor.screen, (255, 255, 0), preview_rect.center, 12)
    elif tool == "4 Missile":
        pygame.draw.circle(editor.screen, (0, 255, 128), preview_rect.center, 12)

    # Boutons
    save_col = (0, 180, 0) if editor.save_message_timer == 0 else (0, 255, 0)
    save_text = "SAVE" if editor.save_message_timer == 0 else f"OK: {editor.level_name}"
    
    buttons = [
        (editor.save_rect, save_text, save_col), 
        (editor.test_rect, "TEST", (0, 100, 200)),
        (editor.exit_editor_rect, "BACK", (180, 0, 0)),
        (editor.clear_rect, "CLEAR", (100, 100, 100))
    ]
    for r, text, col in buttons:
        pygame.draw.rect(editor.screen, col, r, border_radius=5)
        surf = editor.fonts.get('small').render(text, True, COLORS["white"])
        editor.screen.blit(surf, (r.centerx - surf.get_width() // 2, r.centery - surf.get_height() // 2))

def _draw_tile_defaut(editor, x, y, rect):
    """Rendu simple géométrique."""
    if editor.maze[y][x] == 1:
        pygame.draw.rect(editor.screen, COLORS["wall"], rect)
        pygame.draw.rect(editor.screen, COLORS["wall_border"], rect, 1)
    elif editor.maze[y][x] == 2:
        pygame.draw.rect(editor.screen, COLORS["tree"], rect, border_radius=8)
        pygame.draw.rect(editor.screen, COLORS["tree_top"], rect.inflate(-12, -12), border_radius=4)
    else:
        pygame.draw.rect(editor.screen, COLORS["path"], rect)
        pygame.draw.rect(editor.screen, (40, 40, 60), rect, 1)
    
    if [x, y] == editor.start_pos:
        pygame.draw.rect(editor.screen, COLORS["player"], rect.inflate(-12, -12))
    elif [x, y] == editor.exit_pos:
        pygame.draw.rect(editor.screen, COLORS["exit"], rect.inflate(-12, -12))

def _draw_tile_chiade(editor, x, y, rect):
    """Rendu Pixel Art Premium avec détails."""
    if editor.maze[y][x] == 1: # MUR
        if editor.ui_renderer and "wall" in editor.ui_renderer.sprites:
            # Scale sprite to editor tile size
            sprite = pygame.transform.smoothscale(editor.ui_renderer.sprites["wall"], (rect.width, rect.height))
            editor.screen.blit(sprite, rect)
        else:
            pygame.draw.rect(editor.screen, (60, 60, 80), rect) # Fallback
    elif editor.maze[y][x] == 2: # ARBRE
        pygame.draw.circle(editor.screen, (34, 139, 34), rect.center, rect.width//3)
        pygame.draw.circle(editor.screen, (50, 160, 50), rect.center, rect.width//5)
    else: # SOL
        if editor.ui_renderer and "path" in editor.ui_renderer.sprites:
            sprite = pygame.transform.smoothscale(editor.ui_renderer.sprites["path"], (rect.width, rect.height))
            editor.screen.blit(sprite, rect)
        else:
            pygame.draw.rect(editor.screen, (25, 25, 35), rect)

    # Start/Exit Premium
    if [x, y] == editor.start_pos:
        if editor.ui_renderer and "player" in editor.ui_renderer.sprites:
            sprite = pygame.transform.smoothscale(editor.ui_renderer.sprites["player"], (rect.width, rect.height))
            editor.screen.blit(sprite, rect)
        else:
            pygame.draw.circle(editor.screen, (0, 255, 255), rect.center, rect.width//2 - 5, 2)
    elif [x, y] == editor.exit_pos:
        pygame.draw.circle(editor.screen, (255, 20, 147), rect.center, rect.width//2 - 5, 3)

def _draw_mob_defaut(editor, mob, rect):
    if mob["pattern"] == "horizontal": color = (255, 165, 0) 
    elif mob["pattern"] == "vertical": color = (180, 0, 255) 
    elif mob["pattern"] == "chaser": color = (255, 255, 0) 
    else: color = (0, 255, 128) 
    pygame.draw.circle(editor.screen, color, rect.center, editor.tile_size // 3)

def _draw_mob_chiade(editor, mob, rect):
    """Rendu Mob avec détails (Pixel Art style)."""
    cx, cy = rect.center
    sprite_key = None
    if mob["pattern"] == "horizontal": sprite_key = "mob_h"
    elif mob["pattern"] == "vertical": sprite_key = "mob_v"
    
    if sprite_key and editor.ui_renderer and sprite_key in editor.ui_renderer.sprites:
        sprite = pygame.transform.smoothscale(editor.ui_renderer.sprites[sprite_key], (rect.width, rect.height))
        editor.screen.blit(sprite, rect)
    elif mob["pattern"] == "horizontal": # SLIME ORANGE (fallback)
        pygame.draw.ellipse(editor.screen, (255, 140, 0), (cx-15, cy-10, 30, 25))
    elif mob["pattern"] == "vertical": # SPECTRE VIOLET
        pygame.draw.polygon(editor.screen, (150, 0, 200), [(cx, cy-18), (cx-15, cy+10), (cx+15, cy+10)])
        pygame.draw.circle(editor.screen, (0, 0, 0), (cx, cy), 4) # Noyau
    elif mob["pattern"] == "chaser": # OEIL VOLANT
        pygame.draw.circle(editor.screen, (200, 200, 0), (cx, cy), 16)
        pygame.draw.circle(editor.screen, (255, 255, 255), (cx, cy), 10)
        pygame.draw.circle(editor.screen, (255, 0, 0), (cx, cy), 5) # Pupille
    else: # TOURELLE SHOOTER
        pygame.draw.rect(editor.screen, (0, 180, 100), (cx-12, cy-12, 24, 24), border_radius=4)
        pygame.draw.rect(editor.screen, (200, 255, 200), (cx-4, cy-4, 8, 8)) # Canon

    if editor.show_save_panel:
        draw_save_panel(editor)
    if editor.show_confirm_save:
        draw_confirm_save(editor)
    if editor.show_delete_panel:
        draw_delete_confirm(editor)
    if editor.mob_editor.visible:
        editor.mob_editor.draw(editor.screen, editor.fonts)

def draw_sidebar(editor):
    """Dessine la barre latérale avec la liste des niveaux."""
    pygame.draw.rect(editor.screen, (20, 20, 40), editor.sidebar_rect)
    pygame.draw.line(editor.screen, (60, 60, 100), (editor.sidebar_width, 0), (editor.sidebar_width, WINDOW_HEIGHT), 2)
    
    title = editor.fonts.get('small').render("NIVEAUX SAUVEGARDÉS", True, COLORS["white"])
    editor.screen.blit(title, (20, 20))
    
    # Clipping area pour les niveaux
    list_rect = pygame.Rect(0, 70, editor.sidebar_width, WINDOW_HEIGHT - 70)
    
    # Création d'une surface pour le défilement
    items_total_h = len(editor.loadable_levels) * editor.sidebar_item_h
    items_surf = pygame.Surface((editor.sidebar_width, max(list_rect.height, items_total_h)), pygame.SRCALPHA)
    
    mouse_pos = pygame.mouse.get_pos()
    
    for i, lvl in enumerate(editor.loadable_levels):
        ry = i * editor.sidebar_item_h
        item_rect = pygame.Rect(10, ry, editor.sidebar_width - 20, editor.sidebar_item_h - 10)
        
        # Effet hover
        is_hover = item_rect.collidepoint(mouse_pos[0], mouse_pos[1] + editor.sidebar_scroll_y - list_rect.y)
        bg_col = (60, 60, 90) if is_hover else (40, 40, 60)
        if str(lvl['id']) == editor.level_id_str:
            bg_col = (0, 100, 150) # Highlight niveau actuel
            
        pygame.draw.rect(items_surf, bg_col, item_rect, border_radius=5)
        
        txt = f"#{lvl['id']} - {lvl['name']}"
        surf = editor.fonts.get('small').render(txt, True, COLORS["white"])
        items_surf.blit(surf, (item_rect.x + 10, item_rect.y + 10))
        
        hint = editor.fonts.get('controls').render("Clic G: Charger | Clic D: Supprimer", True, (150, 150, 150))
        items_surf.blit(hint, (item_rect.x + 10, item_rect.y + 35))

    # Affichage de la portion visible
    editor.screen.blit(items_surf, (0, list_rect.y), area=pygame.Rect(0, editor.sidebar_scroll_y, list_rect.width, list_rect.height))

    # Barre de défilement (Scrollbar)
    if items_total_h > list_rect.height:
        ratio = list_rect.height / items_total_h
        handle_h = max(30, list_rect.height * ratio)
        handle_y = list_rect.y + (editor.sidebar_scroll_y / (items_total_h - list_rect.height)) * (list_rect.height - handle_h)
        pygame.draw.rect(editor.screen, (100, 100, 100), (editor.sidebar_width - 8, handle_y, 6, handle_h), border_radius=3)

def draw_delete_confirm(editor):
    """Panel de confirmation de suppression."""
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    editor.screen.blit(overlay, (0, 0))
    
    pygame.draw.rect(editor.screen, (40, 10, 10), editor.delete_panel_rect, border_radius=10)
    pygame.draw.rect(editor.screen, (255, 0, 0), editor.delete_panel_rect, 2, border_radius=10)
    
    title = editor.fonts.get('medium').render("SUPPRIMER LE NIVEAU ?", True, (255, 100, 100))
    editor.screen.blit(title, (editor.delete_panel_rect.centerx - title.get_width()//2, editor.delete_panel_rect.y + 40))
    
    msg = f"ID: {editor.level_to_delete['id']} - {editor.level_to_delete['name']}"
    surf = editor.fonts.get('small').render(msg, True, COLORS["white"])
    editor.screen.blit(surf, (editor.delete_panel_rect.centerx - surf.get_width()//2, editor.delete_panel_rect.y + 110))

    # Boutons
    pygame.draw.rect(editor.screen, (150, 0, 0), editor.confirm_delete_rect, border_radius=5)
    pygame.draw.rect(editor.screen, (80, 80, 80), editor.cancel_delete_rect, border_radius=5)
    
    txt_c = editor.fonts.get('small').render("SUPPRIMER", True, COLORS["white"])
    editor.screen.blit(txt_c, (editor.confirm_delete_rect.centerx - txt_c.get_width()//2, editor.confirm_delete_rect.centery - txt_c.get_height()//2))
    
    txt_a = editor.fonts.get('small').render("ANNULER", True, COLORS["white"])
    editor.screen.blit(txt_a, (editor.cancel_delete_rect.centerx - txt_a.get_width()//2, editor.cancel_delete_rect.centery - txt_a.get_height()//2))

def draw_save_panel(editor):
    """Affiche le panel de sauvegarde."""
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    editor.screen.blit(overlay, (0, 0))

    pygame.draw.rect(editor.screen, (30, 30, 50), editor.save_panel_rect, border_radius=10)
    pygame.draw.rect(editor.screen, COLORS["player"], editor.save_panel_rect, 2, border_radius=10)
    
    title = editor.fonts.get('medium').render("SAUVEGARDER LE NIVEAU", True, COLORS["white"])
    editor.screen.blit(title, (editor.save_panel_rect.centerx - title.get_width()//2, editor.save_panel_rect.y + 15))

    lbl_id = editor.fonts.get('small').render("ID (ex: 105) :", True, COLORS["white"])
    editor.screen.blit(lbl_id, (editor.save_id_rect.x, editor.save_id_rect.y - 35))
    pygame.draw.rect(editor.screen, (50, 50, 70), editor.save_id_rect, border_radius=5)
    border_id = COLORS["player"] if editor.save_focus == "id" else COLORS["white"]
    pygame.draw.rect(editor.screen, border_id, editor.save_id_rect, 2, border_radius=5)
    txt_id = editor.fonts.get('medium').render(editor.level_id_str + ("|" if editor.save_focus == "id" else ""), True, COLORS["white"])
    editor.screen.blit(txt_id, (editor.save_id_rect.x + 10, editor.save_id_rect.y + 5))

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

    pygame.draw.rect(editor.screen, (0, 150, 0), editor.confirm_save_rect, border_radius=5)
    txt_v = editor.fonts.get('small').render("VALIDER", True, COLORS["white"])
    editor.screen.blit(txt_v, (editor.confirm_save_rect.centerx - txt_v.get_width()//2, editor.confirm_save_rect.centery - txt_v.get_height()//2))

    pygame.draw.rect(editor.screen, (150, 0, 0), editor.cancel_save_rect, border_radius=5)
    txt_a = editor.fonts.get('small').render("ANNULER", True, COLORS["white"])
    editor.screen.blit(txt_a, (editor.cancel_save_rect.centerx - txt_a.get_width()//2, editor.cancel_save_rect.centery - txt_a.get_height()//2))

    side_x = editor.save_panel_rect.right - 250
    title_list = editor.fonts.get('controls').render("Noms déjà pris :", True, (150, 150, 150))
    editor.screen.blit(title_list, (side_x, editor.save_panel_rect.y + 100))
    for i, name in enumerate(editor.used_names[:8]):
        txt = editor.fonts.get('controls').render(f"- {name}", True, (120, 120, 120))
        editor.screen.blit(txt, (side_x, editor.save_panel_rect.y + 130 + i * 25))

def draw_confirm_save(editor):
    """Affiche une petite boîte de dialogue de confirmation par-dessus tout."""
    # Overlay léger
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 100))
    editor.screen.blit(overlay, (0, 0))
    
    r = editor.confirm_panel_rect
    pygame.draw.rect(editor.screen, (40, 40, 70), r, border_radius=10)
    pygame.draw.rect(editor.screen, (255, 200, 0), r, 3, border_radius=10)
    
    txt = editor.fonts.get('small').render("ID EXISTANT : ÉCRASER LE NIVEAU ?", True, (255, 255, 255))
    editor.screen.blit(txt, (r.centerx - txt.get_width()//2, r.y + 40))
    
    # Aide visuelle pour les boutons
    yes_txt = editor.fonts.get('medium').render("OUI (Entrée)", True, (0, 255, 100))
    no_txt = editor.fonts.get('medium').render("NON (Echap)", True, (255, 80, 80))
    
    editor.screen.blit(yes_txt, (r.x + 80, r.y + 110))
    editor.screen.blit(no_txt, (r.x + 280, r.y + 110))
