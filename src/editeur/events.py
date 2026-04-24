# -*- coding: utf-8 -*-
import pygame

def handle_editor_events(editor):
    """Gere les clics et touches dans l'editeur."""
    if editor.save_message_timer > 0:
        editor.save_message_timer -= 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return "QUIT"
        
        # Défilement Sidebar
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4: # Scroll Up
                editor.sidebar_scroll_y = max(0, editor.sidebar_scroll_y - 40)
            elif event.button == 5: # Scroll Down
                editor.sidebar_scroll_y = min(editor.max_sidebar_scroll, editor.sidebar_scroll_y + 40)

        if event.type == pygame.KEYDOWN:
            # Saisie dans le Save Panel (Modal)
            if editor.show_save_panel:
                if event.key == pygame.K_RETURN:
                    if editor.save_focus == "id": editor.save_focus = "name"
                    else:
                        editor.save_level()
                        editor.show_save_panel = False
                elif event.key == pygame.K_BACKSPACE:
                    if editor.save_focus == "id": editor.level_id_str = editor.level_id_str[:-1]
                    else: editor.level_name = editor.level_name[:-1]
                elif event.key == pygame.K_TAB: editor.save_focus = "name" if editor.save_focus == "id" else "id"
                elif event.key == pygame.K_ESCAPE: editor.show_save_panel = False
                else:
                    if editor.save_focus == "id" and event.unicode.isdigit(): editor.level_id_str += event.unicode
                    elif editor.save_focus == "name": editor.level_name += event.unicode
                return "EDITOR"

            # Confirmation Suppression
            if editor.show_delete_panel:
                if event.key == pygame.K_ESCAPE: editor.show_delete_panel = False
                return "EDITOR"

            # Saisie ID (Global/Top Bar)
            if editor.is_typing_id:
                if event.key == pygame.K_RETURN: editor.is_typing_id = False
                elif event.key == pygame.K_BACKSPACE: editor.level_id_str = editor.level_id_str[:-1]
                elif event.unicode.isdigit(): editor.level_id_str += event.unicode
                return "EDITOR"

            # Shortcuts Généraux
            if event.key == pygame.K_ESCAPE: return "MENU"
            
            if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                _open_save_modal(editor)

            # Undo / Redo
            if (pygame.key.get_mods() & pygame.KMOD_CTRL):
                if event.key == pygame.K_z: editor.undo()
                if event.key == pygame.K_y: editor.redo()
            
            # Raccourcis outils
            shortcuts = {pygame.K_1: "WALL", pygame.K_2: "PATH", pygame.K_3: "START", 
                         pygame.K_4: "EXIT", pygame.K_5: "TREE", pygame.K_6: "1 Horizon", 
                         pygame.K_7: "2 Verti", pygame.K_8: "3 Trackeur", pygame.K_9: "4 Missile"}
            if event.key in shortcuts:
                editor.current_tool = shortcuts[event.key]

        # Priorité aux modaux
        if editor.mob_editor.visible:
            if editor.mob_editor.handle_events(event):
                return "EDITOR"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                editor.mob_editor.close()
            return "EDITOR"

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            
            # Clic sur le bouton de réglage d'un mob dans la grille
            if not editor.sidebar_rect.collidepoint(mx, my):
                gx = (mx - editor.offset_x) // editor.tile_size
                gy = (my - editor.offset_y) // editor.tile_size
                if 0 <= gx < editor.grid_w and 0 <= gy < editor.grid_h:
                    # On vérifie si un mob est ici
                    for mob in editor.mobs:
                        if mob["start_pos"] == [gx, gy]:
                            # Clic sur le petit "G"
                            rect = pygame.Rect(editor.offset_x + gx * editor.tile_size + editor.tile_size - 15, 
                                               editor.offset_y + gy * editor.tile_size + 2, 12, 12)
                            if rect.collidepoint(mx, my):
                                editor.mob_editor.open(mob)
                                return "EDITOR"

            # Confirmation Suppression
            if editor.show_delete_panel:
                if editor.confirm_delete_rect.collidepoint(mx, my):
                    editor.delete_level(editor.level_to_delete["id"])
                    editor.show_delete_panel = False
                elif editor.cancel_delete_rect.collidepoint(mx, my):
                    editor.show_delete_panel = False
                return "EDITOR"

            # Clic dans la Sidebar
            if editor.sidebar_rect.collidepoint(mx, my):
                list_y = my - 70 + editor.sidebar_scroll_y
                if list_y >= 0:
                    idx = list_y // editor.sidebar_item_h
                    if idx < len(editor.loadable_levels):
                        target_lvl = editor.loadable_levels[idx]
                        if event.button == 1: # Clic Gauche : Charger
                            editor.load_level_data(target_lvl)
                        elif event.button == 3: # Clic Droit : Supprimer
                            editor.level_to_delete = target_lvl
                            editor.show_delete_panel = True
                return "EDITOR"

            # Panel Sauvegarde
            if editor.show_save_panel:
                if editor.confirm_save_rect.collidepoint(mx, my):
                    editor.save_level()
                    editor.show_save_panel = False
                elif editor.cancel_save_rect.collidepoint(mx, my): editor.show_save_panel = False
                elif editor.save_id_rect.collidepoint(mx, my): editor.save_focus = "id"
                elif editor.save_name_rect.collidepoint(mx, my): editor.save_focus = "name"
                return "EDITOR"

            # Boutons
            if editor.save_rect.collidepoint(mx, my): _open_save_modal(editor)
            if editor.test_rect.collidepoint(mx, my): return "TEST"
            if editor.exit_editor_rect.collidepoint(mx, my): return "MENU"
            if editor.clear_rect.collidepoint(mx, my):
                editor.save_snapshot()
                editor.maze = [[0 for _ in range(editor.grid_w)] for _ in range(editor.grid_h)]
                editor._add_borders()
                editor.mobs = []

            # Palette Tuiles
            for i, tool in enumerate(editor.tile_tools):
                if editor._get_tool_rect("tile", i).collidepoint(mx, my):
                    editor.current_tool = tool

            # Palette Mobs
            for i, tool in enumerate(editor.mob_tools):
                if editor._get_tool_rect("mob", i).collidepoint(mx, my):
                    editor.current_tool = tool
            
            # Clic sur l'ID (Top Bar)
            if editor.id_input_rect.collidepoint(mx, my):
                editor.is_typing_id = True
            else:
                editor.is_typing_id = False

        # Dessin continu sur la grille
        mouse_pressed = pygame.mouse.get_pressed()
        if (mouse_pressed[0] or mouse_pressed[2]) and not editor.sidebar_rect.collidepoint(pygame.mouse.get_pos()):
            mx, my = pygame.mouse.get_pos()
            if editor.offset_x <= mx < editor.offset_x + editor.grid_w * editor.tile_size and \
               editor.offset_y <= my < editor.offset_y + editor.grid_h * editor.tile_size:
                gx = (mx - editor.offset_x) // editor.tile_size
                gy = (my - editor.offset_y) // editor.tile_size
                is_erase = mouse_pressed[2]
                apply_tool_logic(editor, gx, gy, is_erase)

    return "EDITOR"

