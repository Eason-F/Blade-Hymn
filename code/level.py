from constants import *
from sprite import Sprite
from player import Player
from groups import AllSprites

class Level:
    def __init__(self, tmx_map, level_frames, player_frames):
        self.display_surf = MASTER_DISPLAY

        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()

        self.player_rects = []
        self.enemy_rects = []

        self.player = None

        self.setup(tmx_map, level_frames, player_frames)

    def setup(self, tmx_map, level_frames, player_frames):
        for x, y, surf in tmx_map.get_layer_by_name("ground").tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, (self.all_sprites, self.collision_sprites))

        for obj in tmx_map.get_layer_by_name("objects"):
            if obj.name == "player":
                self.player = Player(
                    pos = (obj.x, obj.y),
                    groups = self.all_sprites,
                    collision_sprites = self.collision_sprites,
                    attack_rects = self.player_rects,
                    enemy_rects = self.enemy_rects,
                    frames = player_frames
                )

    def run(self, dt):
        self.display_surf.fill('black')
        self.all_sprites.update(dt)
        self.all_sprites.draw(self.display_surf, self.player.camera_rect.center)
