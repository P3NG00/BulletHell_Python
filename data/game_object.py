from pygame import Color
from pygame.math import Vector2
from abc import ABC
from abc import abstractmethod
from .constants import BULLET_COLOR
from .constants import BULLET_LIFE
from .constants import BULLET_RADIUS
from .constants import BULLET_SPEED
from .constants import DEBUG_LINE_COLOR
from .constants import DEBUG_LINE_WIDTH
from .constants import ENEMY_COLOR
from .constants import ENEMY_LIFE
from .constants import ENEMY_RADIUS
from .constants import ENEMY_SPEED
from .constants import ENEMY_TRACKING
from .constants import make_framerate_independent
from .constants import PLAYER_COLOR
from .constants import PLAYER_I_FRAMES
from .constants import PLAYER_LIFE
from .constants import PLAYER_RADIUS
from .constants import PLAYER_SPEED
from .draw import Draw

class GameObject(ABC):
    """abstract game object"""

    @abstractmethod
    def __init__(self, pos: Vector2, radius: int, speed: float, color: Color, life: float = None, direction: Vector2 = Vector2(0)):
        self.pos = pos
        self.radius = radius
        self.speed = speed
        self.color = color
        self.direction = direction
        self._life = life

    def is_alive(self) -> bool:
        """returns if the game object has life remaining"""
        return self._life > 0

    def damage(self, amount: int = 1) -> None:
        """reduces the object's life"""
        self._life -= amount

    def kill(self) -> None:
        """instantly kills the game object"""
        self._life = 0

    def update(self) -> None:
        """moves the game object with its direction"""
        self.pos += make_framerate_independent(self.direction * self.speed)

    def draw(self, draw: Draw, draw_direction: bool) -> None:
        """draws the object to the surface"""
        if self.is_alive():
            draw.circle(self.color, self.pos, self.radius)
            if draw_direction:
                draw.line(DEBUG_LINE_COLOR, self.pos, self.direction, self.radius, DEBUG_LINE_WIDTH)

    def is_touching(self, other: 'GameObject') -> bool:
        """returns if this gameobject is touching the other gameobject"""
        return (self.pos - other.pos).magnitude() < self.radius + other.radius

class Player(GameObject):
    """player game object"""

    def __init__(self, pos: Vector2):
        super().__init__(pos, PLAYER_RADIUS, PLAYER_SPEED, PLAYER_COLOR, PLAYER_LIFE)
        self.i_frames = 0

    def is_vulnerable(self) -> bool:
        """returns if the player can take damage"""
        return self.i_frames == 0

    def damage(self, amount: int = 1) -> None:
        """reduces the player's life and starts i-frames"""
        if self.is_vulnerable():
            self.i_frames = PLAYER_I_FRAMES
            super().damage(amount)

    def update(self, input: Vector2) -> None:
        """used to handle movement input"""
        # handle i-frames
        if not self.is_vulnerable():
            self.i_frames -= 1
        # normalize input vector
        self.direction = input
        if self.direction.length() != 0.0 and not self.direction.is_normalized():
            self.direction = self.direction.normalize()
        # update movement this frame
        super().update()

    def draw(self, draw: Draw, draw_direction: bool) -> None:
        """draws the player. if damaged, draw every other frame"""
        if self.i_frames % 2 == 0:
            super().draw(draw, draw_direction)

class Bullet(GameObject):
    """bullet game object"""

    def __init__(self, pos: Vector2, direction: Vector2):
        super().__init__(pos, BULLET_RADIUS, BULLET_SPEED, BULLET_COLOR, BULLET_LIFE, direction)

    def update(self) -> None:
        # tick life
        self.damage()
        # update movement this frame
        super().update()

class Enemy(GameObject):
    """enemy game object"""

    def __init__(self, pos: Vector2):
        super().__init__(pos, ENEMY_RADIUS, ENEMY_SPEED, ENEMY_COLOR, ENEMY_LIFE)

    def update(self, player: Player) -> None:
        """moves the enemy towards the player"""
        # move towards player position
        self.direction = self.direction.lerp(
            (player.pos - self.pos).normalize(), ENEMY_TRACKING)
        # update movement this frame
        super().update()
        # check player collision
        if test_collision(self, player):
            player.damage()

def test_collision(obj_1: GameObject, obj_2: GameObject) -> bool:
    """if objects collide, reposition. returns if collided"""
    if obj_1 is not obj_2 and obj_1.is_touching(obj_2):
        # reposition self
        obj_1.pos = obj_2.pos - (obj_2.pos - obj_1.pos).normalize() * (obj_1.radius + obj_2.radius)
        return True
    return False
