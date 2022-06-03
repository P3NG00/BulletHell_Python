import sys
import random
import pygame as pg
from numpy import cos
from numpy import pi
from numpy import sin
from pygame.math import Vector2
from data.constants import BACKGROUND_COLOR
from data.constants import BULLET_RADIUS
from data.constants import ENEMY_SPAWN_DISTANCE
from data.constants import ENEMY_SPAWN_RATE
from data.constants import FONT_FILE
from data.constants import FONT_SIZES
from data.constants import FPS
from data.constants import FRAME_TIME
from data.constants import GAMEOVER_FONT_COLOR
from data.constants import PAUSE_FONT_COLOR
from data.constants import PAUSE_OVERLAY_ALPHA
from data.constants import PAUSE_OVERLAY_COLOR
from data.constants import PLAYER_RADIUS
from data.constants import RESTART_FONT_COLOR
from data.constants import START_BULLETS
from data.constants import START_ENEMIES
from data.constants import SURFACE_SIZE
from data.constants import TITLE
from data.constants import UI_BORDER_OFFSET
from data.constants import UI_FONT_COLOR
from data.game_object import Bullet
from data.game_object import Enemy
from data.game_object import Player

"""main game script"""


def create_text_surface(text, color, size_index=0):
    """returns a surface with colored text"""
    return font[size_index].render(text, False, color)


def surface_apply_fade():
    """applies fade effect to main surface"""
    surface_main.blit(surface_fade, (0, 0))


def surface_apply_pause():
    """applies pause overlay (over fade) to main surface"""
    surface_apply_fade()
    surface_main.blit(surface_text_pause,
                      ((SURFACE_SIZE - surface_text_pause.get_size()) / 2))


def surface_apply_game_over():
    """applied game over and restart text (over fade) to main surface"""
    surface_apply_fade()
    center = SURFACE_SIZE / 2
    surface_main.blit(surface_text_gameover, (center -
                      (Vector2(surface_text_gameover.get_size()) / 2)))
    center.y += surface_text_gameover.get_height()
    surface_main.blit(surface_text_restart, (center -
                      (Vector2(surface_text_restart.get_size()) / 2)))


def random_vector():
    """returns a unit vector with a random direction"""
    random_angle = random.uniform(0, 2 * pi)
    return Vector2(cos(random_angle), sin(random_angle))


def spawn_enemy(distance_scale=1.0):
    """spawns enemy at random position"""
    obj_enemy.append(Enemy(obj_player.pos + (random_vector()
                     * ENEMY_SPAWN_DISTANCE * distance_scale)))


def fire_bullet():
    # Calculate direction of bullet from player to mouse
    mouse_pos = pg.mouse.get_pos()
    start_pos = obj_player.pos.copy()
    direction = (mouse_pos - start_pos).normalize()
    # make bullet start in front of player
    start_offset = direction.normalize() * (PLAYER_RADIUS + BULLET_RADIUS)
    start_pos += start_offset
    # Create new bullet object
    obj_bullet.append(Bullet(start_pos, direction))
    stats["bullets"] -= 1


def reset_game():
    """resets game data"""
    global obj_player, obj_bullet, obj_enemy, stats
    # reset game objects
    obj_player = Player(SURFACE_SIZE / 2)
    obj_bullet, obj_enemy = [], []
    # reset game stats
    stats = {
        "bullets": START_BULLETS,
        "killed": 0}
    # spawn enemies shorter than regular spawn distance
    for _ in range(START_ENEMIES):
        spawn_enemy(0.6)


