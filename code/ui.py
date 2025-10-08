from constants import *
from sprite import Sprite, AnimatedSprite

class HealthBar(Sprite):
    def __init__(self, pos, max_hp, groups, frames):
        super().__init__(pos, frames["health"][0], groups)
        self.rect.midleft = pos
        self.max_hp = max_hp
        self.frames = frames["health"]

        self.sustained = True
        self.visible = True

    def update(self, **kwargs):
        hp = kwargs.get('hp', 0)
        scale = (hp if hp > 0 else 0) / self.max_hp
        scaled_width = self.rect.width * scale
        scaled_bar = pygame.transform.scale(self.frames[1], (scaled_width, self.rect.height))

        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.image.blit(self.frames[2], (0, 0))
        self.image.blit(scaled_bar, (0, 0))
        self.image.blit(self.frames[0], (0, 0))

        self.rect = self.image.get_frect(midleft=self.rect.midleft)
        self.prev_rect = self.rect.copy()

class CounterToken(Sprite):
    def __init__(self, pos, index, surf, max_count, groups):
        super().__init__(pos, surf[0], groups)
        self.padding = 2
        self.rect = self.image.get_frect(midleft=(
            pos[0] + index * (self.rect.width + self.padding),
            pos[1]
        ))

        self.max_count = max_count
        self.sustained = False

        self.visible = True

class Counter(AnimatedSprite):
    def __init__(self, pos, animation, frame, max_count, groups):
        super().__init__(pos, frame, groups)
        self.rect.midleft = (pos[0], pos[1] - 6)
        self.max_count = max_count
        self.cover = frame[0]
        self.frames = animation

        self.sustained = True
        self.visible = True

    def update(self, **kwargs):
        count = kwargs.get('count', 0)
        dt = kwargs.get('dt', 0)

        multiplier = (count if count > 0 else 0) / self.max_count
        y_offset = (self.rect.height - 48) * (1 - multiplier)

        self.frame_index += ANIMATION_SPEED * dt

        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.image.blit(self.frames[int(self.frame_index) % len(self.frames)], (0, y_offset))
        self.image.blit(self.cover, (0, 0))
        self.image.set_colorkey('black')

        self.rect = self.image.get_frect(midleft=self.rect.midleft)
        self.prev_rect = self.rect.copy()

