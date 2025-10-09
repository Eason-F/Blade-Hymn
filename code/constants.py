import os, sys
import math, random

import pygame
from pygame.math import Vector2 as vector

# general
abs_path = os.path.join(os.path.split(os.path.abspath(__file__))[0], '..')

SCALE_FACTOR = 3
GAME_WIDTH, GAME_HEIGHT = 1280/3, 720/3
WINDOW_WIDTH, WINDOW_HEIGHT = GAME_WIDTH * SCALE_FACTOR, GAME_HEIGHT * SCALE_FACTOR

MASTER_DISPLAY = pygame.surface.Surface((GAME_WIDTH, GAME_HEIGHT))

# game
FPS = 60
ANIMATION_SPEED = 10
TILE_SIZE = 16

GRAVITY = 800
PlAYER_HEALTH = 70

BG_FILL = {
    "spring": "#112218",
    "desert": "#0F0F2B",
    "winter": "#160804"
}

Z_VALUES = {
    'bg': -1,
    'ground': 1,
    'fg': 2,
    'enemies': 3,
    'player': 4,
    'ui': 99
}