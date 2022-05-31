import pygame as pg
from abc import ABC
from abc import abstractmethod
from .constants import BULLET_LIFE
from .constants import FPS
from .constants import MILLISEC_IN_SEC as MS
from .util import normalize


# abstract class
class GameObject(ABC):
    """in-game objects"""

    @abstractmethod
    def __init__(self, pos, radius, speed, color):
        self.pos = pos
        self.radius = radius
        self.speed = speed
        self.color = color

    def update(self):
        """moves the game object with its direction"""
        for i in range(2):
            self.pos[i] += (self.direction[i] * self.speed) / FPS

    def draw(self, surface):
        """draws the object to the surface"""
        pg.draw.circle(surface, self.color, self.pos, self.radius)


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


class Bullet(GameObject):
    """bullet game object"""

    def __init__(self, pos, radius, speed, color, direction):
        super().__init__(pos, radius, speed, color)
        self._life = float(BULLET_LIFE * MS)
        self.direction = direction

    def is_alive(self):
        return self._life > 0

    def update(self):
        self._life -= MS / FPS
        super().update()
