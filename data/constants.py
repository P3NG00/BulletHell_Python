import random
from math import cos
from math import pi
from math import sin
from pygame import Color
from pygame import Vector2
from pygame.font import Font

""" constant game values """

def seconds_to_frames(seconds: float) -> int:
    """returns the amount of frames in the given amount of seconds"""
    return int(FPS * seconds)

def make_framerate_independent(value: float) -> float:
    """returns the value in frames per second"""
    return value / FPS

def random_vector() -> Vector2:
    """returns a unit vector with a random direction"""
    random_angle = random.uniform(0, 2 * pi)
    return Vector2(cos(random_angle), sin(random_angle))

def create_font(size: int) -> Font:
    """creates a font object of specified size"""
    return Font(FONT_FILE, size)

# window properties
SURFACE_SIZE = Vector2(1280, 720)
SURFACE_CENTER = SURFACE_SIZE / 2
TITLE = "Python Game"
FPS = 65.0

# camera
CAMERA_SPEED = make_framerate_independent(3)

# text
TEXT_GAME_OVER = "GAME OVER"
TEXT_PAUSE = "Paused"
TEXT_RESTART = "Press SPACE to restart..."

# ui
DEBUG_LINE_WIDTH = 2
UI_BORDER_OFFSET = 15
AIM_LINE_LENGTH = 40
AIM_LINE_WIDTH = 3

# font file
FONT_FILE = "data/upheavtt.ttf"

# colors
AIM_LINE_COLOR = Color(255, 255, 255)
BULLET_COLOR = Color(0, 128, 255)
DEBUG_LINE_COLOR = Color(255, 64, 128)
ENEMY_COLOR = Color(64, 255, 16)
PAUSE_OVERLAY_COLOR = Color(0, 0, 0, 192)
PLAYER_COLOR = Color(0, 255, 255)

# player
PLAYER_I_FRAMES = seconds_to_frames(3)
PLAYER_LIFE = 3
PLAYER_RADIUS = 16.0
PLAYER_SPEED = 200.0

# bullet
BULLET_LIFE = seconds_to_frames(1)
BULLET_RADIUS = 8.0
BULLET_SPEED = 450.0

# enemy
ENEMY_LIFE = 3
ENEMY_RADIUS = 24.0
ENEMY_SPAWN_DISTANCE = SURFACE_SIZE.magnitude()
ENEMY_DESPAWN_DISTANCE = ENEMY_SPAWN_DISTANCE * 1.1
ENEMY_DESPAWN_RATE = seconds_to_frames(15)
ENEMY_SPAWN_RATE = seconds_to_frames(1.25)
ENEMY_SPEED = 150.0
ENEMY_TRACKING = make_framerate_independent(1.5)
