import pygame as pg
from .constants import BULLET_LIFE
from .constants import FPS
from .util import normalize


class GameObject:
    """in-game objects"""

    def __init__(self, pos, radius, speed, color, direction=[0, 0]):
        # TODO fix, existing bullets still lose time while paused. change to variable that keeps 'life' that ticks down
        self._time_created = pg.time.get_ticks()
        self.pos = pos
        self.radius = radius
        self.speed = speed
        self.color = color
        self.direction = direction

    def update(self):
        """moves the game object with its direction"""
        self.pos[0] += (self.direction[0] * self.speed) / FPS
        self.pos[1] -= (self.direction[1] * self.speed) / FPS

    def draw(self, surface):
        """draws the object to the surface"""
        pg.draw.circle(surface, self.color, self.pos, self.radius)

    def is_alive(self):
        return (pg.time.get_ticks() - self._time_created) < (BULLET_LIFE * 1000)


class Player(GameObject):
    """player game object"""

    def __init__(self, pos, radius, speed, color):
        super().__init__(pos, radius, speed, color)

    def update(self, input):
        """used to handle movement input"""
        # normalize input vector
        self.direction = normalize(input)
        # update movement this frame
        super().update()
