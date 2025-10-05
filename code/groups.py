from constants import *

class CameraLockedSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.offset = vector(100,0)

    def draw(self, surface, target_pos):
        self.offset.x = -(target_pos[0] - GAME_WIDTH / 2)
        self.offset.y = -(target_pos[1] - GAME_HEIGHT / 2)

        for sprite in self:
            offset_pos = sprite.rect.topleft + self.offset
            surface.blit(sprite.image, offset_pos)
