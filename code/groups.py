from constants import *

class CameraLockedSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.offset = vector(0,0)

    def handle_offset(self, target_pos):
        self.offset.x = -(target_pos[0] - GAME_WIDTH / 2)
        self.offset.y = -(target_pos[1] - GAME_HEIGHT / 2)

    def draw(self, surface, target_pos):
        self.handle_offset(target_pos)
        for sprite in self:
            offset_pos = sprite.rect.topleft + self.offset
            surface.blit(sprite.image, offset_pos)

class UISprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def draw(self, surface):
        for sprite in [sprite for sprite in self if sprite.visible]:
            surface.blit(sprite.image, sprite.rect.topleft)

class HitboxSprites(CameraLockedSprites):
    def __init__(self):
        super().__init__()

    def empty(self):
        for sprite in self.sprites():
            if not sprite.sustained:
                self.remove_internal(sprite)
                sprite.remove_internal(self)

    def draw(self, surface, target_pos):
        self.handle_offset(target_pos)
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
