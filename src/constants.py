# -*- coding: utf-8 -*-
from enum import IntEnum


class GameState(IntEnum):
    SPLASH = -1
    LOGIN = 0
    MENU = 1
    PLAYING = 2
    WIN = 3
    LEVEL_SELECT = 4
    STATS = 5
    GAME_OVER = 6
    EDITOR = 7
    OPTIONS = 8
    IA_TEST = 9


EXIT_X, EXIT_Y = 15, 13
