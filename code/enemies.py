from abc import ABC, abstractmethod

from constants import *

from timer import Timer
from sprite import Hitbox


class Enemy(pygame.sprite.Sprite, ABC):
    def __init__(self, pos, groups, collision_sprites, damage_sprites, player, frames, attack_data):
        super().__init__(groups)
        self.player = player
        self.player_pos = player.hitbox_rect.center

        # animation
        self.frames, self.frame_index = frames, 0
        self.state, self.direction = 'walk', 1
        self.image = self.frames[self.state][self.frame_index]
        self.attack_data = attack_data

        self.timers = {
            "attack_cooldown": Timer(1200, sustained=True),
            "attack": Timer(200, sustained=True),
            "stun_recovery": Timer(1000, sustained=True),
            "knocked_back": Timer(700, sustained=True),
            "hit_cooldown": Timer(200, sustained=True),
        }

        # hitbox rect
        self.rect = self.image.get_frect(topleft=pos)
        self.hitbox_rect = self.rect.inflate(-72, -32)
        self.prev_rect = self.hitbox_rect.copy()

        # movement
        self.gravity = GRAVITY
        self.friction = 7
        self.velocity = vector(0, 0)
        self.speed = 25

        self.collisions = {
            'right_edge': False,
            'left_edge': False
        }

        # interaction
        self.collision_sprites = collision_sprites
        self.damage_sprites = damage_sprites

        # combat
        self.player_found = False
        self.can_attack = False
        self.is_attacking = False
        self.attack_stage = 1
        self.attack_combo = False
        self.attack_choice = None

        self.stunned = False

        # variable
        self.sight_range = None
        self.attack_range = None

    def move(self, dt):
        # prevent enemies from falling off ledge
        if not self.collisions["right_edge"]:
            if self.velocity.x > 0:
                self.velocity.x = 0
        elif not self.collisions["left_edge"]:
            if self.velocity.x < 0:
                self.velocity.x = 0

        # apply friction only when knocked back
        if self.timers["knocked_back"].active:
            friction_factor = self.friction * -self.velocity.x
            self.velocity.x += friction_factor / 2 * dt
            self.hitbox_rect.x += self.velocity.x * dt * 10
            self.velocity.x += friction_factor / 2 * dt
        else: # use simple movement when not knocked back
            self.hitbox_rect.x += self.velocity.x * dt
            self.surface_collisions('x')

        # apply gravity
        self.velocity.y += self.gravity / 2 * dt
        self.hitbox_rect.y += self.velocity.y * dt
        self.velocity.y += self.gravity / 2 * dt
        self.surface_collisions('y')

        self.rect.center = self.hitbox_rect.center

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

    def check_collisions(self):
        floor_rect_right = pygame.FRect(self.hitbox_rect.bottomright, (-1, 10))
        floor_rect_left = pygame.FRect(self.hitbox_rect.bottomleft, (-1, 10))
        collide_rects = [sprite.rect for sprite in self.collision_sprites]

        self.collisions["right_edge"] = True if floor_rect_right.collidelist(collide_rects) >= 0 else False
        self.collisions["left_edge"] = True if floor_rect_left.collidelist(collide_rects) >= 0 else False

    def find_player(self):
        player_dist = math.dist((self.hitbox_rect.center[0], 0), (self.player_pos[0], 0))
        if player_dist < self.sight_range:
            self.player_found = True
        else:
            self.player_found = False

        if player_dist < self.attack_range:
            self.can_attack = True
        else:
            if not self.is_attacking:
                self.can_attack = False
                self.attack_stage = random.choice(self.attack_choice)

    # combat
    def knock_back(self, direction, force):
        self.velocity.x = direction * force

        self.timers["knocked_back"].activate()

    def knock_down(self, direction, force=5):
        if not self.stunned:
            self.is_attacking = False
            self.can_attack = False

            self.knock_back(direction, force)
            self.velocity.y = -50
            self.timers["stun_recovery"].activate()

    def handle_knockdown(self):
        if self.timers["stun_recovery"].active:
            self.stunned = True
        else:
            self.stunned = False

    def check_damage(self):
        damage_rects = [sprite for sprite in self.damage_sprites if sprite.tag == 'player']
        damaging_hitbox = self.hitbox_rect.collideobjects(damage_rects, key=lambda x: x.rect)
        is_hit = True if damaging_hitbox else False

        if is_hit and not self.timers["hit_cooldown"].active:
            self.timers["hit_cooldown"].activate()
            if damaging_hitbox.stun:
                self.knock_down(damaging_hitbox.direction, damaging_hitbox.knockback)
            else:
                self.knock_back(damaging_hitbox.direction, damaging_hitbox.knockback)
            self.attack_choice = [1, 2]
    
    def animate(self, dt):
        self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]
        self.image = self.image if self.direction > 0 else pygame.transform.flip(self.image, True, False)
        self.frame_index += ANIMATION_SPEED * dt

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def update_hitboxes(self):
        if self.timers['attack'].active:
            Hitbox('enemy',
                   self.hitbox_rect.center,
                   self.direction,
                   self.attack_data[self.state],
                   self.damage_sprites,
                   'yellow')

        Hitbox('enemy',
               self.hitbox_rect.center,
               self.direction,
               self.attack_data['contact'],
               self.damage_sprites,
               'yellow')

    def update(self, dt):
        self.prev_rect = self.hitbox_rect.copy()
        self.player_pos = self.player.hitbox_rect.center
        self.update_timers()

        self.check_collisions()
        self.check_damage()
        self.handle_knockdown()

    @abstractmethod
    def attack(self):
        pass

    @abstractmethod
    def get_state(self):
        pass


