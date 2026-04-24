# -*- coding: utf-8 -*-
from enum import IntEnum


class GameState(IntEnum):
    LOGIN = 0
    MENU = 1
    PLAYING = 2
    WIN = 3
    LEVEL_SELECT = 4
    STATS = 5
    GAME_OVER = 6


EXIT_X, EXIT_Y = 15, 13
