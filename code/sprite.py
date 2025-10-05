from constants import *

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups = None):
        super().__init__(groups)
        self.image = surf

        self.rect = self.image.get_frect(topleft=pos)
        self.prev_rect = self.rect.copy()

class Hitbox(Sprite):
    def __init__(self, pos, rel_pos, size, direction, damage, groups = None, colour = 'red'):
        surf = pygame.Surface(size)
        surf.fill(colour)

        pos = (pos[0] + rel_pos[0] * direction, pos[1] + rel_pos[1])
        super().__init__(pos, surf, groups)

        self.rect = self.image.get_frect(center=pos)
        self.prev_rect = self.rect.copy()

        self.damage = damage
