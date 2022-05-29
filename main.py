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
from data.util import end_program


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
# create player object
game_object = GameObject([SS[0] / 2, SS[1] / 2], 16, 250, PLAYER_COLOR)
# create game clock
clock = pg.time.Clock()
# paused state
pause = False
# movement variables
input_h, input_v = 0, 0

# loop
while True:

    # handle events
    for event in pg.event.get():
        match event.type:
            case pg.QUIT:
                # actions when window is closed
                end_program()
            case pg.KEYDOWN:
                # actions for keydown events
                match event.key:
                    case pg.K_END:
                        end_program()
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

    # check pause
    if not pause:
        # reset screen
        surface.fill(BACKGROUND_COLOR)
        # pass input to game object
        game_object.move(input_h, input_v)
        print(
            f"h: {input_h:2} | v: {input_v:2} | x: {game_object.pos[0]:7.2f} | y: {game_object.pos[1]:7.2f}")
        # draw game object
        game_object.draw(surface)

    # display surface
    pg.display.flip()
    # fps lock
    clock.tick(FPS)
