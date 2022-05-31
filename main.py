import sys
import pygame as pg
from data.constants import BACKGROUND_COLOR
from data.constants import BULLET_COLOR
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
from data.game_object import Player
from data.util import normalize

"""main game script"""


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
# create player
player = Player([SS[0] / 2, SS[1] / 2], 16, 200, PLAYER_COLOR)
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
                        input[1] += 1
                    case pg.K_s:
                        input[1] -= 1
                    case pg.K_a:
                        input[0] -= 1
                    case pg.K_d:
                        input[0] += 1
            case pg.KEYUP:
                # actions for keyup events
                match event.key:
                    # movement input
                    case pg.K_w:
                        input[1] -= 1
                    case pg.K_s:
                        input[1] += 1
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
                            direction = normalize([
                                mouse_pos[0] - player.pos[0],
                                player.pos[1] - mouse_pos[1]])
                            # Create new bullet object
                            game_objects.append(GameObject(
                                player.pos.copy(), 4, 450, BULLET_COLOR, direction))

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
        # print info
        print(
            f"objs: {len(game_objects):2} | move: {input[0]:2}, {input[1]:2} | pos: {player.pos[0]:7.2f}, {player.pos[1]:7.2f}")

    # display surface
    pg.display.flip()
    # fps lock
    clock.tick(FPS)

# exit code
pg.quit()
sys.exit()