# initialize pygame
pg.init()
pg.display.set_caption(TITLE)
# create fonts
font = [pg.font.Font(FONT_FILE, font_size) for font_size in FONT_SIZES]
# program info
clock = pg.time.Clock()
input = Vector2(0)
pause = False
running = True
current_enemy_spawn_time = ENEMY_SPAWN_RATE
# create surfaces
surface_main = pg.display.set_mode(SURFACE_SIZE)
surface_fade = pg.Surface(SURFACE_SIZE)
surface_fade.fill(PAUSE_OVERLAY_COLOR)
surface_fade.set_alpha(PAUSE_OVERLAY_ALPHA)
surface_text_pause = create_text_surface("Paused", PAUSE_FONT_COLOR)
surface_text_gameover = create_text_surface(
    "GAME OVER", GAMEOVER_FONT_COLOR, 1)
surface_text_restart = create_text_surface(
    "Press SPACE to restart...", RESTART_FONT_COLOR)
# game data
obj_player = None
obj_bullet = None
obj_enemy = None
stats = None
# reset game
reset_game()


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
                        pause = True
                        surface_apply_pause()
                        pg.display.iconify()
                    # handle pause toggling
                    case pg.K_ESCAPE:
                        if obj_player.is_alive():
                            if pause:
                                pause = False
                            else:
                                pause = True
                                surface_apply_pause()
                    # restart game button
                    case pg.K_SPACE:
                        if not obj_player.is_alive():
                            reset_game()
                # movement input press
                match event.key:
                    case pg.K_w:
                        input.y -= 1
                    case pg.K_s:
                        input.y += 1
                    case pg.K_a:
                        input.x -= 1
                    case pg.K_d:
                        input.x += 1
            case pg.KEYUP:
                # movement input release
                match event.key:
                    case pg.K_w:
                        input.y += 1
                    case pg.K_s:
                        input.y -= 1
                    case pg.K_a:
                        input.x += 1
                    case pg.K_d:
                        input.x -= 1
            case pg.MOUSEBUTTONDOWN:
                # shoot bullet
                if event.button == 1 and not pause and stats["bullets"] > 0 and obj_player.is_alive():
                    fire_bullet()
        # end of event handling

    # check pause
    if not pause:

        # spawn enemies around player
        current_enemy_spawn_time -= FRAME_TIME
        if current_enemy_spawn_time < 0.0:
            current_enemy_spawn_time += ENEMY_SPAWN_RATE
            spawn_enemy()
        # reset screen
        surface_main.fill(BACKGROUND_COLOR)
        # update game objects
        if obj_player.is_alive():
            obj_player.update(input)
        for enemy in obj_enemy:
            enemy.update(obj_player)
        for bullet in obj_bullet:
            bullet.update()
            # check bullet collision
            for enemy in obj_enemy:
                # if bullet hits enemy
                if bullet.is_touching(enemy):
                    bullet.life = 0
                    enemy.life -= 1
                    # increment bullet and kill count
                    for stat in ["bullets", "killed"]:
                        stats[stat] += 1
        # remove dead game objects
        obj_bullet = [bullet for bullet in obj_bullet if bullet.is_alive()]
        obj_enemy = [enemy for enemy in obj_enemy if enemy.is_alive()]
        # draw game objects
        if obj_player.is_alive():
            obj_player.draw(surface_main)
        for obj_list in [obj_enemy, obj_bullet]:
            for obj in obj_list:
                obj.draw(surface_main)
        # display appropriate ui
        if obj_player.is_alive():
            ui = [f"{stat}: {stats[stat]}" for stat in ["bullets", "killed"]]
            ui.append(f"life: {obj_player.life}")
            current_height = SURFACE_SIZE.y - UI_BORDER_OFFSET
            for i in range(len(ui)):
                # create text surface from string
                debug_surface = create_text_surface(ui[i], UI_FONT_COLOR)
                # move upwards from last height
                current_height -= debug_surface.get_height()
                # replace index with blit information
                ui[i] = (debug_surface, (UI_BORDER_OFFSET + 5, current_height))
            # blit surfaces
            surface_main.blits(ui)
        else:
            surface_apply_game_over()
        # end of game update

    # display surface
    pg.display.flip()
    # fps lock
    clock.tick(FPS)
    # end of game loop

pg.quit()
sys.exit()
# end of program
