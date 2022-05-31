import pygame as pg
from abc import ABC
from abc import abstractmethod
from .constants import BULLET_COLOR
from .constants import BULLET_LIFE
from .constants import BULLET_RADIUS
from .constants import BULLET_SPEED
from .constants import ENEMY_COLOR
from .constants import ENEMY_LIFE
from .constants import ENEMY_RADIUS
from .constants import ENEMY_SPEED
from .constants import FPS
from .constants import MILLISEC_IN_SEC as MS
from .constants import PLAYER_COLOR
from .constants import PLAYER_RADIUS
from .constants import PLAYER_SPEED
from .util import normalize
from .util import subtract


# abstract class
class GameObject(ABC):
    """in-game objects"""

    @abstractmethod
    def __init__(self, pos, radius, speed, color, life=None):
        self.pos = pos
        self.radius = radius
        self.speed = speed
        self.color = color
        self.life = life

    def is_alive(self):
        return self.life > 0.0

    @abstractmethod
    def update(self, extra_info=None):
        """moves the game object with its direction"""
        for i in range(2):
            self.pos[i] += (self.direction[i] * self.speed) / FPS

    def draw(self, surface):
        """draws the object to the surface"""
        pg.draw.circle(surface, self.color, self.pos, self.radius)

    # TODO create method to check if object is touching another object


class Player(GameObject):
    """player game object"""

    def __init__(self, pos):
        super().__init__(pos, PLAYER_RADIUS, PLAYER_SPEED, PLAYER_COLOR)

    def update(self, input):
        """used to handle movement input"""
        # normalize input vector
        self.direction = normalize(input)
        # update movement this frame
        super().update()


class Bullet(GameObject):
    """bullet game object"""

    def __init__(self, pos, direction):
        super().__init__(pos, BULLET_RADIUS, BULLET_SPEED,
                         BULLET_COLOR, float(BULLET_LIFE * MS))
        self.direction = direction

    # the 'extra_info' is kept so that one 'update' method exists with same parameters
    def update(self, extra_info=None):
        self.life -= MS / FPS
        super().update()


class Enemy(GameObject):
    """enemy game object"""

    def __init__(self, pos):
        super().__init__(pos, ENEMY_RADIUS, ENEMY_SPEED, ENEMY_COLOR, ENEMY_LIFE)

    def update(self, player_pos):
        """moves the enemy towards the player"""
        # move towards player position
        self.direction = normalize(subtract(player_pos, self.pos))
        # TODO check if collided with bullet and lose health
        super().update()
