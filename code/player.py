from constants import *

from timer import Timer
from sprite import Hitbox

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, attack_sprites, enemy_sprites, frames, attack_impact_frames):
        super().__init__(groups)

        # animation
        self.frames, self.frame_index = frames, 0
        self.state, self.direction = 'idle', 1
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

        self.control_lock = False

        # attack
        self.attack_data = attack_impact_frames
        self.is_attacking = self.attack_combo = False
        self.attack_stage, self.attack_stage_count = -1, 3
        self.can_air_atk = True
        self.can_air_boost = True

        # combat
        self.knocked_down = False
        self.vulnerable = True

        # collisions
        self.collision_sprites = collision_sprites

        self.attack_sprites = attack_sprites
        self.enemy_sprites = enemy_sprites

        self.colliding = {
            "ground": False,
            "hitbox": False
        }

        # timers
        self.timers = {
            "stun_recovery": Timer(1000, sustained=True),
            "dash": Timer(1500, auto_start=True, repeat=True),
            "dash_cooldown": Timer(250, sustained=True),
            "attack_combo": Timer(200),
            "attack": Timer(200, sustained=True)
        }

    def input(self, dt):
        keys = pygame.key.get_pressed()
        movement_vect = vector(0, 0)

        if keys[pygame.K_LCTRL]:
            self.knock_down(-self.direction)

        if not self.control_lock:
            if not ("melee" in self.state and self.is_attacking):
                if keys[pygame.K_LEFT]:
                    movement_vect.x -= self.acceleration
                    self.direction = -1

                if keys[pygame.K_RIGHT]:
                    movement_vect.x += self.acceleration
                    self.direction = 1

            if not self.is_attacking:
                if keys[pygame.K_LSHIFT]:
                    movement_vect.x = self.dash(movement_vect.x)

            self.velocity.x += movement_vect.x * dt

            if self.colliding["ground"]:
                self.can_air_atk = True

            if keys[pygame.K_x]:
                if self.colliding["ground"] or self.can_air_atk:
                    self.attack()
            self.attack_update()

            if not self.is_attacking:
                if keys[pygame.K_SPACE]:
                    if self.colliding["ground"]:
                        self.is_jumping = True
        else:
            if keys[pygame.K_SPACE]:
                self.timers["stun_recovery"].deactivate()

    # input related actions
    def dash(self, speed):
        if self.dash_count > 0 and not self.timers["dash_cooldown"].active:
            speed = self.dash_distance * self.direction

            self.dash_count -= 1
            self.timers["dash_cooldown"].activate()
        return speed

    # attacking
    def attack(self):
        if not self.is_attacking:
            self.attack_stage = (self.attack_stage + 1) % self.attack_stage_count
            self.frame_index = 0
            self.can_air_boost = True
            self.timers["dash_cooldown"].deactivate() # prevent dash cooldown while attacking

        self.is_attacking = True
        self.attack_combo = True
        self.timers['attack_combo'].deactivate()

    def attack_update(self):
        if self.colliding["ground"]:
            self.attack_stage_count = 3
        else:
            self.attack_stage_count = 2

        if 'melee' in self.state or 'air' in self.state:
            if self.frame_index >= len(self.frames[self.state]):
                self.is_attacking = False
                self.timers['attack_combo'].activate()

                if self.attack_stage == 1 and 'air' in self.state:
                    self.can_air_atk = False
                    self.attack_combo = False

        if self.timers['attack_combo'].active:
            self.attack_combo = False
            self.is_attacking = False
            self.attack_stage = -1

            if self.state in ['jump', 'fall']: # prevent continous air attacks
                self.can_air_atk = False

    def handle_hitboxes(self):
        if self.is_attacking:
            if int(self.frame_index) + 1 in self.attack_data[self.state]["impact"]:
                self.timers["attack"].activate()
        else:
            self.timers["attack"].deactivate()

        if self.timers["attack"].active:
            Hitbox(self.hitbox_rect.center,
                   self.attack_data[self.state]["rel_pos"],
                   self.attack_data[self.state]["size"],
                   self.direction,
                   self.attack_data[self.state]["damage"],
                   self.attack_sprites)

    # movement related actions
    def move(self, dt):
        friction_factor = self.friction * -self.velocity.x
        self.velocity.x += friction_factor / 2 * dt
        self.hitbox_rect.x += self.velocity.x * self.speed * dt
        self.velocity.x += friction_factor / 2 * dt
        self.surface_collisions('x')

        if 'air' in self.state: # give slight vertical boost when air attacking
            if self.can_air_boost:
                self.velocity.y = -self.jump_height / 1.7
                self.can_air_boost = False

        self.velocity.y += self.gravity / 2 * dt
        self.hitbox_rect.y += self.velocity.y * dt
        self.velocity.y += self.gravity / 2 * dt
        self.surface_collisions('y')

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

    def surface_collisions(self, axis):
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

    # knockdown
    def knock_down(self, direction, force = 5):
        if not self.knocked_down:
            self.knocked_down = True
            self.control_lock = True

            self.is_attacking = False
            self.attack_combo = False

            self.velocity.y = -50
            self.velocity.x = direction * force

    def handle_knockdown(self):
        if self.colliding["ground"]:
            if self.knocked_down:
                self.timers["stun_recovery"].activate()

            self.knocked_down = False
            self.control_lock = False

        if self.timers["stun_recovery"].active:
            self.control_lock = True

    # animations
    def animate(self, dt):
        self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]
        self.image = self.image if self.direction > 0 else pygame.transform.flip(self.image, True, False)
        self.frame_index += ANIMATION_SPEED * dt

    def get_state(self):
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
        self.handle_knockdown()

        self.input(dt)
        self.move(dt)

        self.get_state()
        self.animate(dt)

        self.handle_hitboxes()