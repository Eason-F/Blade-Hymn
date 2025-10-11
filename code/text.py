from settings import *
from pygame.key import name

TEXT_TAGS = {
    "intro": {
        "movement": f"Move with {name(RIGHT_KEY)} and {name(LEFT_KEY)}.",
        "jump": f"Jumping ({name(JUMP_KEY)}) \ncan be used to travel vertically.",
        "dash": f"Dashing ({name(DASH_KEY)}) can be \nused to travel long distances \nand gain damage invulnerability. \n\nA dash consumes a token \nthat regenerates over time.",
        "attack": f"Attack with '{name(ATTACK_KEY)}'.",
        "air_attack": f"Attacking in the air can \nprovide a vertical boost.",
        "heal": f"When damage is taken, '{name(HEAL_KEY)}' can heal you \nand consume a heal charge.",
        "level_end": "To end the level, all enemies must be defeated..."
    }
}