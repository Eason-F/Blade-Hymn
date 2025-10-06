from constants import *
from sprite import Sprite
from player import Player
from enemies import SpringBasic
from groups import CameraLockedSprites, AttackingSprites

class Level:
    def __init__(self, tmx_map, level_frames, player_frames, attack_impact_frames):
        self.display_surf = MASTER_DISPLAY
        self.player = None

        # groups
        self.all_sprites = CameraLockedSprites()
        self.collision_sprites = pygame.sprite.Group()

        self.attacking_sprites = AttackingSprites()
        self.damage_sprites = CameraLockedSprites()

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
            if obj.name == "sbasic":
                SpringBasic(
                    pos = (obj.x, obj.y),
                    groups = (self.all_sprites, self.attacking_sprites, self.damage_sprites),
                    collision_sprites = self.collision_sprites,
                    damage_sprites = self.damage_sprites,
                    player = self.player,
                    frames = level_frames[obj.name],
                    attack_data = attack_impact_frames[obj.name]
                )


    def run(self, dt):
        self.display_surf.fill('black')

        self.damage_sprites.empty()
        self.attacking_sprites.update()

        self.all_sprites.update(dt)
        self.all_sprites.draw(self.display_surf, self.player.camera_rect.center)

        self.damage_sprites.draw(self.display_surf, self.player.camera_rect.center)
