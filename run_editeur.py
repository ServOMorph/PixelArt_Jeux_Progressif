# -*- coding: utf-8 -*-
"""
Standalone launcher for the Level Editor.
Starts the game directly in editor mode to enable all features like Test mode and Stats.
"""
from src.game import Game
from src.constants import GameState

def run_standalone_editor():
    """Lance le jeu directement en mode éditeur avec toutes les fonctionnalités."""
    game = Game()
    game.state = GameState.EDITOR
    game.run()

if __name__ == "__main__":
    run_standalone_editor()
