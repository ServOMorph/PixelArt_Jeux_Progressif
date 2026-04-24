# -*- coding: utf-8 -*-
"""
Main entry point for the Pixel Art Maze Game.
Initializes the game engine and starts the main loop.
"""
from src.game import Game

if __name__ == "__main__":
    game = Game()
    game.run()
