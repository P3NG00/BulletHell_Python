from pygame import Color
from pygame import Vector2

""" constant game values """

def seconds_to_frames(seconds: float) -> int:
    """returns the amount of frames in the given amount of seconds"""
    return int(FPS * seconds)

# window properties
SURFACE_SIZE = Vector2(1280, 720)
SURFACE_CENTER = SURFACE_SIZE / 2
TITLE = "Python Game"
FPS = 65.0

# colors
AIM_LINE_COLOR = Color(255, 255, 255)
BULLET_COLOR = Color(0, 128, 255)
ENEMY_COLOR = Color(64, 255, 16)
PAUSE_OVERLAY_COLOR = Color(0, 0, 0, 192)  # with alpha value
PLAYER_COLOR = Color(0, 255, 255)

# player
PLAYER_I_FRAMES = seconds_to_frames(3)
PLAYER_LIFE = 3  # hits before game over
PLAYER_RADIUS = 16.0
PLAYER_SPEED = 200.0

# bullet
BULLET_LIFE = seconds_to_frames(1)
BULLET_RADIUS = 8.0
BULLET_SPEED = 450.0

# enemy
ENEMY_LIFE = 3  # in hits before death
ENEMY_RADIUS = 16.0
ENEMY_SPAWN_DISTANCE = SURFACE_SIZE.magnitude()
ENEMY_SPAWN_RATE = seconds_to_frames(1.25)
ENEMY_SPEED = 150.0
ENEMY_TRACKING = 0.04
