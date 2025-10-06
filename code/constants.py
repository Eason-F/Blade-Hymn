import os, sys
import math, random

import pygame
from pygame.math import Vector2 as vector

# general
abs_path = os.path.join(os.path.split(os.path.abspath(__file__))[0], '..')

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
SCALE_FACTOR = 3
GAME_WIDTH, GAME_HEIGHT = WINDOW_WIDTH / SCALE_FACTOR, WINDOW_HEIGHT / SCALE_FACTOR

MASTER_DISPLAY = pygame.surface.Surface((GAME_WIDTH, GAME_HEIGHT))

# game
FPS = 60
ANIMATION_SPEED = 10
TILE_SIZE = 16

GRAVITY = 800