import pygame as pg
from pygame.math import Vector2
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
from .constants import FRAME_TIME
from .constants import PLAYER_COLOR
from .constants import PLAYER_LIFE
from .constants import PLAYER_RADIUS
from .constants import PLAYER_SPEED


# abstract class
class GameObject(ABC):
    """in-game objects"""

    @abstractmethod
    def __init__(self, pos: Vector2, radius: float, speed: float, color: pg.Color, life: float = None):
        self.pos = pos
        self.radius = radius
        self.speed = speed
        self.color = color
        self.life = life
        self.direction = Vector2(0)

    def is_alive(self):
        """returns if the game object has life remaining"""
        return self.life > 0.0

    def update(self):
        """moves the game object with its direction"""
        self.pos += (self.direction * self.speed) / FPS

    def draw(self, surface: pg.Surface, camera_offset: Vector2):
        """draws the object to the surface"""
        pg.draw.circle(surface, self.color, self.pos -
                       camera_offset, self.radius)

    def is_touching(self, other):
        return (self.pos - other.pos).magnitude() < self.radius + other.radius


class Player(GameObject):
    """player game object"""

    def __init__(self, pos: Vector2):
        super().__init__(pos, PLAYER_RADIUS, PLAYER_SPEED, PLAYER_COLOR, PLAYER_LIFE)

    def update(self, input: Vector2):
        """used to handle movement input"""
        # normalize input vector
        self.direction = input
        if self.direction.is_normalized():
            self.direction = self.direction.normalize()
        # update movement this frame
        super().update()


class Bullet(GameObject):
    """bullet game object"""

    def __init__(self, pos: Vector2, direction: Vector2):
        super().__init__(pos, BULLET_RADIUS, BULLET_SPEED, BULLET_COLOR, BULLET_LIFE)
        self.direction = direction

    def update(self):
        self.life -= FRAME_TIME
        super().update()


class Enemy(GameObject):
    """enemy game object"""

    def __init__(self, pos: Vector2):
        super().__init__(pos, ENEMY_RADIUS, ENEMY_SPEED, ENEMY_COLOR, ENEMY_LIFE)

    def update(self, player: Player):
        """moves the enemy towards the player"""
        # move towards player position
        self.direction = (player.pos - self.pos).normalize()
        # check player collision
        if self.is_touching(player):
            self.life = 0
            player.life -= 1
        super().update()
