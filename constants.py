# -*- coding: utf-8 -*-
from enum import IntEnum


class GameState(IntEnum):
    MENU = 0
    PLAYING = 1
    WIN = 2


EXIT_X, EXIT_Y = 15, 13
