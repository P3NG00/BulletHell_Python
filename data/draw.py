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
from .constants import CAMERA_SPEED
from .constants import DEBUG_LINE_WIDTH
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

    def background(self) -> int:
        """draws background, returns amount of tiles drawn"""
        # blit background tiles
        start_x = (-self.camera_offset.x % self.tile_size.x) - self.tile_size.x
        pos = Vector2(start_x, (-self.camera_offset.y % self.tile_size.y) - self.tile_size.y)
        self._blit_info.clear()
        while pos.y < SURFACE_SIZE.y:
            while pos.x < SURFACE_SIZE.x:
                self._blit_info.append((self.tile, pos.copy()))
                pos.x += self.tile_size.x
            pos.x = start_x
            pos.y += self.tile_size.y
        self.surface.blits(self._blit_info)
        return len(self._blit_info)

    def circle(self, color: Color, center: Vector2, radius: float) -> None:
        """draws a circle"""
        center = center - self.camera_offset
        if self.anti_aliasing:
            self._aa_circle(int(center.x), int(center.y), int(radius), color)
        else:
            draw_circle(self.surface, color, center, radius)

    def line(self, color: Color, start: Vector2, direction: Vector2, length: float, width: float) -> None:
        """draws a line"""
        start = start - self.camera_offset
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
            self._aa_polygon(points, color)
        else:
            draw_line(self.surface, color, start, end, width)

    def _aa_circle(self, x: int, y: int, radius: int, color: Color) -> None:
        draw_aa_circle(self.surface, x, y, radius, color)
        draw_filled_circle(self.surface, x, y, radius, color)

    def _aa_polygon(self, points, color: Color) -> None:
        draw_aa_polygon(self.surface, points, color)
        draw_filled_polygon(self.surface, points, color)
