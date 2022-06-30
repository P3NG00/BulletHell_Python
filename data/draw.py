from math import atan2
from math import cos
from math import sin
from pygame import Color
from pygame import Surface
from pygame import Vector2
from pygame.draw import circle as draw_circle
from pygame.draw import line as draw_line
from pygame.gfxdraw import aacircle as draw_aa_circle
from pygame.gfxdraw import aapolygon as draw_aa_polygon
from pygame.gfxdraw import filled_circle as draw_filled_circle
from pygame.gfxdraw import filled_polygon as draw_filled_polygon
from typing import Sequence
from .constants import CAMERA_SPEED
from .constants import DEBUG_LINE_WIDTH

class Draw:
    """draw functions"""

    def __init__(self):
        self.camera_offset = None
        self.anti_aliasing = False
        self._blit_info = []

    def update(self, surface: Surface, pos: Vector2, anti_aliasing: bool) -> None:
        """updates the draw object"""
        self.anti_aliasing = anti_aliasing
        # lerp camera offset towards player position
        self.camera_offset = self.camera_offset.lerp(pos - (Vector2(surface.get_size()) / 2), CAMERA_SPEED)

    def background(self, surface: Surface, tile: Surface) -> int:
        """draws background, returns amount of tiles drawn"""
        start_x = (-self.camera_offset.x % tile.get_width()) - tile.get_height()
        pos = Vector2(start_x, (-self.camera_offset.y % tile.get_height()) - tile.get_height())
        self._blit_info.clear()
        while pos.y < surface.get_height():
            while pos.x < surface.get_width():
                self._blit_info.append((tile, pos.copy()))
                pos.x += tile.get_width()
            pos.x = start_x
            pos.y += tile.get_height()
        surface.blits(self._blit_info)
        return len(self._blit_info)

    def circle(self, surface: Surface, color: Color, center: Vector2, radius: float) -> None:
        """draws a circle"""
        center = center - self.camera_offset
        if self.anti_aliasing:
            _aa_circle(surface, int(center.x), int(center.y), int(radius), color)
        else:
            draw_circle(surface, color, center, radius)

    def line(self, surface: Surface, color: Color, start: Vector2, direction: Vector2, length: float, width: float) -> None:
        """draws a line"""
        start = start - self.camera_offset
        self.line_no_offset(surface, color, start, direction, length, width)

    def line_no_offset(self, surface: Surface, color: Color, start: Vector2, direction: Vector2, length: float, width: float) -> None:
        """draws a line without using camera offset"""
        end = start + (direction * length)
        if self.anti_aliasing:
            center = (start + end) / 2
            half_length = (start - end).length() / 2
            half_thickness = DEBUG_LINE_WIDTH / 2
            angle = atan2(start.y - end.y, start.x - end.x)
            angle_cos = cos(angle)
            angle_sin = sin(angle)
            points = ((center.x + half_length * angle_cos - half_thickness * angle_sin,
                       center.y + half_thickness * angle_cos + half_length * angle_sin),
                      (center.x - half_length * angle_cos - half_thickness * angle_sin,
                       center.y + half_thickness * angle_cos - half_length * angle_sin),
                      (center.x - half_length * angle_cos + half_thickness * angle_sin,
                       center.y - half_thickness * angle_cos - half_length * angle_sin),
                      (center.x + half_length * angle_cos + half_thickness * angle_sin,
                       center.y - half_thickness * angle_cos + half_length * angle_sin))
            _aa_polygon(surface, points, color)
        else:
            draw_line(surface, color, start, end, width)

def _aa_circle(surface: Surface, x: int, y: int, radius: int, color: Color) -> None:
    draw_aa_circle(surface, x, y, radius, color)
    draw_filled_circle(surface, x, y, radius, color)

def _aa_polygon(surface: Surface, points: Sequence[tuple[float, float]], color: Color) -> None:
    draw_aa_polygon(surface, points, color)
    draw_filled_polygon(surface, points, color)
