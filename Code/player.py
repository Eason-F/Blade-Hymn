from constants import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.image = pygame.image.load(os.path.join(abs_path, "Assets", "Graphics", "player", "player.png")).convert_alpha()

        # hitbox_rect
        self.rect = self.image.get_frect(topleft=pos)
        self.hitbox_rect = self.rect.inflate(-72, -32)
        self.prev_rect = self.hitbox_rect.copy()

        self.camera_rect = self.hitbox_rect.copy()

        # movement
        self.gravity = GRAVITY
        self.friction = 10
        self.velocity = vector(0, 0)
        self.speed = 25

        self.is_jumping = False
        self.jump_height = 12

        self.dash_distance = 25
        self.dash_cooldown_length = 0.75
        self.dash_cooldown = 0
        self.max_dash_count = 2
        self.dash_count = self.max_dash_count

        # collisions
        self.collision_sprites = collision_sprites

        self.colliding = {
            "ground": False,
            "hitbox": False
        }

    def input(self):
        keys = pygame.key.get_pressed()
        movement_vect = vector(0, 0)

        if keys[pygame.K_LEFT]:
            movement_vect.x -= 1
        if keys[pygame.K_RIGHT]:
            movement_vect.x += 1

        if keys[pygame.K_LSHIFT]:
            movement_vect.x = self.dash(movement_vect.x)
        self.velocity.x += movement_vect.x

        if keys[pygame.K_SPACE]:
            if self.colliding["ground"]:
                self.is_jumping = True

    def move(self, dt):
        self.dash_cooldown -= dt

        self.velocity.x *= 0.85
        self.hitbox_rect.x += self.velocity.x * self.speed * dt
        self.collision('x')

        self.velocity.y += (self.gravity / 2) * dt
        self.hitbox_rect.y += self.velocity.y
        self.velocity.y += (self.gravity / 2) * dt
        self.collision('y')

        if self.is_jumping:
            self.velocity.y = -self.jump_height
            self.hitbox_rect.bottom += 1
            self.is_jumping = False

        self.rect.center = self.hitbox_rect.center
        self.move_camera()

    def dash(self, speed):
        if self.dash_cooldown <= 0:
            self.dash_count = self.max_dash_count

        if self.dash_cooldown <= self.dash_cooldown_length / 1.5 and self.dash_count > 0:
            dash_direction = self.velocity.x / abs(self.velocity.x) if abs(self.velocity.x) else 1
            speed = self.dash_distance * dash_direction
            self.dash_cooldown = self.dash_cooldown_length
            self.dash_count -= 1
        return speed

    def check_collisions(self):
        ground_rect = pygame.Rect(self.hitbox_rect.bottomleft, (self.hitbox_rect.width, 2))
        collide_rects = [sprite.rect for sprite in self.collision_sprites]

        self.colliding["ground"] = True if ground_rect.collidelist(collide_rects) >= 0 else False

    def collision(self, axis):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if axis == 'x': # horizontal
                    if self.hitbox_rect.left <= sprite.rect.right:
                        if int(self.prev_rect.left) >= int(sprite.prev_rect.right): # left
                            self.hitbox_rect.left = sprite.rect.right

                    if self.hitbox_rect.right >= sprite.rect.left:
                        if int(self.prev_rect.right) <= int(sprite.prev_rect.left): # right
                            self.hitbox_rect.right = sprite.rect.left
                else: # vertical
                    if self.hitbox_rect.top <= sprite.rect.bottom:
                        if int(self.prev_rect.top) >= int(sprite.prev_rect.bottom):  # up
                            self.hitbox_rect.top = sprite.rect.bottom

                    if self.hitbox_rect.bottom >= sprite.rect.top:
                        if int(self.prev_rect.bottom) <= int(sprite.prev_rect.top):  # down
                            self.hitbox_rect.bottom = sprite.rect.top
                    self.velocity.y = 0

    def move_camera(self):
        camera_speed = math.dist(self.hitbox_rect.center, self.camera_rect.center) / 500
        self.camera_rect.x += (self.hitbox_rect.x - self.camera_rect.x) * camera_speed
        self.camera_rect.y += (self.hitbox_rect.y - self.camera_rect.y) * camera_speed

    def update(self, dt):
        self.prev_rect = self.hitbox_rect.copy()
        self.check_collisions()
        self.input()
        self.move(dt)

# in combat jumping is disabled ie. combat lock
# 2 consecutive dashes before cooldown