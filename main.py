import sys
import pygame as pg
from data.constants import BACKGROUND_COLOR
from data.constants import FONT_FILE
from data.constants import FONT_SIZE
from data.constants import FPS
from data.constants import PAUSE_FONT_COLOR
from data.constants import PAUSE_OVERLAY_ALPHA
from data.constants import PAUSE_OVERLAY_COLOR
from data.constants import PLAYER_COLOR
from data.constants import SURFACE_SIZE as SS
from data.constants import TITLE
from data.game_object import GameObject


# initialize pygame
pg.init()
# create main window with title
surface = pg.display.set_mode(SS)
pg.display.set_caption(TITLE)
# create font
font = pg.font.Font(FONT_FILE, FONT_SIZE)
# create pause overlay
surface_pause = pg.Surface(SS)
surface_pause.fill(PAUSE_OVERLAY_COLOR)
surface_pause.set_alpha(PAUSE_OVERLAY_ALPHA)
surface_pause_text = font.render("Paused", True, PAUSE_FONT_COLOR)
# create game clock
clock = pg.time.Clock()
# paused state
pause = False
# movement variables
input_h, input_v = 0, 0
# create player object
player = GameObject([SS[0] / 2, SS[1] / 2], 16, 300, PLAYER_COLOR)
# program running variable
running = True

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
                        input_v += 1
                    case pg.K_s:
                        input_v -= 1
                    case pg.K_a:
                        input_h -= 1
                    case pg.K_d:
                        input_h += 1
            case pg.KEYUP:
                # actions for keyup events
                match event.key:
                    # movement input
                    case pg.K_w:
                        input_v -= 1
                    case pg.K_s:
                        input_v += 1
                    case pg.K_a:
                        input_h += 1
                    case pg.K_d:
                        input_h -= 1
            case pg.MOUSEBUTTONDOWN:
                # actions for mouse button down events
                match event.button:
                    # left mouse button click
                    case 1:
                        # TODO make character shoot a new bullet circle object in direction of mouse cursor
                        print(1)

    # check pause
    if not pause:
        # reset screen
        surface.fill(BACKGROUND_COLOR)
        # update game objects
        # TODO update ALL registered game objects
        player.update((input_h, input_v))
        # draw game object
        # TODO draw ALL registered game objects
        player.draw(surface)
        # print info about the game object
        print(
            f"h: {input_h:2} | v: {input_v:2} | x: {player.pos[0]:7.2f} | y: {player.pos[1]:7.2f}")

    # display surface
    pg.display.flip()
    # fps lock
    clock.tick(FPS)

# exit code
pg.quit()
sys.exit()