def _open_save_modal(editor):
    """Réinitialise et ouvre le modal de sauvegarde."""
    editor.level_id_str = ""
    editor.level_name = ""
    editor.save_focus = "id"
    editor.show_save_panel = True

def apply_tool_logic(editor, x, y, erase=False):
    """Applique l'outil selectionne ou efface a la case (x, y)."""
    if erase:
        if editor.maze[y][x] == 0 and not any(m["start_pos"] == [x,y] for m in editor.mobs) and [x,y] != editor.start_pos and [x,y] != editor.exit_pos:
            return
        editor.save_snapshot()
        editor.maze[y][x] = 0
        editor.mobs = [m for m in editor.mobs if m["start_pos"] != [x, y]]
        return

    editor.save_snapshot()

    if editor.current_tool == "WALL": editor.maze[y][x] = 1
    elif editor.current_tool == "PATH":
        editor.maze[y][x] = 0
        editor.mobs = [m for m in editor.mobs if m["start_pos"] != [x, y]]
    elif editor.current_tool == "START":
        editor.maze[y][x] = 0
        editor.start_pos = [x, y]
    elif editor.current_tool == "EXIT":
        editor.maze[y][x] = 0
        editor.exit_pos = [x, y]
    elif editor.current_tool == "TREE":
        editor.maze[y][x] = 2
    elif editor.current_tool in ["1 Horizon", "2 Verti", "3 Trackeur", "4 Missile"]:
        editor.maze[y][x] = 0
        if editor.current_tool == "1 Horizon": pattern = "horizontal"
        elif editor.current_tool == "2 Verti": pattern = "vertical"
        elif editor.current_tool == "3 Trackeur": pattern = "chaser"
        else: pattern = "shooter"
        editor.mobs = [m for m in editor.mobs if m["start_pos"] != [x, y]]
        editor.mobs.append({
            "type": "Mob1", "start_pos": [x, y], "pattern": pattern, 
            "distance": 4 if pattern != "shooter" else 120, 
            "speed": 0.08 if pattern not in ["chaser", "shooter"] else 0.04
        })
