import pygame as pg
import json
from enum import Enum
from pygame import Surface
from pygame.color import Color
from pygame.display import flip as update_window
from pygame.display import iconify as minimize_window
from pygame.display import set_caption as set_window_title
from pygame.display import set_mode as create_window
from pygame.image import load as load_image
from pygame.math import Vector2
from pygame.mouse import get_pos as get_mouse_pos
from pygame.time import Clock
from data.constants import AIM_LINE_COLOR
from data.constants import AIM_LINE_LENGTH
from data.constants import AIM_LINE_WIDTH
from data.constants import BULLET_RADIUS
from data.constants import create_font
from data.constants import ENEMY_DESPAWN_DISTANCE
from data.constants import ENEMY_DESPAWN_RATE
from data.constants import ENEMY_SPAWN_DISTANCE
from data.constants import ENEMY_SPAWN_RATE
from data.constants import FPS
from data.constants import PAUSE_OVERLAY_COLOR
from data.constants import PLAYER_RADIUS
from data.constants import random_vector
from data.constants import seconds_to_frames
from data.constants import SURFACE_CENTER
from data.constants import SURFACE_SIZE
from data.constants import TEXT_GAME_OVER
from data.constants import TEXT_PAUSE
from data.constants import TEXT_RESTART
from data.constants import TITLE
from data.constants import UI_BORDER_OFFSET
from data.draw import Draw
from data.game_object import Bullet
from data.game_object import Enemy
from data.game_object import Player
from data.game_object import test_collision

"""main game script"""

pg.init()

# game settings
SETTINGS_FILE = "data/settings.json"

ANTI_ALIASING = "anti_aliasing"
SHOW_AIM_LINE = "show_aim_line"
SHOW_DEBUG_INFO = "show_debug_info"

DEFAULT_SETTINGS = {ANTI_ALIASING: False,
                    SHOW_AIM_LINE: True,
                    SHOW_DEBUG_INFO: False}

# attempt to load settings from file
try:
    with open(SETTINGS_FILE) as file:
        settings = json.load(file)
    default_copy = DEFAULT_SETTINGS.copy()
    # delete invalid settings
    for setting in settings.copy():
        try:
            del default_copy[setting]
        except KeyError:
            del settings[setting]
    # add missing settings
    for setting in default_copy:
        settings[setting] = default_copy[setting]
# error loading file, use default settings
except:
    settings = DEFAULT_SETTINGS

def toggle_setting(setting: str) -> None:
    """toggles specified setting"""
    settings[setting] = not settings[setting]

# fonts
class FontType(Enum):
    """font types"""
    NORMAL = 0
    UI = 1
    GAMEOVER = 2

FONTS = {FontType.NORMAL: create_font(24),
         FontType.UI: create_font(16),
         FontType.GAMEOVER: create_font(64)}

# font colors
GAMEOVER_FONT_COLOR = Color(255, 0, 0)
PAUSE_FONT_COLOR = Color(255, 255, 255)
RESTART_FONT_COLOR = Color(128, 128, 128)
UI_FONT_COLOR = Color(192, 192, 192)

# surfaces
surface_main = create_window(SURFACE_SIZE)
surface_fade = Surface(SURFACE_SIZE)
surface_fade.fill(PAUSE_OVERLAY_COLOR)
surface_fade.set_alpha(PAUSE_OVERLAY_COLOR.a)

def create_text_surface(color: Color, font_type: FontType, text: str) -> Surface:
    """returns a surface with colored text"""
    return FONTS[font_type].render(text, settings[ANTI_ALIASING], color)

def surface_apply_fade() -> None:
    """applies fade effect to main surface"""
    surface_main.blit(surface_fade, (0, 0))

def spawn_enemy(distance_scale: float = 1.0) -> None:
    """spawns enemy at random position"""
    obj_enemy.append(Enemy(player.pos + (random_vector() * ENEMY_SPAWN_DISTANCE * distance_scale)))

