from constants import *
from timer import Timer

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.image = pygame.image.load(os.path.join(abs_path, "assets", "graphics", "player", "player.png")).convert_alpha()

        # hitbox_rect
        self.rect = self.image.get_frect(topleft=pos)
        self.hitbox_rect = self.rect.inflate(-72, -32)
        self.prev_rect = self.hitbox_rect.copy()

        self.camera_rect = self.hitbox_rect.copy()

        # movement
        self.gravity = GRAVITY
        self.friction = 0.85
        self.velocity = vector(0, 0)
        self.speed = 25

        self.is_jumping = False
        self.jump_height = 6

        self.dash_distance = 25
        self.max_dash_count = 2
        self.dash_count = self.max_dash_count

        # collisions
        self.collision_sprites = collision_sprites

        self.colliding = {
            "ground": False,
            "hitbox": False
        }

        # timers
        self.timers = {
            "dash": Timer(1500, auto_start=True, repeat=True),
            "dash_cooldown": Timer(250, sustained=True),
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
        self.velocity.x *= self.friction
        self.hitbox_rect.x += self.velocity.x * self.speed * dt
        self.collision('x')

        self.velocity.y += self.gravity * dt
        self.hitbox_rect.y += self.velocity.y
        self.collision('y')

        if self.is_jumping:
            self.velocity.y = -self.jump_height
            self.hitbox_rect.bottom += 1
            self.is_jumping = False

        if self.timers["dash"].active:
            self.dash_count = self.dash_count + 1 if self.dash_count < self.max_dash_count else self.max_dash_count

        self.rect.center = self.hitbox_rect.center
        self.move_camera()

    def dash(self, speed):
        if self.dash_count > 0 and not self.timers["dash_cooldown"].active:
            dash_direction = self.velocity.x / abs(self.velocity.x) if abs(self.velocity.x) else 1
            speed = self.dash_distance * dash_direction

            self.dash_count -= 1
            self.timers["dash_cooldown"].activate()

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

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def update(self, dt):
        self.prev_rect = self.hitbox_rect.copy()
        self.update_timers()
        self.check_collisions()
        self.input()
        self.move(dt)

# in combat jumping is disabled ie. combat lock
# 2 consecutive dashes before cooldown