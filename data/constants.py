import pygame as pg
from enum import Enum
from pygame.font import Font
from pygame.image import load as load_image
from pygame import Color
from pygame import Vector2

""" constant game values """


# font types
class FontType(Enum):
    """font types"""
    NORMAL = 0
    UI = 1
    GAMEOVER = 2


def create_font(size: int):
    """creates a font object of specified size"""
    return Font(FONT_FILE, size)


# window properties
SURFACE_SIZE = Vector2(1280, 720)
SURFACE_CENTER = SURFACE_SIZE / 2
TITLE = "Python Game"
FPS = 65.0
FRAME_TIME = 1000.0 / FPS  # in milliseconds

# game values
START_BULLETS = 10
START_ENEMY_AMOUNT = 3
START_ENEMY_DISTANCE = 0.55
START_ENEMY_INCREMENT = 0.1

# fonts
pg.font.init()
FONT_FILE = "data/upheavtt.ttf"
FONTS = {FontType.NORMAL: create_font(24),
         FontType.UI: create_font(16),
         FontType.GAMEOVER: create_font(64)}
GAMEOVER_FONT_COLOR = Color(255, 0, 0)
PAUSE_FONT_COLOR = Color(255, 255, 255)
RESTART_FONT_COLOR = Color(128, 128, 128)
UI_FONT_COLOR = Color(192, 192, 192)

# colors
BULLET_COLOR = Color(0, 128, 255)
ENEMY_COLOR = Color(255, 0, 0)
PAUSE_OVERLAY_COLOR = Color(0, 0, 0, 192)  # with alpha value
PLAYER_COLOR = Color(0, 255, 255)

# tile
TILE = load_image("data/tile.png")
TILE_SIZE = Vector2(TILE.get_size())
TILE_CENTER = TILE_SIZE / 2

# camera
CAMERA_SPEED = 0.035

# ui
UI_BORDER_OFFSET = 15

# bullet
BULLET_LIFE = 1000.0  # in milliseconds
BULLET_RADIUS = 4.0
BULLET_SPEED = 450.0

# enemy
ENEMY_LIFE = 1.0
ENEMY_RADIUS = 12.0
ENEMY_SPAWN_DISTANCE = SURFACE_SIZE.magnitude()
ENEMY_SPAWN_RATE = 1250  # in milliseconds
ENEMY_SPEED = 150.0

# player
PLAYER_LIFE = 3  # hits before game over
PLAYER_RADIUS = 16.0
PLAYER_SPEED = 200.0