def get_mouse_direction() -> Vector2:
    """returns a normalized vector2 in the direction of the mouse from the player"""
    return (get_mouse_pos() + draw.camera_offset - player.pos).normalize()

def reset_game() -> None:
    """resets game data"""
    global player, obj_bullet, obj_enemy, weapon_cooldown, weapon_reload, stats
    # reset camera offset
    draw.camera_offset = -SURFACE_CENTER
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
             "kills": 0,
             "shots": 0}
    # spawn enemies shorter than regular spawn distance
    for i in range(START_ENEMY_AMOUNT):
        spawn_enemy(START_ENEMY_DISTANCE + (i * START_ENEMY_INCREMENT))

# game values
START_ENEMY_AMOUNT = 3
START_ENEMY_DISTANCE = 0.55
START_ENEMY_INCREMENT = 0.1

# weapon
WEAPON_BULLETS = 10
WEAPON_COOLDOWN_FRAMES = seconds_to_frames(0.2)
WEAPON_DAMAGE = 1
WEAPON_RELOAD_FRAMES = seconds_to_frames(1)

# tile
TILE = load_image("images/tile.png").convert()

# begin main script
set_window_title(TITLE)
# program info
draw = Draw(surface_main, TILE)
clock = Clock()
input = Vector2(0)
pause = False
running = True
current_enemy_spawn_time = ENEMY_SPAWN_RATE
current_enemy_despawn_time = ENEMY_DESPAWN_RATE
# game data
player = None
obj_bullet = None
obj_enemy = None
weapon_cooldown = None
weapon_reload = None
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
            case pg.ACTIVEEVENT:
                # hasattr needed because first active event sent doesnt contain gain and state data
                if hasattr(event, "gain") and event.gain == 0 and event.state == 1:
                    # pause on lost focus
                    pause = True
            case pg.KEYDOWN:
                # actions for keydown events
                match event.key:
                    # close application
                    case pg.K_END:
                        running = False
                    # minimize game
                    case pg.K_PAGEDOWN:
                        if player.is_alive():
                            pause = True
                        minimize_window()
                    # handle pause toggling
                    case pg.K_ESCAPE:
                        if player.is_alive():
                            pause = not pause
                    # restart game button
                    case pg.K_SPACE:
                        if not player.is_alive():
                            reset_game()
                    # toggle anti-aliasing
                    case pg.K_F1:
                        toggle_setting(ANTI_ALIASING)
                    # toggle debug info
                    case pg.K_F12:
                        toggle_setting(SHOW_DEBUG_INFO)
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
                    # fire a bullet in the direction of the mouse if bullets are available
                    case 1:
                        # game not paused, player weapon not on cooldown or reloading, and player is alive
                        if not pause and weapon_cooldown == 0 and weapon_reload == 0 and player.is_alive():
                            # update stats
                            stats["bullets"] -= 1
                            stats["shots"] += 1
                            # if last bullet begin reload
                            if stats["bullets"] == 0:
                                weapon_reload = WEAPON_RELOAD_FRAMES
                            # if bullets remain, start cooldown
                            else:
                                weapon_cooldown = WEAPON_COOLDOWN_FRAMES
                            # create new bullet object in front of player
                            direction = get_mouse_direction()
                            obj_bullet.append(Bullet(player.pos + (direction * (PLAYER_RADIUS + BULLET_RADIUS)), direction))
                    # toggle aim line
                    case 3:
                        if not pause:
                            toggle_setting(SHOW_AIM_LINE)
        # end of event handling

    # check pause
    if not pause:

        # Update

        # spawn enemies around player
        current_enemy_spawn_time -= 1
        if current_enemy_spawn_time == 0:
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
        # update bullets
        for bullet in obj_bullet:
            bullet.update()
            # check bullet collision
            for enemy in obj_enemy:
                # if bullet hits enemy
                if bullet.is_touching(enemy):
                    bullet.kill()
                    enemy.damage(WEAPON_DAMAGE)
                    stats["hits"] += 1
        # update enemies
        for enemy in obj_enemy:
            enemy.update(player)
            # test enemy collision
            for enemy_ in obj_enemy:
                test_collision(enemy, enemy_)
        # check despawn timer
        current_enemy_despawn_time -= 1
        if current_enemy_despawn_time == 0:
            current_enemy_despawn_time = ENEMY_DESPAWN_RATE
            obj_enemy = [enemy for enemy in obj_enemy if (player.pos - enemy.pos).magnitude() < ENEMY_DESPAWN_DISTANCE]
        # remove dead game objects
        obj_bullet = [bullet for bullet in obj_bullet if bullet.is_alive()]
        enemies = len(obj_enemy)
        obj_enemy = [enemy for enemy in obj_enemy if enemy.is_alive()]
        # increment kill for each dead enemy
        stats["kills"] += enemies - len(obj_enemy)
        # update draw object
        draw.update(player.pos, settings[ANTI_ALIASING])

    # Render

    # draw background
    tiles_drawn = draw.background()
    # draw game objects
    player.draw(draw, settings[SHOW_DEBUG_INFO])
    for obj_list in [obj_enemy, obj_bullet]:
        for obj in obj_list:
            obj.draw(draw, settings[SHOW_DEBUG_INFO])
    # display appropriate ui
    if player.is_alive():
        if not pause and settings[SHOW_AIM_LINE]:
            # draw aim line
            start_pos = player.pos + (get_mouse_direction() * (player.radius * 2))
            draw.line(AIM_LINE_COLOR, start_pos, get_mouse_direction(), AIM_LINE_LENGTH, AIM_LINE_WIDTH)
        if settings[SHOW_DEBUG_INFO]:
            # these are printed top to bottom
            debug_info = [f"screen_width: {SURFACE_SIZE.x}",
                          f"screen_height: {SURFACE_SIZE.y}",
                          f"frames_per_second: {clock.get_fps():.3f}",
                          f"pos_x: {player.pos.x:.3f}",
                          f"pos_y: {player.pos.y:.3f}",
                          f"entity_enemies: {len(obj_enemy)}",
                          f"entity_bullets: {len(obj_bullet)}",
                          f"tiles_drawn: {tiles_drawn}",
                          f"enemy_spawn_time: {current_enemy_spawn_time}",
                          f"enemy_despawn_time: {current_enemy_despawn_time}"]
            current_height = UI_BORDER_OFFSET
            for i in range(len(debug_info)):
                # replace index with blit information
                debug_info[i] = (create_text_surface(UI_FONT_COLOR, FontType.UI, debug_info[i]), (UI_BORDER_OFFSET + 5, current_height))
                # move downwards from last height
                current_height += debug_info[i][0].get_height()
            # blit surfaces
            surface_main.blits(debug_info)
        # if paused overlay fade
        if pause:
            # apply pause overlay
            surface_apply_fade()
            surface_text_pause = create_text_surface(PAUSE_FONT_COLOR, FontType.NORMAL, TEXT_PAUSE)
            surface_main.blit(surface_text_pause, (SURFACE_SIZE - surface_text_pause.get_size()) / 2)
    else:
        # apply game over and restart text
        surface_apply_fade()
        center = SURFACE_CENTER.copy()
        surface_text_gameover = create_text_surface(GAMEOVER_FONT_COLOR, FontType.GAMEOVER, TEXT_GAME_OVER)
        surface_text_restart = create_text_surface(RESTART_FONT_COLOR, FontType.NORMAL, TEXT_RESTART)
        surface_main.blit(surface_text_gameover, center - Vector2(surface_text_gameover.get_size()) / 2)
        center.y += surface_text_gameover.get_height()
        surface_main.blit(surface_text_restart, center - Vector2(surface_text_restart.get_size()) / 2)
    # end of game update

    # display surface
    update_window()
    # fps lock
    clock.tick(FPS)
    # end of game loop

# save settings
with open(SETTINGS_FILE, "w") as file:
    json.dump(settings, file, indent=2)
# close pygame
pg.quit()
# end of program
