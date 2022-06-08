import random
import pygame as pg
import json
from numpy import cos
from numpy import pi
from numpy import sin
from pygame import Surface
from pygame.color import Color
from pygame.draw import line as draw_line
from pygame.math import Vector2
from data.constants import AIM_LINE_COLOR
from data.constants import AIM_LINE_LENGTH
from data.constants import BULLET_RADIUS
from data.constants import CAMERA_SPEED
from data.constants import ENEMY_SPAWN_DISTANCE
from data.constants import ENEMY_SPAWN_RATE
from data.constants import FONTS
from data.constants import FontType
from data.constants import FPS
from data.constants import GAMEOVER_FONT_COLOR
from data.constants import PAUSE_FONT_COLOR
from data.constants import PAUSE_OVERLAY_COLOR
from data.constants import PLAYER_RADIUS
from data.constants import RESTART_FONT_COLOR
from data.constants import SETTINGS_DEFAULT
from data.constants import SETTINGS_FILE
from data.constants import START_ENEMY_AMOUNT
from data.constants import START_ENEMY_DISTANCE
from data.constants import START_ENEMY_INCREMENT
from data.constants import SURFACE_CENTER
from data.constants import SURFACE_SIZE
from data.constants import TILE
from data.constants import TILE_SIZE
from data.constants import TITLE
from data.constants import UI_BORDER_OFFSET
from data.constants import UI_FONT_COLOR
from data.constants import WEAPON_BULLETS
from data.constants import WEAPON_COOLDOWN_FRAMES
from data.constants import WEAPON_DAMAGE
from data.constants import WEAPON_RELOAD_FRAMES
from data.game_object import Bullet
from data.game_object import Enemy
from data.game_object import Player
from data.game_object import test_collision


"""main game script"""


def create_text_surface(text: str, color: Color, font_type: FontType) -> Surface:
    """returns a surface with colored text"""
    return FONTS[font_type].render(text, False, color)


def surface_apply_fade() -> None:
    """applies fade effect to main surface"""
    surface_main.blit(surface_fade, (0, 0))


def surface_apply_pause() -> None:
    """applies pause overlay (over fade) to main surface"""
    surface_apply_fade()
    surface_main.blit(surface_text_pause, (SURFACE_SIZE -
                      surface_text_pause.get_size()) / 2)


def surface_apply_game_over() -> None:
    """applied game over and restart text (over fade) to main surface"""
    surface_apply_fade()
    center = SURFACE_SIZE / 2
    surface_main.blit(surface_text_gameover, center -
                      Vector2(surface_text_gameover.get_size()) / 2)
    center.y += surface_text_gameover.get_height()
    surface_main.blit(surface_text_restart, center -
                      Vector2(surface_text_restart.get_size()) / 2)


def random_vector() -> Vector2:
    """returns a unit vector with a random direction"""
    random_angle = random.uniform(0, 2 * pi)
    return Vector2(cos(random_angle), sin(random_angle))


def spawn_enemy(distance_scale: float = 1.0) -> None:
    """spawns enemy at random position"""
    obj_enemy.append(Enemy(player.pos + (random_vector()
                     * ENEMY_SPAWN_DISTANCE * distance_scale)))


def get_mouse_direction() -> Vector2:
    """returns a normalized vector2 in the direction of the mouse from the player"""
    return (pg.mouse.get_pos() + camera_offset - player.pos).normalize()


def fire_bullet() -> None:
    """fires a bullet in the direction of the mouse if bullets are available"""
    global weapon_cooldown, weapon_reload
    # game not paused, player weapon not on cooldown or reloading, and player is alive
    if not pause and weapon_cooldown == 0 and weapon_reload == 0 and player.is_alive():
        # subtract bullet count
        stats["bullets"] -= 1
        # if last bullet begin reload
        if stats["bullets"] == 0:
            weapon_reload = WEAPON_RELOAD_FRAMES
        # if bullets remain, start cooldown
        else:
            weapon_cooldown = WEAPON_COOLDOWN_FRAMES
        # create new bullet object in front of player
        direction = get_mouse_direction()
        obj_bullet.append(
            Bullet(player.pos + (direction * (PLAYER_RADIUS + BULLET_RADIUS)), direction))


def reset_game() -> None:
    """resets game data"""
    global camera_offset, player, obj_bullet, obj_enemy, weapon_cooldown, weapon_reload, stats
    # reset camera offset
    camera_offset = -SURFACE_CENTER
    # reset game objects
    player = Player(Vector2(0))
    obj_bullet, obj_enemy = [], []
    # reset weapon time
    weapon_cooldown = 0
    weapon_reload = 0
    # reset game stats
    stats = {"bullets": WEAPON_BULLETS,
             "distance": 0.0,
             "hits": 0,
             "shots": 0}
    # spawn enemies shorter than regular spawn distance
    for i in range(START_ENEMY_AMOUNT):
        spawn_enemy(START_ENEMY_DISTANCE + (i * START_ENEMY_INCREMENT))


