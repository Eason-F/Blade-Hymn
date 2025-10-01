from constants import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.image = pygame.Surface((20, 28))
        self.image.fill('red')

        self.rect = self.image.get_frect(topleft=pos)
        self.prev_rect = self.rect.copy()

        # movement
        self.direction = vector(0, 0)
        self.speed = 200

        # collisions
        self.collision_sprites = collision_sprites

    def input(self):
        keys = pygame.key.get_pressed()
        movement_vect = vector(0,0)
        if keys[pygame.K_LEFT]:
            movement_vect.x -= 1
        if keys[pygame.K_RIGHT]:
            movement_vect.x += 1

        self.direction = movement_vect.normalize() if movement_vect else movement_vect

    def move(self, dt):
        self.rect.x += self.direction.x * self.speed * dt
        self.collision('x')

        self.rect.y += self.direction.y * self.speed * dt
        self.collision('y')

    def collision(self, axis):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.rect):
                if axis == 'x': # horizontal
                    if self.rect.left <= sprite.rect.right and self.prev_rect.left >= sprite.prev_rect.right: # left
                        self.rect.left = sprite.rect.right

                    if self.rect.right >= sprite.rect.left and self.prev_rect.right <= sprite.prev_rect.left: # right
                        self.rect.right = sprite.rect.left
                else: # vertical
                    pass

    def update(self, dt):
        self.prev_rect = self.rect.copy()
        self.input()
        self.move(dt)