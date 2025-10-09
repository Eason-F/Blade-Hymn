import json
from pytmx.util_pygame import load_pygame

from constants import *
from utility import import_subfolders
from debug import debug

from level import Level
from menu import MainMenu

class Game:
    def __init__(self):
        pygame.init()
        self.display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), vsync=1)
        self.display_surf = MASTER_DISPLAY
        pygame.display.set_caption("Blade Hymn")

        self.clock = pygame.time.Clock()

        # assets
        self.level_frames = {}
        self.player_frames = {}
        self.ui_frames = {}
        self.attack_impact_frames = {}

        self.import_assets()

        # level data
        self.tmx_data = {
            0: load_pygame(os.path.join(abs_path, "data", "tmx", "testmap.tmx"))
        }

        self.current_stage = None
        self.stages = {
            "main_menu": MainMenu(self.level_frames["bg_tiles"], self.ui_frames),
            "test": Level(self.tmx_data[0], self.ui_frames, self.level_frames, self.player_frames, self.attack_impact_frames)
        }

        self.set_stage("main_menu")

    def import_assets(self):
        self.level_frames = {
            "sbasic": import_subfolders("assets", "graphics", "enemies", "sbasic"),
            "wbasic": import_subfolders("assets", "graphics", "enemies", "wbasic"),
            "dbasic": import_subfolders("assets", "graphics", "enemies", "dbasic"),
            "samurai": import_subfolders("assets", "graphics", "enemies", "bossSamurai"),
            "archer": import_subfolders("assets", "graphics", "enemies", "bossArcher"),
            "bg_tiles": import_subfolders("assets", "graphics", "background"),
        }
        self.player_frames = import_subfolders("assets", "graphics", "player")
        self.ui_frames = {
            "player": import_subfolders("assets", "graphics", "ui", "player"),
            "archer": import_subfolders("assets", "graphics", "ui", "bossArcher"),
            "samurai": import_subfolders("assets", "graphics", "ui", "bossSamurai"),
        }

        with open(os.path.join(abs_path, "data", "json", "attack_data.json")) as jsonf:
            self.attack_impact_frames = json.load(jsonf)

    def set_stage(self, stage):
        self.current_stage = self.stages[stage]
        self.current_stage.in_transition.start()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.set_stage("test")

            self.current_stage.run(dt)

            debug(self.current_stage.in_transition.active)

            self.display.blit(pygame.transform.scale_by(self.display_surf, SCALE_FACTOR), (0, 0))
            pygame.display.update()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()