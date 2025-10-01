from pytmx.util_pygame import load_pygame

from constants import *
from level import Level

class Game:
    def __init__(self):
        pygame.init()
        self.display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), vsync=1)
        self.display_surf = MASTER_DISPLAY
        pygame.display.set_caption("Blade Hymn")

        self.clock = pygame.time.Clock()

        self.tmx_data = {
            0: load_pygame(os.path.join(abs_path, "Data", "tmx", "testmap.tmx"))
        }

        self.current_level = Level(self.tmx_data[0])

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.current_level.run(dt)

            self.display.blit(pygame.transform.scale_by(self.display_surf, SCALE_FACTOR), (0, 0))
            pygame.display.update()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()