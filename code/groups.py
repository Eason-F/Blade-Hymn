import pygame.transform

from constants import *

class CameraLockedSprites(pygame.sprite.Group):
    def __init__(self, width, height):
        super().__init__()
        self.offset = vector(0,0)
        self.width, self.height = width, height

    def handle_offset(self, target_pos):
        self.offset.x = -(target_pos[0] - GAME_WIDTH / 2)
        self.offset.y = -(target_pos[1] - GAME_HEIGHT / 2)

    def camera_constraint(self):
        self.offset.x = self.offset.x if self.offset.x < 0 else 0
        self.offset.x = self.offset.x if self.offset.x > -self.width + GAME_WIDTH else -self.width + GAME_WIDTH
        self.offset.y = self.offset.y if self.offset.y > -self.height + GAME_HEIGHT else -self.height + GAME_HEIGHT

    def update_offset(self, target_pos):
        self.handle_offset(target_pos)
        self.camera_constraint()

    def draw(self, surface, target_pos):
        self.update_offset(target_pos)

class AllSprites(CameraLockedSprites):
    def __init__(self, width, height, bg_tiles, colour):
        super().__init__(width, height)
        self.bg_tiles = [pygame.transform.scale(tile, (GAME_WIDTH, GAME_HEIGHT)) for tile in bg_tiles]
        self.colour = colour
        self.tile_width = GAME_WIDTH
        self.tiles = 5

        self.desaturate_surf = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        self.desaturate_surf.fill((255, 255, 255, 50))

    def draw_bg(self, surface, target_pos):
        x_offset = -(target_pos[0] - GAME_WIDTH / 2)
        y_offset = -(target_pos[1] - GAME_HEIGHT / 2)
        for tile in range(self.tiles):
            for i in range(len(self.bg_tiles)):
                bg = self.bg_tiles[i]
                surface.blit(bg, (
                        self.tile_width * tile + (x_offset * (i / 25)),
                        (y_offset * (i / 25)) - 5
                    )
                )

        bottom = (y_offset * ((len(self.bg_tiles) - 1) / 25)) - 5 + GAME_HEIGHT
        fill = pygame.rect.FRect(0, bottom, GAME_WIDTH, GAME_HEIGHT)
        pygame.draw.rect(surface, self.colour, fill)
        surface.blit(self.desaturate_surf, (0, 0))


    def draw(self, surface, target_pos):
        super().draw(surface, target_pos)
        self.draw_bg(surface, target_pos)
        for sprite in sorted(self.sprites(), key = lambda x: x.z):
            offset_pos = sprite.rect.topleft + self.offset
            surface.blit(sprite.image, offset_pos)

class HitboxSprites(CameraLockedSprites):
    def __init__(self, width, height):
        super().__init__(width, height)

    def empty(self):
        for sprite in self.sprites():
            if not sprite.sustained:
                self.remove_internal(sprite)
                sprite.remove_internal(self)

    def draw(self, surface, target_pos):
        super().draw(surface, target_pos)
        for sprite in self:
            if sprite.visible:
                offset_pos = sprite.rect.topleft + self.offset
                surface.blit(sprite.image, offset_pos)

class AttackingSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def update(self):
        freeze_frame = [sprite.update_hitboxes() for sprite in self]
        if any(freeze_frame):
            return True
        return False

class UISprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def draw(self, surface):
        for sprite in [sprite for sprite in self if sprite.visible]:
            surface.blit(sprite.image, sprite.rect.topleft)

class MenuSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def draw(self, surface):
        for sprite in sorted(self.sprites(), key = lambda x: x.z):
            surface.blit(sprite.image, sprite.rect)

class ParallaxSprites(CameraLockedSprites):
    def __init__(self):
        super().__init__(GAME_WIDTH, GAME_HEIGHT)
        self.tile_width = GAME_WIDTH

        self.desaturate_surf = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        self.desaturate_surf.fill((255, 255, 255, 50))

    def draw(self, surface, target_pos):
        self.handle_offset(target_pos)
        for sprite in sorted(self.sprites(), key=lambda x: x.z):
            speed = sprite.z / 50
            offset_pos = (self.offset.x * speed - 20, self.offset.y * speed - 10)
            surface.blit(sprite.image, offset_pos)
            surface.blit(self.desaturate_surf, (0, 0))
