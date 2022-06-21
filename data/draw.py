import pygame
from pygame import Color
from pygame import gfxdraw
from pygame import Surface
from pygame import Vector2
from .constants import CAMERA_SPEED
from .constants import SURFACE_CENTER
from .constants import SURFACE_SIZE

class Draw:
    """draw functions"""

    def __init__(self, surface: Surface, tile: Surface):
        self.surface = surface
        self.tile = tile
        self.tile_size = Vector2(tile.get_size())
        self.camera_offset = None
        self.anti_aliasing = False
        self._blit_info = []

    def update(self, pos: Vector2, anti_aliasing: bool) -> None:
        """updates the draw object"""
        self.anti_aliasing = anti_aliasing
        # lerp camera offset towards player position
        self.camera_offset = self.camera_offset.lerp(pos - SURFACE_CENTER, CAMERA_SPEED)

    def background(self) -> None:
        """draws background"""
        # blit background tiles
        start_x = (-self.camera_offset.x % self.tile_size.x) - self.tile_size.x
        current_pos = Vector2(start_x, (-self.camera_offset.y % self.tile_size.y) - self.tile_size.y)
        self._blit_info.clear()
        while current_pos.y < SURFACE_SIZE.y:
            while current_pos.x < SURFACE_SIZE.x:
                self._blit_info.append((self.tile, current_pos.copy()))
                current_pos.x += self.tile_size.x
            current_pos.x = start_x
            current_pos.y += self.tile_size.y
        self.surface.blits(self._blit_info)

    def circle(self, color: Color, center: Vector2, radius: float) -> None:
        """draws a circle"""
        # make copy of position and add offset
        center = center.copy() - self.camera_offset
        if self.anti_aliasing:
            radius, x, y = int(radius), int(center.x), int(center.y)
            gfxdraw.aacircle(self.surface, x, y, radius, color)
            gfxdraw.filled_circle(self.surface, x, y, radius, color)
        else:
            pygame.draw.circle(self.surface, color, center, radius)

    def line(self, color: Color, start: Vector2, direction: Vector2, length: float, width: float) -> None:
        """draws a line"""
        # make copy of position and add offset
        start = start.copy() - self.camera_offset
        end = start + (direction * length)
        if self.anti_aliasing:
            # TODO https://stackoverflow.com/questions/30578068/pygame-draw-anti-aliased-thick-line
            pygame.draw.aaline(self.surface, color, start, end)
        else:
            pygame.draw.line(self.surface, color, start, end, width)
