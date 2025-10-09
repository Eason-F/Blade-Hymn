from constants import *
from sprite import Sprite, Transition
from groups import MenuSprites, ParallaxSprites
from ui import Button, SelectionIndicator
from timer import Timer

class MainMenu:
    def __init__(self, bg_frames, ui_frames):
        self.display_surf = MASTER_DISPLAY

        # groups
        self.sprites = pygame.sprite.Group()
        self.bg_sprites = ParallaxSprites()
        self.button_sprites = pygame.sprite.Group()
        self.graphic_sprites = MenuSprites()

        self.timers = {
            "button_click": Timer(200, sustained=True)
        }

        # input
        self.mouse_pos = (0, 0)
        self.mouse_states = None
        self.key_states = None

        # general
        self.button_size = [100, 20]
        self.selection_pos = (0, 0)
        self.selection_indicator = None

        self.level_selection = 'spring' # number representing dictionary key in level selector
        self.out_transition = Transition(1000, 255, groups = self.sprites)
        self.in_transition = Transition(2000, 0, groups = self.sprites)

        for name, scene in bg_frames.items():
            bg_frames[name] = [pygame.transform.scale(image, (GAME_WIDTH + 40, GAME_HEIGHT + 40)) for image in bg_frames[name]]
        self.bg_frames = bg_frames

        self.setup(ui_frames)

    def setup(self, ui_frames):
        Button('spring', (20, 100), pygame.Surface(self.button_size), (self.sprites, self.button_sprites))
        Button('desert', (20, 130), pygame.Surface(self.button_size), (self.sprites, self.button_sprites))
        Button('winter', (20, 160), pygame.Surface(self.button_size), (self.sprites, self.button_sprites))

        self.selection_pos = (20 + self.button_size[0] / 2, 100)
        self.selection_indicator = SelectionIndicator(self.selection_pos, self.button_size, 5,(self.sprites, self.graphic_sprites), 1)

        graphic = pygame.Surface((150, GAME_WIDTH), pygame.SRCALPHA); graphic.fill((0, 0, 0, 127))
        Sprite((0, 0), graphic, (self.sprites, self.graphic_sprites), 0)

        self.update_bg()

    def check_states(self):
        for button in self.button_sprites:
            if button.pressed and not self.timers['button_click'].active and not self.out_transition.active:
                if self.level_selection == button.tag:
                    self.out_transition.start()
                else:
                    self.level_selection = button.tag
                    self.selection_pos = button.rect.center
                self.timers['button_click'].activate()

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

        self.in_transition.draw(self.display_surf)
        self.out_transition.draw(self.display_surf)
