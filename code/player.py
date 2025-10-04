from constants import *
from timer import Timer

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, attack_rects, enemy_rects, frames):
        super().__init__(groups)

        # animation
        self.frames, self.frame_index = frames, 0
        self.state, self.facing_right = 'idle', True
        self.image = self.frames[self.state][self.frame_index]

        # hitbox rect
        self.rect = self.image.get_frect(topleft=pos)
        self.hitbox_rect = self.rect.inflate(-72, -32)
        self.prev_rect = self.hitbox_rect.copy()

        self.camera_rect = self.hitbox_rect.copy()

        # movement
        self.gravity = GRAVITY
        self.friction = 7
        self.velocity = vector(0, 0)
        self.acceleration = 20
        self.speed = 60

        self.is_jumping = False
        self.jump_height = 300

        self.dash_distance = self.acceleration * 20
        self.max_dash_count = 2; self.dash_count = self.max_dash_count

        # attack
        self.is_attacking = self.attack_combo = False
        self.attack_stage, self.attack_stage_count = -1, 3
        self.can_air_atk = True

        # collisions
        self.collision_sprites = collision_sprites

        self.attack_rects = attack_rects
        self.enemy_rects = enemy_rects

        self.colliding = {
            "ground": False,
            "hitbox": False
        }

        # timers
        self.timers = {
            "dash": Timer(1500, auto_start=True, repeat=True),
            "dash_cooldown": Timer(250, sustained=True),
            "attack_combo": Timer(200)
        }

    def input(self, dt):
        keys = pygame.key.get_pressed()
        movement_vect = vector(0, 0)

        if not self.is_attacking:
            if keys[pygame.K_LEFT]:
                movement_vect.x -= self.acceleration
                self.facing_right = False

            if keys[pygame.K_RIGHT]:
                movement_vect.x += self.acceleration
                self.facing_right = True

            if keys[pygame.K_LSHIFT]:
                movement_vect.x = self.dash(movement_vect.x)

            if keys[pygame.K_SPACE]:
                if self.colliding["ground"]:
                    self.is_jumping = True

        self.velocity.x += movement_vect.x * dt

        if self.colliding["ground"]:
            self.can_air_atk = True

        if keys[pygame.K_x]:
            if self.colliding["ground"] or self.can_air_atk:
                self.attack()
        self.attack_update()

    # input related actions
    def dash(self, speed):
        if self.dash_count > 0 and not self.timers["dash_cooldown"].active:
            dash_direction = 1 if self.facing_right else -1
            speed = self.dash_distance * dash_direction

            self.dash_count -= 1
            self.timers["dash_cooldown"].activate()

        return speed

    def attack(self):
        if self.colliding["ground"]:
            self.attack_stage_count = 3
        else:
            self.attack_stage_count = 2

        if not self.is_attacking:
            self.attack_stage = (self.attack_stage + 1) % self.attack_stage_count
            self.frame_index = 0

        self.is_attacking = True
        self.attack_combo = True
        self.timers['attack_combo'].deactivate()

    def attack_update(self):
        if 'melee' in self.state or 'air' in self.state:
            if self.frame_index >= len(self.frames[self.state]):
                self.is_attacking = False
                self.timers['attack_combo'].activate()

                if self.attack_stage == 1 and 'air' in self.state:
                    self.can_air_atk = False
                    self.attack_combo = False

        if self.timers['attack_combo'].active:
            self.attack_combo = False
            self.attack_stage = -1

    # movement related actions
    def move(self, dt):
        friction_factor = self.friction * -self.velocity.x
        # if friction_factor * dt:
        #     print(friction_factor * dt)
        self.velocity.x += friction_factor / 2 * dt
        self.hitbox_rect.x += self.velocity.x * self.speed * dt
        self.velocity.x += friction_factor / 2 * dt
        self.collision('x')

        # if abs(self.velocity.x) < 0.1: self.velocity.x = 0

        if 'air' in self.state:
            self.velocity.y = 0
        self.velocity.y += self.gravity / 2 * dt
        self.hitbox_rect.y += self.velocity.y * dt
        self.velocity.y += self.gravity / 2 * dt
        self.collision('y')

        if self.is_jumping:
            self.velocity.y = -self.jump_height
            self.is_jumping = False

        if self.timers["dash"].active:
            self.dash_count = self.dash_count + 1 if self.dash_count < self.max_dash_count else self.max_dash_count

        self.rect.center = self.hitbox_rect.center
        self.move_camera()

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

    #animations
    def animate(self, dt):
        self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]
        self.image = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)
        self.frame_index += ANIMATION_SPEED * dt

    def get_state(self):
        print(self.state, int(self.frame_index % len(self.frames[self.state])))
        if self.colliding["ground"]:
            if self.is_attacking:
                self.state = f'melee{self.attack_stage + 1}'
            else:
                self.state = 'idle' if abs(self.velocity.x) < 0.2 else 'run'
        else:
            if self.is_attacking and self.can_air_atk:
                self.state = f'air{self.attack_stage + 1}'
            else:
                if self.velocity.y > 0:
                    self.state = 'jump'
                else:
                    self.state = 'fall'

        if self.timers["dash_cooldown"].active:
            self.state = 'dash'
    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def update(self, dt):
        self.prev_rect = self.hitbox_rect.copy()
        self.update_timers()
        self.check_collisions()

        self.input(dt)
        self.move(dt)

        self.get_state()
        self.animate(dt)