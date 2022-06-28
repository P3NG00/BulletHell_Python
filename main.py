import json
from enum import Enum
import pygame as pg
from pygame import init as init_pygame
from pygame import Surface
from pygame.color import Color
from pygame.display import flip as update_window
from pygame.display import iconify as minimize_window
from pygame.display import set_caption as set_window_title
from pygame.display import set_mode as create_window
from pygame.event import get as get_events
from pygame.image import load as load_image
from pygame.math import Vector2
from pygame.mouse import get_pos as get_mouse_pos
from pygame.time import Clock
from pygame.transform import scale as scale_surface
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
from data.constants import TEXT_DEBUG
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

init_pygame()

# game settings
SETTINGS_FILE = "data/settings.json"

ANTI_ALIASING = "anti_aliasing"
SHOW_AIM_LINE = "show_aim_line"
SHOW_DEBUG_INFO = "show_debug_info"

DEFAULT_SETTINGS = {ANTI_ALIASING: True,
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
DEBUG_FONT_COLOR = Color(192, 192, 192)
GAMEOVER_FONT_COLOR = Color(255, 0, 0)
PAUSE_FONT_COLOR = Color(255, 255, 255)
RESTART_FONT_COLOR = Color(128, 128, 128)

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

# weapon
WEAPON_BULLETS = 10
WEAPON_COOLDOWN_FRAMES = seconds_to_frames(0.2)
WEAPON_DAMAGE = 1
WEAPON_RELOAD_FRAMES = seconds_to_frames(1)

# images
def _load_image(file: str, scale: Vector2) -> Surface:
    return scale_surface(load_image(f"images/{file}.png").convert_alpha(), scale)

IMAGE_BULLET_SCALE = Vector2(16, 32)
IMAGE_HEART_SCALE = Vector2(32)
IMAGE_HEART_SPACE_SCALE = IMAGE_HEART_SCALE / 4
IMAGE_TILE_SCALE = Vector2(96)

IMAGE_BULLET = _load_image("bullet", IMAGE_BULLET_SCALE)
IMAGE_HEART = _load_image("heart", IMAGE_HEART_SCALE)
IMAGE_TILE = _load_image("tile", IMAGE_TILE_SCALE)

IMAGE_BULLET_SIZE = Vector2(IMAGE_BULLET.get_size())
IMAGE_HEART_SIZE = Vector2(IMAGE_HEART.get_size())

UI_BULLET_START_POS = SURFACE_SIZE - Vector2(UI_BORDER_OFFSET) - IMAGE_BULLET_SIZE

# begin main script
set_window_title(TITLE)
# program info
draw = Draw(surface_main, IMAGE_TILE)
clock = Clock()
input = Vector2(0)
firing = False
pause = False
running = True
current_enemy_spawn_time = int(ENEMY_SPAWN_RATE / 2)
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
    for event in get_events():
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
                    # enable firing
                    case 1:
                        firing = True
                    # toggle aim line
                    case 3:
                        if not pause:
                            toggle_setting(SHOW_AIM_LINE)
            case pg.MOUSEBUTTONUP:
                match event.button:
                    # disable firing
                    case 1:
                        firing = False
    # end of event handling

    # check pause
    if not pause:

        # Update

        # spawn enemies around player
        current_enemy_spawn_time -= 1
        if current_enemy_spawn_time == 0:
            current_enemy_spawn_time = ENEMY_SPAWN_RATE
            obj_enemy.append(Enemy(player.pos + (random_vector() * ENEMY_SPAWN_DISTANCE * 0.5)))
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
        # fire a bullet in the direction of the mouse if bullets are available
        # game not paused, player weapon not on cooldown or reloading, and player is alive
        if firing and not pause and weapon_cooldown == 0 and weapon_reload == 0 and player.is_alive():
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
        # remove dead game objects
        obj_bullet = [bullet for bullet in obj_bullet if bullet.is_alive()]
        enemies = len(obj_enemy)
        obj_enemy = [enemy for enemy in obj_enemy if enemy.is_alive()]
        # increment kill for each dead enemy
        stats["kills"] += enemies - len(obj_enemy)
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
        # draw aim line if not paused and setting is enabled
        if not pause and settings[SHOW_AIM_LINE]:
            draw.line(AIM_LINE_COLOR, player.pos + (get_mouse_direction() * (player.radius * 2)), get_mouse_direction(), AIM_LINE_LENGTH, AIM_LINE_WIDTH)
        # draw health
        height = SURFACE_SIZE.y - IMAGE_HEART_SIZE.y - UI_BORDER_OFFSET
        start = SURFACE_CENTER.x - (player._life * (IMAGE_HEART_SIZE.x / 2) + ((player._life - 1) * (IMAGE_HEART_SPACE_SCALE.x / 2)))
        surface_main.blits([(IMAGE_HEART, (start + ((IMAGE_HEART_SIZE.x + IMAGE_HEART_SPACE_SCALE.x) * i), height)) for i in range(0, player._life)])
        # draw ammo
        surface_main.blits([(IMAGE_BULLET, (UI_BULLET_START_POS.x - (IMAGE_BULLET_SIZE.x * i), UI_BULLET_START_POS.y)) for i in range(stats["bullets"])])
        # draw debug info
        if settings[SHOW_DEBUG_INFO]:
            # these are printed top to bottom
            blit_info = [f"screen_size: {int(SURFACE_SIZE.x)}x{int(SURFACE_SIZE.y)}",
                         f"frames_per_second: {clock.get_fps():.3f}",
                         f"pos_x: {player.pos.x:.3f}",
                         f"pos_y: {player.pos.y:.3f}",
                         f"direction_x: {player.direction.x:.3f}",
                         f"direction_y: {player.direction.y:.3f}",
                         f"entity_enemies: {len(obj_enemy)}",
                         f"entity_bullets: {len(obj_bullet)}",
                         f"tiles_drawn: {tiles_drawn}",
                         f"enemy_spawn_time: {current_enemy_spawn_time}",
                         f"enemy_despawn_time: {current_enemy_despawn_time}"]
            # blit surfaces
            surface_main.blit(create_text_surface(DEBUG_FONT_COLOR, FontType.NORMAL, TEXT_DEBUG), (UI_BORDER_OFFSET + 5, UI_BORDER_OFFSET))
            current_height = UI_BORDER_OFFSET + FONTS[FontType.NORMAL].get_height()
            surface_main.blits([(create_text_surface(DEBUG_FONT_COLOR, FontType.UI, blit_info[i]), (UI_BORDER_OFFSET + 5, current_height + (FONTS[FontType.UI].get_height() * i))) for i in range(len(blit_info))])
        # if paused apply overlay
        if pause:
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
