from abc import ABC, abstractmethod

from constants import *

from timer import Timer
from sprite import Hitbox, Projectile


class Enemy(pygame.sprite.Sprite, ABC):
    def __init__(self, pos, hp, groups, collision_sprites, damage_sprites, player, frames, attack_data):
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
            "hit_cooldown": Timer(250, sustained=True),
            "fallen": Timer(2000, sustained=True),
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
        self.hp = hp
        self.player_found = False
        self.can_attack = False
        self.is_attacking = False
        self.attack_stage = 1
        self.attack_choice = None

        self.stunned = False

        # variable
        self.sight_range = None
        self.attack_range = None

    # movement
    def move(self, dt):
        if not self.timers["knocked_back"].active and not self.stunned:
            self.velocity.x = 0
            if self.player_found and not self.is_attacking:
                self.direction = 1 if self.player_pos[0] > self.hitbox_rect.center[0] else -1
                self.move_to_player()

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

    def move_to_player(self):
        if not self.can_attack:
            self.velocity.x = self.direction * self.speed

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
        player_dist_x = abs(self.hitbox_rect.center[0] - self.player_pos[0])
        player_dist_y = abs(self.hitbox_rect.center[1] - self.player_pos[1])
        if player_dist_x <= self.sight_range and player_dist_y <= 80:
            self.player_found = True
        else:
            self.player_found = False

        if player_dist_x <= self.attack_range:
            self.can_attack = True
        elif not self.is_attacking:
            self.can_attack = False
            self.attack_stage = random.choice(self.attack_choice)

    # animation
    @abstractmethod
    def get_state(self):
        if self.timers["fallen"].active:
            self.state = 'fallen'

    def animate(self, dt):
        self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]
        self.image = self.image if self.direction > 0 else pygame.transform.flip(self.image, True, False)
        self.frame_index += ANIMATION_SPEED * dt

    def hit_flicker(self):
        if self.timers["hit_cooldown"].active and math.sin(pygame.time.get_ticks() / 32) >= 0:
            white_mask = pygame.mask.from_surface(self.image)
            white_surf = white_mask.to_surface()
            white_surf.set_colorkey('black')
            self.image = white_surf

    # combat
    @abstractmethod
    def attack(self):
        pass

    @abstractmethod
    def counter_attack(self):
        pass

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

        if is_hit and not self.timers["hit_cooldown"].active and not self.hp <= 0:
            self.timers["hit_cooldown"].activate()
            if damaging_hitbox.stun:
                self.knock_down(damaging_hitbox.direction, damaging_hitbox.knockback)
            else:
                self.knock_back(damaging_hitbox.direction, damaging_hitbox.knockback)
            self.timers["attack"].deactivate()
            self.counter_attack()
            self.take_damage(damaging_hitbox.damage)

        if self.state == 'fallen' and self.frame_index >= len(self.frames[self.state]) - 1:
            if not self.timers["fallen"].active:
                self.kill()
            self.frame_index = len(self.frames[self.state]) - 1

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0 and (not self.timers["fallen"].active):
            self.frame_index = 0
            self.timers["fallen"].activate()

    # update
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

        if not self.timers["fallen"].active:
            self.find_player()
            self.move(dt)
            self.attack()

        self.get_state()
        self.animate(dt)
        self.hit_flicker()

