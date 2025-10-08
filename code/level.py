from constants import *

from sprite import Sprite
from player import Player
from enemies import BasicSwordsman, BossSamurai, BossArcher
from groups import CameraLockedSprites, AttackingSprites, HitboxSprites, UISprites
from ui import HealthBar, CounterToken, Counter

class Level:
    def __init__(self, tmx_map, ui_frames, level_frames, player_frames, attack_impact_frames):
        self.display_surf = MASTER_DISPLAY

        # general
        self.player = None
        self.boss = None
        self.boss_health_bar = None

        # groups
        self.all_sprites = CameraLockedSprites()
        self.ui_sprites = UISprites()
        self.collision_sprites = pygame.sprite.Group()

        self.attacking_sprites = AttackingSprites()
        self.damage_sprites = HitboxSprites()

        self.ui_frames = ui_frames
        self.setup(tmx_map, level_frames, player_frames, attack_impact_frames)

    def setup(self, tmx_map, level_frames, player_frames, attack_impact_frames):
        for x, y, surf in tmx_map.get_layer_by_name("ground").tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, (self.all_sprites, self.collision_sprites))

        for obj in tmx_map.get_layer_by_name("objects"):
            if obj.name == "player":
                self.player = Player(
                    pos = (obj.x, obj.y),
                    groups = (self.all_sprites, self.attacking_sprites),
                    collision_sprites = self.collision_sprites,
                    damage_sprites = self.damage_sprites,
                    frames = player_frames,
                    attack_data= attack_impact_frames["player"]
                )
            elif obj.name in ["sbasic", "dbasic", "cbasic"]:
                BasicSwordsman(
                    pos = (obj.x, obj.y),
                    hp = obj.hp,
                    groups = (self.all_sprites, self.attacking_sprites),
                    collision_sprites = self.collision_sprites,
                    damage_sprites = self.damage_sprites,
                    player = self.player,
                    frames = level_frames[obj.name],
                    attack_data = attack_impact_frames[obj.name]
                )
            elif obj.name == 'samurai':
                self.boss = BossSamurai(
                    pos = (obj.x, obj.y),
                    hp = obj.hp,
                    groups = (self.all_sprites, self.attacking_sprites),
                    collision_sprites = self.collision_sprites,
                    damage_sprites = self.damage_sprites,
                    player = self.player,
                    frames = level_frames[obj.name],
                    attack_data = attack_impact_frames[obj.name]
                )
                self.boss_health_bar = HealthBar((29, 20), obj.hp, self.ui_sprites, self.ui_frames[obj.name])
            elif obj.name == 'archer':
                self.boss = BossArcher(
                    pos = (obj.x, obj.y),
                    hp = obj.hp,
                    groups = (self.all_sprites, self.attacking_sprites),
                    collision_sprites = self.collision_sprites,
                    damage_sprites = self.damage_sprites,
                    player = self.player,
                    frames = level_frames[obj.name],
                    attack_data = attack_impact_frames[obj.name]
                )
                self.boss_health_bar = HealthBar((29, 20), obj.hp, self.ui_sprites, self.ui_frames[obj.name])

        HealthBar((10, 190), PlAYER_HEALTH, self.ui_sprites, self.ui_frames['player'])
        Counter((10, 215), self.ui_frames['player']['heal'], self.ui_frames['player']['heal_frame'], self.player.max_heal, self.ui_sprites)

    def update_ui(self, dt):
        for sprite in self.ui_sprites:
            if not sprite.sustained:
                sprite.kill()
            else:
                sprite.update(
                    hp = self.player.hp,
                    count = self.player.heal_count,
                    dt = dt
                )

        self.boss_health_bar.update(hp = self.boss.hp)
        if self.boss.player_found and self.boss.hp > 0:
            self.boss_health_bar.visible = True
        else:
            self.boss_health_bar.visible = False

        for count in range(self.player.dash_count):
            CounterToken((50, 215), count, self.ui_frames['player']['dash'], self.player.max_dash_count, self.ui_sprites)

    def run(self, dt):
        self.display_surf.fill('light blue')

        self.damage_sprites.empty()
        self.attacking_sprites.update()

        self.damage_sprites.update(dt)
        self.all_sprites.update(dt)
        self.all_sprites.draw(self.display_surf, self.player.camera_rect.center)

        self.damage_sprites.draw(self.display_surf, self.player.camera_rect.center)

        self.update_ui(dt)
        self.ui_sprites.draw(self.display_surf)
