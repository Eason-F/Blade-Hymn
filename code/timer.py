from constants import *

class Timer:
    def __init__(self, duration, auto_start = False, repeat = False, sustained = False):
        self.duration = duration
        self.repeat = repeat
        self.sustained = sustained

        self.activated = False

        self.active = False
        self.start_time = 0
        if auto_start:
            self.activate()

        self.time = 0

    def activate(self):
        self.activated = True
        self.start_time = pygame.time.get_ticks()
        if self.sustained:
            self.active = True

    def deactivate(self):
        self.activated = False
        if self.sustained:
            self.active = False

    def update(self):
        if not self.sustained:
            self.active = False

        current_time = pygame.time.get_ticks()
        self.time = current_time - self.start_time
        if self.activated:
            if self.time >= self.duration:
                self.active = True

                if self.repeat:
                    self.activate()
                else:
                    self.deactivate()