# initialize pygame
pg.display.set_caption(TITLE)
# program info
clock = pg.time.Clock()
input = Vector2(0)
pause = False
running = True
current_enemy_spawn_time = ENEMY_SPAWN_RATE
# create surfaces
surface_main = pg.display.set_mode(SURFACE_SIZE)
surface_fade = Surface(SURFACE_SIZE)
surface_fade.fill(PAUSE_OVERLAY_COLOR)
surface_fade.set_alpha(PAUSE_OVERLAY_COLOR.a)
surface_text_pause = create_text_surface(
    "Paused", PAUSE_FONT_COLOR, FontType.NORMAL)
surface_text_gameover = create_text_surface(
    "GAME OVER", GAMEOVER_FONT_COLOR, FontType.GAMEOVER)
surface_text_restart = create_text_surface(
    "Press SPACE to restart...", RESTART_FONT_COLOR, FontType.NORMAL)
# game data
camera_offset = None
player = None
obj_bullet = None
obj_enemy = None
weapon_cooldown = None
weapon_reload = None
stats = None
# game settings
try:
    with open(SETTINGS_FILE) as file:
        settings = json.load(file)
except:
    settings = SETTINGS_DEFAULT.copy()
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
                        if player.is_alive():
                            pause = not pause
                            if pause:
                                surface_apply_pause()
                    # restart game button
                    case pg.K_SPACE:
                        if not player.is_alive():
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
                match event.button:
                    case 1:
                        # shoot bullet
                        fire_bullet()
                    case 3:
                        # toggle aim line
                        settings["show_aim_line"] = not settings["show_aim_line"]
        # end of event handling

    # check pause
    if not pause:

        # Update

        # spawn enemies around player
        current_enemy_spawn_time -= 1
        if current_enemy_spawn_time <= 0:
            current_enemy_spawn_time = ENEMY_SPAWN_RATE
            spawn_enemy()
        # update player
        original_pos = player.pos.copy()
        if player.is_alive():
            player.update(input)
            if weapon_cooldown > 0:
                weapon_cooldown -= 1
            elif weapon_reload > 0:
                weapon_reload -= 1
                if weapon_reload == 0:
                    # reload finished
                    stats["bullets"] = WEAPON_BULLETS
        stats["distance"] += (player.pos - original_pos).length()
        # update enemies
        for enemy in obj_enemy:
            enemy.update(player)
            # test enemy collision
            for enemy_ in obj_enemy:
                test_collision(enemy, enemy_)
        # update bullets
        for bullet in obj_bullet:
            bullet.update()
            # check bullet collision
            for enemy in obj_enemy:
                # if bullet hits enemy
                if bullet.is_touching(enemy):
                    bullet.life = 0
                    enemy.life -= WEAPON_DAMAGE
                    stats["hits"] += 1
        # remove dead game objects
        obj_bullet = [bullet for bullet in obj_bullet if bullet.is_alive()]
        obj_enemy = [enemy for enemy in obj_enemy if enemy.is_alive()]
        # move camera_offset towards player position
        camera_offset = camera_offset.lerp(
            player.pos - SURFACE_CENTER, CAMERA_SPEED)

        # Render

        # blit background tiles
        start_x = (-camera_offset.x % TILE_SIZE.x) - TILE_SIZE.x
        current_pos = Vector2(start_x, (-camera_offset.y %
                              TILE_SIZE.y) - TILE_SIZE.y)
        while current_pos.y < SURFACE_SIZE.y:
            while current_pos.x < SURFACE_SIZE.x:
                surface_main.blit(TILE, current_pos)
                current_pos.x += TILE_SIZE.x
            current_pos.x = start_x
            current_pos.y += TILE_SIZE.y
        # draw game objects
        if player.is_alive():
            player.draw(surface_main, camera_offset)
        for obj_list in [obj_enemy, obj_bullet]:
            for obj in obj_list:
                obj.draw(surface_main, camera_offset)
        # display appropriate ui
        if player.is_alive():
            if settings["show_aim_line"]:
                # draw aim line
                start_pos = player.pos + \
                    (get_mouse_direction() * (player.radius * 2)) - camera_offset
                draw_line(surface_main, AIM_LINE_COLOR, start_pos,
                          start_pos + (get_mouse_direction() * AIM_LINE_LENGTH), 2)
            # these are printed top to bottom
            ui_info = [f"pos_x: {player.pos.x:.2f}",
                       f"pos_y: {player.pos.y:.2f}",
                       f"fps: {clock.get_fps():.2f}",
                       f"distance: {stats['distance']:.2f}",
                       f"bullets: {stats['bullets']}",
                       f"shots: {stats['shots']:.2f}",
                       f"hits: {stats['hits']}",
                       f"life: {player.life}"]
            current_height = UI_BORDER_OFFSET
            for i in range(len(ui_info)):
                # replace index with blit information
                ui_info[i] = (create_text_surface(
                    ui_info[i], UI_FONT_COLOR, FontType.UI), (UI_BORDER_OFFSET + 5, current_height))
                # move downwards from last height
                current_height += ui_info[i][0].get_height()
            # blit surfaces
            surface_main.blits(ui_info)
        else:
            surface_apply_game_over()
        # end of game update

    # display surface
    pg.display.flip()
    # fps lock
    clock.tick(FPS)
    # end of game loop

# save settings
with open(SETTINGS_FILE, "w") as file:
    json.dump(settings, file, indent=4)
# close pygame
pg.quit()
# end of program