class BasicSwordsman(Enemy):
    def __init__(self, pos, hp, groups, collision_sprites, damage_sprites, player, frames, attack_data):
        super().__init__(pos, hp, groups, collision_sprites, damage_sprites, player, frames, attack_data)

        self.hitbox_rect = self.rect.inflate(-84, -42)
        self.prev_rect = self.hitbox_rect.copy()

        self.speed = 25
        self.sight_range = 200
        self.attack_range = 45
        self.attack_choice = [1, 1, 1, 2]
        self.attack_combo = False

        self.timers["attack_cooldown"] = Timer(1000, sustained=True)
        self.timers["combo_cooldown"] = Timer(400, sustained=True)

    def attack(self):
        if self.can_attack and not (self.timers["attack_cooldown"].active or self.timers["combo_cooldown"].active):
            if not self.is_attacking:
                if not self.attack_combo:
                    self.frame_index = 0
                else:
                    self.frame_index = 3
                self.direction = 1 if self.player_pos[0] > self.hitbox_rect.center[0] else -1
            self.is_attacking = True

        if 'melee' in self.state:
            if self.frame_index >= len(self.frames[self.state]):
                self.is_attacking = False

                self.timers["attack_cooldown"].activate()
                self.timers["combo_cooldown"].deactivate()
                self.attack_choice = [1, 1, 1, 2]

                if random.randint(0,2) == 1 and self.attack_stage == 1:
                    self.attack_choice = [2]
                    self.attack_combo = True
                    self.timers["attack_cooldown"].deactivate()
                    self.timers['combo_cooldown'].activate()
                else:
                    self.attack_combo = False

                self.attack_stage = random.choice(self.attack_choice)

    def counter_attack(self):
        if random.randint(0, 2) == 1:
            self.attack_stage = 2
            self.attack_combo = True
            self.timers["attack_cooldown"].deactivate()
            self.timers['combo_cooldown'].activate()

    def get_state(self):
        if self.is_attacking:
            self.state = f'melee{self.attack_stage}'
        else:
            if self.velocity.x:
                self.state = 'walk'
            else:
                self.state = 'idle'
        super().get_state()

    def update_hitboxes(self):
        if 'melee' in self.state:
            if int(self.frame_index) + 1 in self.attack_data[self.state]["impact"]:
                self.timers["attack"].activate()
        else:
            self.timers["attack"].deactivate()

        super().update_hitboxes()

class BossSamurai(Enemy):
    def __init__(self, pos, hp, groups, collision_sprites, damage_sprites, player, frames, attack_data):
        super().__init__(pos, hp, groups, collision_sprites, damage_sprites, player, frames, attack_data)

        self.hitbox_rect = self.rect.inflate(-80, -52)
        self.prev_rect = self.hitbox_rect.copy()

        self.speed = 30
        self.sight_range = 300
        self.attack_range = 50

        self.base_attack_choice = [1, 1, 1, 1, 2, 2, 3]
        self.attack_choice = self.base_attack_choice

        self.timers["attack_cooldown"] = Timer(1000, sustained=True)
        self.timers["blocking"] = Timer(3000, sustained=True)
        self.timers["block_duration"] = Timer(200, sustained=True)

    def attack(self):
        if self.timers["blocking"].active:
            self.can_attack = False
            self.is_attacking = True

        if self.can_attack and not self.timers["attack_cooldown"].active:
            if not self.is_attacking:
                if random.randint(0, 3) == 1:
                    self.timers["blocking"].activate()
                else:
                    self.frame_index = 0
                    self.is_attacking = True
                self.direction = 1 if self.player_pos[0] > self.hitbox_rect.center[0] else -1

        if 'melee' in self.state:
            if self.frame_index >= len(self.frames[self.state]):
                self.is_attacking = False

                self.timers["attack_cooldown"].activate()
                self.attack_choice = self.base_attack_choice
                self.attack_stage = random.choice(self.attack_choice)

    def counter_attack(self):
        if random.randint(0, 2) == 1:
            self.attack_stage = 3
            self.timers["attack_cooldown"].deactivate()

    def take_damage(self, damage):
        if not self.timers["blocking"].active:
            super().take_damage(damage)
        else:
            self.timers["block_duration"].activate()
            self.timers["attack_cooldown"].deactivate()

    def get_state(self):
        if self.timers["blocking"].active:
            self.state = 'block'
        elif self.stunned:
            self.state = 'hurt'
        elif self.is_attacking:
            self.state = f'melee{self.attack_stage}'
        elif not self.can_attack:
            if abs(self.velocity.x) > 0.5:
                self.state = 'walk'
            else:
                self.state = 'idle'

        super().get_state()

    def update_hitboxes(self):
        if 'melee' in self.state:
            check = [int(self.frame_index) + 1 > impact for impact in self.attack_data[self.state]["impact"]]
            if any(check):
                self.timers["attack"].activate()
                self.timers["block_duration"].deactivate()
        elif self.timers["block_duration"].active:
            self.timers["attack"].activate()
            self.timers["blocking"].deactivate()
        else:
            self.timers["attack"].deactivate()

        super().update_hitboxes()

