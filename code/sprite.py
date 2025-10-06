from constants import *

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups = None):
        super().__init__(groups)
        self.image = surf

        self.rect = self.image.get_frect(topleft=pos)
        self.prev_rect = self.rect.copy()

class Hitbox(Sprite):
    def __init__(self, pos, direction, data, groups = None, colour = 'red'):
        surf = pygame.Surface(data['size'])
        surf.fill(colour)

        pos = (pos[0] + data['rel_pos'][0] * direction, pos[1] + data['rel_pos'][1])
        super().__init__(pos, surf, groups)

        self.rect = self.image.get_frect(center=pos)
        self.prev_rect = self.rect.copy()

        self.damage = data['damage']
        self.knockback = data['knockback']
        self.stun = data['stun']