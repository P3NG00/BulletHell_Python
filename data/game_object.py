import pygame as pg
from math import sqrt
from .constants import FPS
from .constants import VECTOR_DIAG_NORM as VDN


class GameObject:
    """in-game objects"""

    def __init__(self, pos, radius, speed, color):
        self.pos = pos
        self.radius = radius
        self.speed = speed
        self.color = color

    def update(self, input):
        """used to handle movement input"""
        move_h, move_v = input[0], input[1]
        # normalize input vector
        if sqrt((input[0] ** 2) + (input[1] ** 2)) > 1.0:
            move_h = input[0] * VDN
            move_v = input[1] * VDN
        # update movement this frame
        self.pos[0] += (move_h * self.speed) / FPS
        self.pos[1] -= (move_v * self.speed) / FPS

    def draw(self, surface):
        """draws the object to the surface"""
        pg.draw.circle(surface, self.color, self.pos, self.radius)
