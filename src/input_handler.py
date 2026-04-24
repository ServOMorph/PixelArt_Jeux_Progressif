# -*- coding: utf-8 -*-
import pygame
from src.constants import GameState


class InputHandler:
    """Gere les entrees utilisateur."""

    def handle_events(self, game_state, pseudo="", ui_renderer=None):
        """Gere les evenements clavier et souris.

        Retourne (running, new_state, updated_pseudo)
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, game_state, pseudo

            if event.type == pygame.MOUSEBUTTONDOWN and ui_renderer:
                mx, my = pygame.mouse.get_pos()
                
                if game_state == GameState.MENU:
                    for action, rect in ui_renderer.click_areas.items():
                        if rect.collidepoint(mx, my):
                            if action == "PLAY": return True, GameState.PLAYING, pseudo
                            if action == "LEVEL_SELECT": return True, GameState.LEVEL_SELECT, pseudo
                            if action == "STATS": return True, GameState.STATS, pseudo
                            if action == "EDITOR": return True, GameState.EDITOR, pseudo
                            if action == "QUIT": return False, game_state, pseudo

                elif game_state == GameState.LEVEL_SELECT:
                    for action, rect in ui_renderer.click_areas.items():
                        if rect.collidepoint(mx, my):
                            if action.startswith("LEVEL_"):
                                level_id = int(action.split("_")[1])
                                return True, ("START_LEVEL", level_id), pseudo
                            if action == "BACK": return True, GameState.MENU, pseudo

                elif game_state == GameState.WIN:
                    for action, rect in ui_renderer.click_areas.items():
                        if rect.collidepoint(mx, my):
                            if action == "NEXT": return True, GameState.MENU, pseudo # Logic handles next level in game.py
                            if action == "MENU": return True, GameState.MENU, pseudo
                            if action == "QUIT": return False, game_state, pseudo

            if event.type == pygame.KEYDOWN:
                if game_state == GameState.LOGIN:
                    if event.key == pygame.K_RETURN and len(pseudo) > 0:
                        return True, GameState.MENU, pseudo
                    elif event.key == pygame.K_BACKSPACE:
                        pseudo = pseudo[:-1]
                    elif len(pseudo) < 15 and event.unicode.isalnum():
                        pseudo += event.unicode
                    return True, GameState.LOGIN, pseudo

                if event.key == pygame.K_ESCAPE:
                    if game_state == GameState.PLAYING:
                        return True, GameState.MENU, pseudo
                    if game_state == GameState.EDITOR: # handled in editor but backup
                        return True, GameState.MENU, pseudo
                    return False, game_state, pseudo

                if game_state == GameState.MENU:
                    if event.key == pygame.K_1:
                        return True, GameState.PLAYING, pseudo
                    elif event.key == pygame.K_2:
                        return True, GameState.LEVEL_SELECT, pseudo
                    elif event.key == pygame.K_3:
                        return True, GameState.STATS, pseudo
                    elif event.key == pygame.K_4:
                        return True, GameState.EDITOR, pseudo
                    elif event.key == pygame.K_q:
                        return False, game_state, pseudo

                elif game_state == GameState.LEVEL_SELECT:
                    if pygame.K_1 <= event.key <= pygame.K_9:
                        level_id = event.key - pygame.K_0
                        return True, ("START_LEVEL", level_id), pseudo
                    elif event.key == pygame.K_ESCAPE:
                        return True, GameState.MENU, pseudo

                elif game_state == GameState.STATS:
                    return True, GameState.MENU, pseudo

                elif game_state == GameState.WIN:
                    if event.key == pygame.K_SPACE:
                        return True, GameState.MENU, pseudo
                    elif event.key == pygame.K_q:
                        return False, game_state, pseudo

        return True, game_state, pseudo

    def handle_continuous_input(self, player):
        """Gere le mouvement continu du joueur."""
        keys = pygame.key.get_pressed()

        if keys[pygame.K_z]:
            player.move(0, -1)
        if keys[pygame.K_s]:
            player.move(0, 1)
        if keys[pygame.K_q]:
            player.move(-1, 0)
        if keys[pygame.K_d]:
            player.move(1, 0)
