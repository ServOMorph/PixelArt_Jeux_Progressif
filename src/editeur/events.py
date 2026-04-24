# -*- coding: utf-8 -*-
import pygame

def handle_editor_events(editor):
    """Gere les clics et touches dans l'editeur."""
    if editor.save_message_timer > 0:
        editor.save_message_timer -= 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return "QUIT"
        
        if event.type == pygame.KEYDOWN:
            # Saisie dans le Save Panel (Modal)
            if editor.show_save_panel:
                if event.key == pygame.K_RETURN:
                    if editor.save_focus == "id":
                        editor.save_focus = "name" # Passer au nom si on tape entrée dans l'ID
                    else:
                        editor.save_level()
                        editor.show_save_panel = False
                elif event.key == pygame.K_BACKSPACE:
                    if editor.save_focus == "id":
                        editor.level_id_str = editor.level_id_str[:-1]
                    else:
                        editor.level_name = editor.level_name[:-1]
                elif event.key == pygame.K_TAB: # Alterner focus
                    editor.save_focus = "name" if editor.save_focus == "id" else "id"
                elif event.key == pygame.K_ESCAPE:
                    editor.show_save_panel = False
                else:
                    if editor.save_focus == "id" and event.unicode.isdigit():
                        editor.level_id_str += event.unicode
                    elif editor.save_focus == "name":
                        editor.level_name += event.unicode
                return "EDITOR"

            # Saisie ID (Global/Top Bar)
            if editor.is_typing_id:
                if event.key == pygame.K_RETURN: editor.is_typing_id = False
                elif event.key == pygame.K_BACKSPACE:
                    editor.level_id_str = editor.level_id_str[:-1]
                elif event.unicode.isdigit():
                    editor.level_id_str += event.unicode
                return "EDITOR"

            # Shortcuts Généraux
            if event.key == pygame.K_ESCAPE:
                if editor.show_load_panel: editor.show_load_panel = False
                else: return "MENU"
            
            if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                _open_save_modal(editor)

            # Undo / Redo
            if (pygame.key.get_mods() & pygame.KMOD_CTRL):
                if event.key == pygame.K_z: editor.undo()
                if event.key == pygame.K_y: editor.redo()
            
            # Raccourcis outils
            shortcuts = {pygame.K_1: "WALL", pygame.K_2: "PATH", pygame.K_3: "START", 
                         pygame.K_4: "EXIT", pygame.K_5: "MOB_H", pygame.K_6: "MOB_V"}
            if event.key in shortcuts:
                editor.current_tool = shortcuts[event.key]

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            
            # Si le panel de sauvegarde est ouvert
            if editor.show_save_panel:
                if editor.confirm_save_rect.collidepoint(mx, my):
                    editor.save_level()
                    editor.show_save_panel = False
                elif editor.cancel_save_rect.collidepoint(mx, my):
                    editor.show_save_panel = False
                elif editor.save_id_rect.collidepoint(mx, my):
                    editor.save_focus = "id"
                elif editor.save_name_rect.collidepoint(mx, my):
                    editor.save_focus = "name"
                return "EDITOR"

            # Si le panel de chargement est ouvert
            if editor.show_load_panel:
                if not editor.load_panel_rect.collidepoint(mx, my):
                    editor.show_load_panel = False
                else:
                    header_h = 60
                    item_h = 50
                    for i, lvl in enumerate(editor.loadable_levels):
                        item_rect = pygame.Rect(editor.load_panel_rect.x + 20, editor.load_panel_rect.y + header_h + i * item_h, 560, 40)
                        if item_rect.collidepoint(mx, my):
                            editor.load_level_data(lvl)
                            editor.show_load_panel = False
                return "EDITOR"

            # Clic sur les inputs
            editor.is_typing_id = editor.id_input_rect.collidepoint(mx, my)

            # Boutons
            if editor.save_rect.collidepoint(mx, my): 
                _open_save_modal(editor)
            if editor.load_rect.collidepoint(mx, my): editor.open_load_panel()
            if editor.exit_editor_rect.collidepoint(mx, my): return "MENU"
            if editor.clear_rect.collidepoint(mx, my):
                editor.save_snapshot()
                editor.maze = [[0 for _ in range(editor.grid_w)] for _ in range(editor.grid_h)]
                editor._add_borders()
                editor.mobs = []

            # Palette
            for i, tool in enumerate(editor.tools):
                if editor._get_tool_rect(i).collidepoint(mx, my):
                    editor.current_tool = tool

        # Dessin continu sur la grille
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0] or mouse_pressed[2]: # Clic Gauche ou Droit
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
    editor.level_id_str = "" # Vide
    editor.level_name = ""   # Vide
    editor.save_focus = "id" # Focus sur l'ID au début
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

    if editor.current_tool == "WALL":
        editor.maze[y][x] = 1
    elif editor.current_tool == "PATH":
        editor.maze[y][x] = 0
        editor.mobs = [m for m in editor.mobs if m["start_pos"] != [x, y]]
    elif editor.current_tool == "START":
        editor.maze[y][x] = 0
        editor.start_pos = [x, y]
    elif editor.current_tool == "EXIT":
        editor.maze[y][x] = 0
        editor.exit_pos = [x, y]
    elif editor.current_tool.startswith("MOB"):
        editor.maze[y][x] = 0
        pattern = "horizontal" if editor.current_tool == "MOB_H" else "vertical"
        editor.mobs = [m for m in editor.mobs if m["start_pos"] != [x, y]]
        editor.mobs.append({
            "type": "Mob1", 
            "start_pos": [x, y], 
            "pattern": pattern, 
            "distance": 4, 
            "speed": 0.08
        })
