import pygame
from pygame import Color
from pygame import gfxdraw
from pygame import Surface
from pygame import Vector2

""" constant game values """

def seconds_to_frames(seconds: float) -> int:
    """returns the amount of frames in the given amount of seconds"""
    return int(FPS * seconds)

def make_framerate_independent(value: float) -> float:
    """returns the value in frames per second"""
    return value / FPS

# window properties
SURFACE_SIZE = Vector2(1280, 720)
SURFACE_CENTER = SURFACE_SIZE / 2
TITLE = "Python Game"
FPS = 65.0

# draw functions
def draw_circle(surface: Surface, color: Color, center: Vector2, radius: float, anti_aliasing: bool) -> None:
    """draws a circle"""
    if anti_aliasing:
        radius, x, y = int(radius), int(center.x), int(center.y)
        gfxdraw.aacircle(surface, x, y, radius, color)
        gfxdraw.filled_circle(surface, x, y, radius, color)
    else:
        pygame.draw.circle(surface, color, center, radius)

def draw_line(surface: Surface, color: Color, start: Vector2, end: Vector2, width: float, anti_aliasing: bool) -> None:
    """draws a line"""
    if anti_aliasing:
        # TODO https://stackoverflow.com/questions/30578068/pygame-draw-anti-aliased-thick-line
        pygame.draw.aaline(surface, color, start, end)
    else:
        pygame.draw.line(surface, color, start, end, width)

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
ENEMY_TRACKING = make_framerate_independent(0.5)
