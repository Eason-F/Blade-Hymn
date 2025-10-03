from constants import *

class Timer:
    def __init__(self, duration, auto_start = False, repeat = False, sustained = False):
        self.duration = duration
        self.repeat = repeat
        self.sustained = sustained

        self.active = False
        self.start_time = 0
        if auto_start:
            self.activate()

    def activate(self):
        self.start_time = pygame.time.get_ticks()
        if self.sustained:
            self.active = True

    def deactivate(self):
        self.start_time = 0
        if self.sustained:
            self.active = False

    def update(self):
        if not self.sustained:
            self.active = False

        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.duration:
            self.active = True

            if self.repeat:
                self.activate()
            else:
                self.deactivate()