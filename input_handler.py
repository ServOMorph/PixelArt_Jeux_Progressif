# -*- coding: utf-8 -*-
import pygame
from constants import GameState


class InputHandler:
    """Gere les entrees utilisateur."""

    def handle_events(self, game_state):
        """Gere les evenements clavier et fermeture.

        Retourne (running, new_state)
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, game_state

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False, game_state

                if game_state == GameState.MENU:
                    if event.key == pygame.K_1:
                        return True, GameState.PLAYING
                    elif event.key == pygame.K_q:
                        return False, game_state

                elif game_state == GameState.WIN:
                    if event.key == pygame.K_SPACE:
                        return True, GameState.MENU
                    elif event.key == pygame.K_q:
                        return False, game_state

        return True, game_state

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
