from constants import *
from sprite import Sprite, Transition
from groups import MenuSprites, ParallaxSprites, TextSprites
from ui import Button, SelectionIndicator, Text
from timer import Timer

class MainMenu:
    def __init__(self, bg_frames, ui_frames, audio_files):
        self.display_surf = MASTER_DISPLAY

        # groups
        self.sprites = pygame.sprite.Group()
        self.bg_sprites = ParallaxSprites()
        self.button_sprites = pygame.sprite.Group()
        self.graphic_sprites = MenuSprites()
        self.text_sprites = TextSprites(GAME_WIDTH, GAME_HEIGHT)

        self.timers = {
            "button_click": Timer(200, sustained=True)
        }

        # sound
        self.music = audio_files

        # input
        self.mouse_pos = (0, 0)
        self.mouse_states = None
        self.key_states = None

        # general
        self.button_size = [120, 20]
        self.selection_pos = (0, 0)
        self.selection_indicator = None

        self.level_selection = 'spring' # number representing dictionary key in level selector
        self.out_transition = Transition(1000, 255, groups = self.sprites)
        self.in_transition = Transition(2000, 0, groups = self.sprites)

        for name, scene in bg_frames.items():
            bg_frames[name] = [pygame.transform.scale(image, (GAME_WIDTH + 40, GAME_HEIGHT + 40)) for image in bg_frames[name]]
        self.bg_frames = bg_frames

        self.music[f'{self.level_selection}_bgm'].play(-1)
        self.setup(ui_frames["menu"])

    def setup(self, ui_frames):
        Sprite((20, -5), ui_frames["title"][0], (self.sprites, self.graphic_sprites), 99)
        Text((30, 92), "Ve rdant Begi nni ngs", 11, groups = self.text_sprites)
        Text((30, 132), "Frosted Path", 11, groups = self.text_sprites)
        Text((30, 172), "Cri mson Desolation", 11, groups = self.text_sprites)

        ui_frames["level_selection"][0] = pygame.transform.scale(ui_frames["level_selection"][0], self.button_size)
        Button('spring', (20, 100), ui_frames["level_selection"][0], (self.sprites, self.button_sprites))
        Button('winter', (20, 140), ui_frames["level_selection"][0], (self.sprites, self.button_sprites))
        Button('desert', (20, 180), ui_frames["level_selection"][0], (self.sprites, self.button_sprites))
        Button('quit', (400, 20), ui_frames["quit"][0], (self.sprites, self.button_sprites))

        self.selection_pos = (20 + self.button_size[0] / 2, 100)
        self.selection_indicator = SelectionIndicator(self.selection_pos, self.button_size, 5,(self.sprites, self.graphic_sprites), 1)

        graphic = pygame.Surface((170, GAME_WIDTH), pygame.SRCALPHA); graphic.fill((0, 0, 0, 127))
        Sprite((0, 0), graphic, (self.sprites, self.graphic_sprites), 0)

        self.update_bg()

    def check_states(self):
        for button in self.button_sprites:
            if button.pressed and not self.timers['button_click'].active and not self.out_transition.active:
                if self.level_selection == button.tag:
                    self.out_transition.start()
                else:
                    if self.level_selection != button.tag and button.tag != 'quit':
                        pygame.mixer.stop()
                        self.music[f'{button.tag}_bgm'].play(-1)

                    self.level_selection = button.tag
                    self.selection_pos = button.rect.center
                self.timers['button_click'].activate()

        if self.level_selection == 'quit':
            pygame.quit()
            sys.exit()

    def input(self):
        self.mouse_pos = [axis / SCALE_FACTOR for axis in pygame.mouse.get_pos()]
        self.mouse_states = pygame.mouse.get_pressed()
        self.key_states = pygame.key.get_pressed()

    def update_bg(self):
        self.bg_sprites.empty()
        for frame in range(len(self.bg_frames[self.level_selection])):
            Sprite((0, 0), self.bg_frames[self.level_selection][frame], (self.sprites, self.bg_sprites), frame)

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def run(self, dt):
        self.update_timers()

        self.input()
        self.sprites.update(dt,
            selection_pos = self.selection_pos,
            mouse_pos = self.mouse_pos,
            mouse_states = self.mouse_states,
            key_states = self.key_states,
        )
        self.check_states()
        self.update_bg()

        self.bg_sprites.draw(self.display_surf, self.mouse_pos)
        self.graphic_sprites.draw(self.display_surf)
        self.button_sprites.draw(self.display_surf)
        self.text_sprites.draw(self.display_surf, (0, GAME_HEIGHT))

        self.in_transition.draw(self.display_surf)
        self.out_transition.draw(self.display_surf)
