from constants import *

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups = None):
        super().__init__(groups)
        self.image = surf
        self.image.fill('white')

        self.rect = self.image.get_frect(topleft=pos)
        self.prev_rect = self.rect.copy()