from constants import *
from timer import Timer

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups = None):
        super().__init__(groups)
        self.image = surf

        self.rect = self.image.get_frect(topleft=pos)
        self.prev_rect = self.rect.copy()

class AnimatedSprite(Sprite):
    def __init__(self, pos, frames, groups = None):
        super().__init__(pos, frames[0], groups)
        self.frames = frames
        self.frame_index = 0

        self.image = self.frames[int(self.frame_index) % len(self.frames)]

    def update(self, dt):
        self.prev_rect = self.rect.copy()
        self.frame_index += dt * ANIMATION_SPEED
        self.image = self.frames[int(self.frame_index) % len(self.frames)]

class Hitbox(Sprite):
    def __init__(self, tag, pos, direction, data, groups = None, colour = 'red'):
        surf = pygame.Surface(data['size'])
        surf.fill(colour)

        pos = (pos[0] + data['rel_pos'][0] * direction, pos[1] + data['rel_pos'][1])
        super().__init__(pos, surf, groups)

        self.rect = self.image.get_frect(center=pos)
        self.prev_rect = self.rect.copy()

        self.tag = tag
        self.direction = direction
        self.damage = data['damage']
        self.knockback = data['knockback']
        self.stun = data['stun']

        self.visible = False
        self.sustained = False

class Projectile(Hitbox):
    def __init__(self, tag, pos, direction, data, image, collision_rects, groups = None):
        super().__init__(tag, pos, direction, data, groups)
        self.image = image if self.direction > 0 else pygame.transform.flip(image, True, False)
        self.rect = self.image.get_frect(center = pos)
        self.prev_rect = self.rect.copy()

        self.visible = True
        self.sustained = True

        self.data = data
        self.velocity = vector(data['velocity'][0] * direction, data['velocity'][1])

        self.collision_rects = collision_rects
        self.timer = Timer(1000, sustained = True)
        self.timer.activate()

        self.hitbox = None

    def update(self, dt):
        self.hitbox = Hitbox(
            tag = 'enemy',
            pos = self.rect.center,
            direction = self.direction,
            data = self.data,
            groups = self.groups(),
            colour = 'blue'
        )

        self.timer.update()
        if self.hitbox.rect.collidelist(self.collision_rects) >= 0:
            self.timer.deactivate()

        if self.timer.active:
            self.prev_rect = self.rect.copy()
            self.rect.x += self.velocity.x * dt
            self.rect.y += self.velocity.y * dt
        else:
            self.kill()