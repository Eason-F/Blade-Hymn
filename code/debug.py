from constants import *

pygame.init()
font = pygame.font.Font(None, 15)

def debug(info, y = 10, x = 10):
    debug_surf = font.render(str(info), True, 'white')
    debug_rect = debug_surf.get_rect(topleft = (x, y))
    pygame.draw.rect(MASTER_DISPLAY, 'black', debug_rect)
    MASTER_DISPLAY.blit(debug_surf, debug_rect)