import pygame
from math import sqrt
from .constants import VECTOR_DIAG_NORM as VDN
from .util import scale_fps


class GameObject:
    """in-game objects"""

    def __init__(self, pos, radius, speed, color):
        self.pos = pos
        self.radius = radius
        self.speed = speed
        self.color = color

    def draw(self, surface):
        """draws the object to the surface"""
        pygame.draw.circle(surface, self.color, self.pos, self.radius)

    def move(self, input_h, input_v):
        """moves the position of the player"""
        magnitude = sqrt((input_h ** 2) + (input_v ** 2))
        if magnitude > 1.0:
            if input_h < 0:
                input_h = -VDN
            else:
                input_h = VDN
            if input_v < 0:
                input_v = -VDN
            else:
                input_v = VDN
        self.pos[0] += scale_fps(input_h * self.speed)
        self.pos[1] -= scale_fps(input_v * self.speed)