class SpringBasic(Enemy):
    def __init__(self, pos, groups, collision_sprites, damage_sprites, player, frames, attack_data):
        super().__init__(pos, groups, collision_sprites, damage_sprites, player, frames, attack_data)

        self.hitbox_rect = self.rect.inflate(-84, -41)
        self.prev_rect = self.hitbox_rect.copy()

        self.speed = 25
        self.sight_range = 200
        self.attack_range = 40

        self.player_found = False
        self.can_attack = False
        self.attack_choice = [1, 1, 1, 2]

    def move(self, dt):
        if not self.timers["knocked_back"].active:
            self.velocity.x = 0

            if self.player_found and not self.stunned:
                if not self.is_attacking:
                    self.direction = 1 if self.player_pos[0] > self.hitbox_rect.center[0] else -1

                if not self.can_attack:
                    self.velocity.x = self.direction * self.speed

        super().move(dt)

    def attack(self):
        if self.can_attack and not self.timers["attack_cooldown"].active:
            if not self.is_attacking:
                if not self.attack_combo:
                    self.frame_index = 0
                else:
                    self.frame_index = 3
            self.is_attacking = True

        if 'melee' in self.state:
            if self.frame_index >= len(self.frames[self.state]):
                self.is_attacking = False

                if random.randint(0,2) == 1 and self.attack_stage == 1:
                    self.attack_stage += 1
                    self.attack_combo = True
                else:
                    self.timers['attack_cooldown'].activate()
                    self.attack_combo = False
                    self.attack_choice = [1, 1, 1, 2]
                    self.attack_stage = random.choice(self.attack_choice)

    def get_state(self):
        if self.is_attacking:
            self.state = f'melee{self.attack_stage}'
        else:
            if self.velocity.x:
                self.state = 'walk'
            else:
                self.state = 'idle'

    def update_hitboxes(self):
        if 'melee' in self.state:
            if int(self.frame_index) + 1 in self.attack_data[self.state]["impact"]:
                self.timers["attack"].activate()
        else:
            self.timers["attack"].deactivate()

        super().update_hitboxes()

    def update(self, dt):
        super().update(dt)

        self.find_player()
        self.move(dt)
        self.attack()

        self.get_state()
        self.animate(dt)
