import os, sys
import time, math, random

import pygame
from pygame.math import Vector2 as vector

# general
abs_path = os.path.join(os.path.split(os.path.abspath(__file__))[0], '..')

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
SCALE_FACTOR = 3
GAME_WIDTH, GAME_HEIGHT = WINDOW_WIDTH / SCALE_FACTOR, WINDOW_HEIGHT / SCALE_FACTOR
TILE_SIZE = 16

MASTER_DISPLAY = pygame.surface.Surface((GAME_WIDTH, GAME_HEIGHT))

# game
FPS = 60

GRAVITY = 40