class BossArcher(Enemy):
    def __init__(self, pos, hp, groups, collision_sprites, damage_sprites, player, frames, attack_data):
        super().__init__(pos, hp, groups, collision_sprites, damage_sprites, player, frames, attack_data)

        self.hitbox_rect = self.rect.inflate(-80, -78)
        self.prev_rect = self.hitbox_rect.copy()

        self.speed = 30
        self.sight_range = 300
        self.max_shoot_range, self.min_shoot_range = 350, 150
        self.attack_range = 50

        self.max_combo_length = 2
        self.combo_length = 0

        self.can_shoot = False
        self.is_shooting = False
        self.has_shot = True
        self.max_ammo = self.ammo = 2

        self.base_attack_choice = [1, 1, 1, 2, 2]
        self.attack_choice = self.base_attack_choice

        self.timers["attack_cooldown"] = Timer(1600, sustained=True)
        self.timers["combo_cooldown"] = Timer(200, sustained=True)

    def find_player(self):
        super().find_player()
        player_dist_x = abs(self.hitbox_rect.center[0] - self.player_pos[0])
        if self.min_shoot_range < player_dist_x < self.max_shoot_range and self.player_found:
            self.can_shoot = True
        else:
            self.can_shoot = False

    def move_to_player(self):
        if not (self.can_attack or self.is_shooting):
            self.velocity.x = self.direction * self.speed

    def attack(self):
        if self.ammo <= 0:
            self.can_shoot = False

        if not (self.timers["attack_cooldown"].active or self.timers["combo_cooldown"].active):
            if self.can_shoot:
                if not self.is_shooting and not self.is_attacking:
                    self.frame_index = 0
                    self.is_shooting = True
                    self.is_attacking = False

            elif self.can_attack:
                if not self.is_attacking:
                    self.frame_index = 0
                    self.is_attacking = True
                    self.is_shooting = False
                    self.combo_length += 1
                    self.direction = 1 if self.player_pos[0] > self.hitbox_rect.center[0] else -1

            if self.frame_index >= len(self.frames[self.state]):
                self.frame_index = 0
                if self.state == 'shoot' or 'melee' in self.state:
                    self.timers["attack_cooldown"].activate()

                if 'melee' in self.state:
                    self.is_attacking = False

                    self.attack_choice = self.base_attack_choice
                    self.chain_attacks()
                    self.attack_stage = random.choice(self.attack_choice)

                    self.ammo = self.ammo + 1 if self.ammo < self.max_ammo else self.ammo
                elif 'shoot' in self.state:
                    self.is_shooting = False
                    self.ammo -= 1

    def chain_attacks(self):
        if self.combo_length < self.max_combo_length and random.randint(0, 1) == 1:
            self.attack_choice = [1, 2]
            self.timers["attack_cooldown"].deactivate()
            self.timers["combo_cooldown"].activate()
        else:
            self.combo_length = 0
            if random.randint(0, 1) == 1:
                self.attack_choice = [3]

    def counter_attack(self):
        if random.randint(0, 3) == 1:
            self.attack_stage = random.choice([2, 2, 3])
            self.ammo = self.ammo + 1 if self.ammo < self.max_ammo else self.ammo
            self.timers["attack_cooldown"].deactivate()
            self.frame_index = 3

    def get_state(self):
        if self.stunned:
            self.state = 'hurt'
        elif self.is_attacking and self.can_attack:
            self.state = f'melee{self.attack_stage}'
        elif self.is_shooting:
            self.state = 'shoot'
        else:
            if abs(self.velocity.x) > 0.5:
                self.state = 'walk'
            else:
                self.state = 'idle'
        super().get_state()

    def update_hitboxes(self):
        if 'melee' in self.state:
            if int(self.frame_index) + 1 in self.attack_data[self.state]["impact"]:
                self.timers["attack"].activate()
        elif self.state == "shoot":
            if int(self.frame_index) + 1 in self.attack_data[self.state]["impact"]:
                self.has_shot = False
                self.frame_index += 1
        else:
            self.timers["attack"].deactivate()

        if not self.has_shot:
            self.has_shot = True
            Projectile(
                tag = "enemy",
                pos = self.hitbox_rect.center,
                direction = self.direction,
                data = self.attack_data[self.state],
                image = self.frames["arrow"][0],
                collision_rects = [sprite.rect for sprite in self.collision_sprites],
                groups = self.damage_sprites
            )

        super().update_hitboxes()