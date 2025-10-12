from constants import *
from text import TEXT_TAGS

from sprite import Sprite, Transition
from player import Player
from enemies import BasicSwordsman, BossSamurai, BossArcher
from groups import AllSprites, AttackingSprites, HitboxSprites, UISprites, TextSprites
from ui import HealthBar, CounterToken, Counter, Text

class Level:
    def __init__(self, name, tmx_map, ui_frames, level_frames, audio_files, player_frames, attack_impact_frames):
        self.display_surf = MASTER_DISPLAY
        self.name = name

        # entities
        self.player = None
        self.boss = None
        self.boss_health_bar = None

        # properties
        self.status = "normal"
        self.level_width = tmx_map.width * TILE_SIZE
        self.level_height = tmx_map.height * TILE_SIZE
        self.level_properties = tmx_map.get_layer_by_name("data").properties
        bg_tiles = level_frames["bg_tiles"][self.level_properties["bg"]]
        fill_colour = BG_FILL[self.level_properties["bg"]]

        # groups
        self.all_sprites = AllSprites(self.level_width, self.level_height, bg_tiles, fill_colour)
        self.ui_sprites = UISprites()
        self.collision_sprites = pygame.sprite.Group()
        self.text_sprites = TextSprites(self.level_width, self.level_height,)

        self.attacking_sprites = AttackingSprites()
        self.damage_sprites = HitboxSprites(self.level_width, self.level_height)

        # setup
        self.ui_frames = ui_frames
        self.reset(tmx_map, level_frames, audio_files, player_frames, attack_impact_frames)

        # transitions
        self.out_transition = Transition(1000, 255, groups=self.all_sprites)
        self.in_transition = Transition(2000, 0, groups=self.all_sprites)

        # sound

    def setup(self, tmx_map, level_frames, audio_files, player_frames, attack_impact_frames):
        for x, y, surf in tmx_map.get_layer_by_name("ground").tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, (self.all_sprites, self.collision_sprites), Z_VALUES['ground'])

        for x, y, surf in tmx_map.get_layer_by_name("barrier").tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, self.collision_sprites)

        for x, y, surf in tmx_map.get_layer_by_name("fg").tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, Z_VALUES['fg'])

        for x, y, surf in tmx_map.get_layer_by_name("bg").tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, Z_VALUES['bg'])

        for obj in tmx_map.get_layer_by_name("player"):
            self.player = Player(
                pos = (obj.x, obj.y),
                groups = (self.all_sprites, self.attacking_sprites),
                collision_sprites = self.collision_sprites,
                damage_sprites = self.damage_sprites,
                frames = player_frames,
                sounds = audio_files,
                attack_data = attack_impact_frames["player"],
                level_dim = (self.level_width, self.level_height)
            )

        for obj in tmx_map.get_layer_by_name("objects"):
            if obj.name == 'text':
                Text(
                    pos = (obj.x, obj.y),
                    text = TEXT_TAGS[obj.context][obj.tag],
                    size = 12,
                    groups = self.text_sprites
                )

            elif obj.name in ["sbasic", "dbasic", "wbasic"]:
                BasicSwordsman(
                    pos = (obj.x, obj.y),
                    hp = obj.hp,
                    groups = (self.all_sprites, self.attacking_sprites),
                    collision_sprites = self.collision_sprites,
                    damage_sprites = self.damage_sprites,
                    player = self.player,
                    frames = level_frames[obj.name],
                    sounds = audio_files,
                    attack_data = attack_impact_frames["basic"]
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
                    sounds = audio_files,
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
                    sounds = audio_files,
                    attack_data = attack_impact_frames[obj.name]
                )
                self.boss_health_bar = HealthBar((29, 20), obj.hp, self.ui_sprites, self.ui_frames[obj.name])

        HealthBar((10, 190), PlAYER_HEALTH, self.ui_sprites, self.ui_frames['player'])
        Counter((10, 215), self.ui_frames['player']['heal'], self.ui_frames['player']['heal_frame'], self.player.max_heal, self.ui_sprites)

    def reset(self, tmx_map, level_frames, audio_files, player_frames, attack_impact_frames):
        self.all_sprites.empty()
        self.ui_sprites.empty()
        self.collision_sprites.empty()
        self.text_sprites.empty()
        self.attacking_sprites.empty()
        self.damage_sprites.empty()

        self.in_transition = Transition(2000, 0, groups=self.all_sprites)

        self.boss = None
        self.boss_health_bar = None
        self.status = "normal"
        self.setup(tmx_map, level_frames, audio_files, player_frames, attack_impact_frames)

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

        if self.boss:
            self.boss_health_bar.update(hp = self.boss.hp)
            if self.boss.player_found and self.boss.hp > 0:
                self.boss_health_bar.visible = True
            else:
                self.boss_health_bar.visible = False

        for count in range(self.player.dash_count):
            CounterToken((50, 215), count, self.ui_frames['player']['dash'], self.player.max_dash_count, self.ui_sprites)

    def check_status(self):
        if not len(self.damage_sprites) and not self.player.fallen:
            self.status = 'complete'
        elif self.player.fallen:
            self.status = 'fail'

    def run(self, dt):
        self.damage_sprites.empty()

        # update
        if self.status == 'normal':
            self.attacking_sprites.update()
            self.damage_sprites.update(dt)
            self.all_sprites.update(dt)
        self.update_ui(dt)
        self.check_status()

        # draw
        self.all_sprites.draw(self.display_surf, self.player.camera_rect.center)
        self.damage_sprites.draw(self.display_surf, self.player.camera_rect.center)
        self.ui_sprites.draw(self.display_surf)
        self.text_sprites.draw(self.display_surf, self.player.camera_rect.center)

        self.in_transition.draw(self.display_surf)
        self.out_transition.draw(self.display_surf)
