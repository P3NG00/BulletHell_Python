import sys
import pygame as pg
from pygame.math import Vector2
from data.constants import BACKGROUND_COLOR
from data.constants import BULLET_RADIUS
from data.constants import DEBUG_FONT_COLOR
from data.constants import FONT_FILE
from data.constants import FONT_SIZE
from data.constants import FPS
from data.constants import PAUSE_FONT_COLOR
from data.constants import PAUSE_OVERLAY_ALPHA
from data.constants import PAUSE_OVERLAY_COLOR
from data.constants import PLAYER_RADIUS
from data.constants import SURFACE_SIZE as SS
from data.constants import TITLE
from data.game_object import Bullet
from data.game_object import Enemy
from data.game_object import Player

"""main game script"""

# initialize pygame
pg.init()
# create main window with title
surface = pg.display.set_mode(SS)
pg.display.set_caption(TITLE)
# create font
font = pg.font.Font(FONT_FILE, FONT_SIZE)


def create_text_surface(text, color):
    """returns a surface with colored text"""
    return font.render(text, False, color)


# create pause overlay
surface_pause = pg.Surface(SS)
surface_pause.fill(PAUSE_OVERLAY_COLOR)
surface_pause.set_alpha(PAUSE_OVERLAY_ALPHA)
surface_pause_text = create_text_surface("Paused", PAUSE_FONT_COLOR)
# create game clock
clock = pg.time.Clock()
# game objects
obj = {
    "player": Player(SS / 2),
    "bullets": [],
    "enemies": []}
# movement input variables
input = Vector2(0)
# stats
stats = {
    "bullets": 10,
    "killed": 0}
# program states
program = {
    "running": True,
    "pause": False}

# loop
while program["running"]:

    # handle events
    for event in pg.event.get():
        match event.type:
            case pg.QUIT:
                # actions when window is closed
                program["running"] = False
            case pg.KEYDOWN:
                # actions for keydown events
                match event.key:
                    case pg.K_END:
                        program["running"] = False
                    case pg.K_PAGEDOWN:
                        pg.display.iconify()
                    # handle pause toggling
                    case pg.K_ESCAPE:
                        program["pause"] = not program["pause"]
                        if program["pause"]:
                            # draw pausing overlay
                            surface.blits([
                                (surface_pause, (0, 0)),
                                (surface_pause_text, ((
                                    SS.x / 2) - (surface_pause_text.get_width() / 2), (
                                    SS.y / 2) - (surface_pause_text.get_height() / 2)))])
                    # movement input
                    case pg.K_w:
                        input.y -= 1
                    case pg.K_s:
                        input.y += 1
                    case pg.K_a:
                        input.x -= 1
                    case pg.K_d:
                        input.x += 1
            case pg.KEYUP:
                # actions for keyup events
                match event.key:
                    # movement input
                    case pg.K_w:
                        input.y += 1
                    case pg.K_s:
                        input.y -= 1
                    case pg.K_a:
                        input.x += 1
                    case pg.K_d:
                        input.x -= 1
            case pg.MOUSEBUTTONDOWN:
                # actions for mouse button down events
                match event.button:
                    # left mouse button click
                    case 1:
                        if not program["pause"] and stats["bullets"] > 0:
                            # Calculate direction of bullet from player to mouse
                            mouse_pos = pg.mouse.get_pos()
                            start_pos = obj["player"].pos.copy()
                            direction = (mouse_pos - start_pos).normalize()
                            # make bullet start in front of player
                            start_offset = direction.normalize() * (PLAYER_RADIUS + BULLET_RADIUS)
                            start_pos += start_offset
                            # Create new bullet object
                            obj["bullets"].append(
                                Bullet(start_pos, direction))
                            stats["bullets"] -= 1
                    # right mouse button click
                    # TODO remove, only for debugging
                    case 3:
                        if not program["pause"]:
                            # create new enemy
                            obj["enemies"].append(
                                Enemy(Vector2(pg.mouse.get_pos())))

    # check pause
    if not program["pause"]:

        # TODO spawn enemies naturally
        # reset screen
        surface.fill(BACKGROUND_COLOR)
        # update game objects
        obj["player"].update(input)
        for enemy in obj["enemies"]:
            enemy.update(obj["player"])
        for bullet in obj["bullets"]:
            bullet.update()
            # check bullet collision
            for enemy in obj["enemies"]:
                # if bullet hits enemy
                if bullet.is_touching(enemy):
                    bullet.life = 0
                    enemy.life -= 1
                    # increment bullet and kill count
                    for stat in ["bullets", "killed"]:
                        stats[stat] += 1
        # remove dead game objects
        for obj_str in ["enemies", "bullets"]:
            obj[obj_str] = [go for go in obj[obj_str] if go.is_alive()]
        # draw game objects
        obj["player"].draw(surface)
        for obj_str in ["enemies", "bullets"]:
            for go in obj[obj_str]:
                go.draw(surface)
        # update ui info
        ui = [
            f"killed: {stats['killed']}",
            f"bullets: {stats['bullets']}",
            f"life: {obj['player'].life}"]
        current_height = SS.y
        # replace ui strings with its blit info
        for i in range(len(ui)):
            # create text surface from string
            debug_surface = create_text_surface(ui[i], DEBUG_FONT_COLOR)
            # move upwards from last height
            current_height -= debug_surface.get_height()
            # replace index with blit information
            ui[i] = (debug_surface, (2, current_height))
        # blit surfaces
        surface.blits(ui)

    # display surface
    pg.display.flip()
    # fps lock
    clock.tick(FPS)

# exit code
pg.quit()
sys.exit()
