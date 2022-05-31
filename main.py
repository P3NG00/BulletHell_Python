import sys
import pygame as pg
from data.constants import BACKGROUND_COLOR
from data.constants import BULLET_COLOR
from data.constants import BULLET_RADIUS
from data.constants import BULLET_SPEED
from data.constants import DEBUG_FONT_COLOR
from data.constants import FONT_FILE
from data.constants import FONT_SIZE
from data.constants import FPS
from data.constants import PAUSE_FONT_COLOR
from data.constants import PAUSE_OVERLAY_ALPHA
from data.constants import PAUSE_OVERLAY_COLOR
from data.constants import PLAYER_COLOR
from data.constants import PLAYER_RADIUS
from data.constants import PLAYER_SPEED
from data.constants import SURFACE_SIZE as SS
from data.constants import TITLE
from data.game_object import Bullet
from data.game_object import Player
from data.util import normalize
from data.util import subtract

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
# create player
player = Player([SS[0] / 2, SS[1] / 2], PLAYER_RADIUS,
                PLAYER_SPEED, PLAYER_COLOR)
# create list of current game objects
game_objects = []
# movement input variables
input = [0, 0]
# program running and pause states
running, pause = True, False

# loop
while running:

    # handle events
    for event in pg.event.get():
        match event.type:
            case pg.QUIT:
                # actions when window is closed
                running = False
            case pg.KEYDOWN:
                # actions for keydown events
                match event.key:
                    case pg.K_END:
                        running = False
                    case pg.K_PAGEDOWN:
                        pg.display.iconify()
                    # handle pause toggling
                    case pg.K_ESCAPE:
                        pause = not pause
                        if pause:
                            # draw pausing overlay
                            pause_font_left = (
                                SS[0] / 2) - (surface_pause_text.get_width() / 2)
                            pause_font_top = (
                                SS[1] / 2) - (surface_pause_text.get_height() / 2)
                            surface.blits([
                                (surface_pause, (0, 0)),
                                (surface_pause_text, (pause_font_left, pause_font_top))])
                    # movement input
                    case pg.K_w:
                        input[1] -= 1
                    case pg.K_s:
                        input[1] += 1
                    case pg.K_a:
                        input[0] -= 1
                    case pg.K_d:
                        input[0] += 1
            case pg.KEYUP:
                # actions for keyup events
                match event.key:
                    # movement input
                    case pg.K_w:
                        input[1] += 1
                    case pg.K_s:
                        input[1] -= 1
                    case pg.K_a:
                        input[0] += 1
                    case pg.K_d:
                        input[0] -= 1
            case pg.MOUSEBUTTONDOWN:
                # actions for mouse button down events
                match event.button:
                    # left mouse button click
                    case 1:
                        if not pause:
                            # Calculate direction of bullet from player to mouse
                            mouse_pos = pg.mouse.get_pos()
                            start_pos = player.pos.copy()
                            direction = normalize(
                                subtract(mouse_pos, start_pos))
                            # make bullet start in front of player
                            start_offset = normalize(
                                direction, PLAYER_RADIUS + BULLET_RADIUS)
                            for i in range(2):
                                start_pos[i] += start_offset[i]
                            # Create new bullet object
                            game_objects.append(
                                Bullet(start_pos, BULLET_RADIUS, BULLET_SPEED, BULLET_COLOR, direction))

    # check pause
    if not pause:
        # reset screen
        surface.fill(BACKGROUND_COLOR)
        # update game objects
        player.update(input)
        for go in game_objects:
            go.update()
        # remove dead game objects
        game_objects = [go for go in game_objects if go.is_alive()]
        # draw game objects
        player.draw(surface)
        for go in game_objects:
            go.draw(surface)
        # display info on screen
        debug_prints = [
            f"move_x: {input[0]}",
            f"move_y: {input[1]}",
            f"pos_x: {player.pos[0]:.2f}",
            f"pos_y: {player.pos[1]:.2f}",
            f"objs: {len(game_objects)}"]
        # get current screen height
        current_height = SS[1]
        # use each string in the array to create a surface
        for i in range(len(debug_prints)):
            # create text surface from string
            debug_surface = create_text_surface(
                debug_prints[i], DEBUG_FONT_COLOR)
            # move upwards from last height
            current_height -= debug_surface.get_height()
            # replace index with blit information
            debug_prints[i] = (debug_surface, (2, current_height))
        # blit surfaces
        surface.blits(debug_prints)

    # display surface
    pg.display.flip()
    # fps lock
    clock.tick(FPS)

# exit code
pg.quit()
sys.exit()
