import os, sys
import time, math, random

import pygame
from pygame.math import Vector2 as vector

abs_path = os.path.join(os.path.split(os.path.abspath(__file__))[0], '..')

GAME_WIDTH, GAME_HEIGHT = 640, 360
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
SCALE_FACTOR = 2
TILE_SIZE = 16

MASTER_DISPLAY = pygame.surface.Surface((GAME_WIDTH, GAME_HEIGHT))