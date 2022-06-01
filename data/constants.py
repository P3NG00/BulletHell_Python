from pygame import Color
from pygame import Vector2

""" constant game values """

# window properties
SURFACE_SIZE = Vector2(1280, 720)
TITLE = "Python Game"
FPS = 65.0

# game values
BACKGROUND_COLOR = Color(32, 32, 32)
BULLET_COLOR = Color(0, 128, 255)
BULLET_LIFE = 1.0  # in seconds
BULLET_RADIUS = 4.0
BULLET_SPEED = 450.0
DEBUG_FONT_COLOR = Color(64, 64, 64)
ENEMY_COLOR = Color(255, 0, 0)
ENEMY_LIFE = 1.0
ENEMY_RADIUS = 12.0
ENEMY_SPEED = 100.0
FONT_FILE = "data/upheavtt.ttf"
FONT_SIZE = 24
GAME_OVER_FONT_COLOR = Color(255, 0, 0)
PAUSE_FONT_COLOR = Color(255, 255, 255)
PAUSE_OVERLAY_COLOR = Color(0, 0, 0)
PAUSE_OVERLAY_ALPHA = 192
PLAYER_COLOR = Color(0, 255, 255)
PLAYER_LIFE = 3
PLAYER_RADIUS = 16.0
PLAYER_SPEED = 200.0
RESTART_FONT_COLOR = Color(192, 192, 192)

# math
MILLISEC_IN_SEC = 1000.0
