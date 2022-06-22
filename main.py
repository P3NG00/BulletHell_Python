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
from data.constants import BULLET_RADIUS
from data.constants import create_font
from data.constants import ENEMY_SPAWN_DISTANCE
from data.constants import ENEMY_SPAWN_RATE
from data.constants import FPS
from data.constants import PAUSE_OVERLAY_COLOR
from data.constants import PLAYER_RADIUS
from data.constants import random_vector
from data.constants import seconds_to_frames
from data.constants import SURFACE_CENTER
from data.constants import SURFACE_SIZE
from data.constants import TITLE
from data.draw import Draw
from data.game_object import Bullet
from data.game_object import Enemy
from data.game_object import Player
from data.game_object import test_collision

"""main game script"""

pg.init()

# default game settings
SETTINGS_FILE = "data/settings.json"
# game settings
try:
    with open(SETTINGS_FILE) as file:
        settings = json.load(file)
except:
    settings = {"anti-aliasing": False,
                "show_aim_line": True}

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
    return FONTS[font_type].render(text, settings["anti-aliasing"], color)

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
# TODO eventually this will be changed to a dictionary to allow for multiple weapons (maybe custom ones too)
WEAPON_BULLETS = 10
WEAPON_COOLDOWN_FRAMES = seconds_to_frames(0.2)
WEAPON_DAMAGE = 1
WEAPON_RELOAD_FRAMES = seconds_to_frames(1)

# tile
TILE = load_image("images/tile.png").convert()

# ui
UI_BORDER_OFFSET = 15
AIM_LINE_LENGTH = 40


# begin main script
set_window_title(TITLE)
# program info
draw = Draw(surface_main, TILE)
clock = Clock()
input = Vector2(0)
pause = False
running = True
current_enemy_spawn_time = ENEMY_SPAWN_RATE
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
                    case pg.K_F12:
                        settings["anti-aliasing"] = not settings["anti-aliasing"]
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
        # update enemies
        for enemy in obj_enemy:
            enemy.update(player)
            # test enemy collision
            for enemy_ in obj_enemy:
                test_collision(enemy, enemy_)
        # remove dead game objects
        obj_bullet = [bullet for bullet in obj_bullet if bullet.is_alive()]
        enemies = len(obj_enemy)
        obj_enemy = [enemy for enemy in obj_enemy if enemy.is_alive()]
        # increment kill for each dead enemy
        stats["kills"] += enemies - len(obj_enemy)
        # update draw object
        draw.update(player.pos, settings["anti-aliasing"])

    # Render

    # draw background
    draw.background()
    # draw game objects
    if player.is_alive():
        player.draw(draw)
    for obj_list in [obj_enemy, obj_bullet]:
        for obj in obj_list:
            obj.draw(draw)
    # display appropriate ui
    if player.is_alive():
        if not pause and settings["show_aim_line"]:
            # draw aim line
            start_pos = player.pos + (get_mouse_direction() * (player.radius * 2))
            draw.line(AIM_LINE_COLOR, start_pos, get_mouse_direction(), AIM_LINE_LENGTH, 2)
        # these are printed top to bottom
        ui_info = [f"pos_x: {player.pos.x:.2f}",
                   f"pos_y: {player.pos.y:.2f}",
                   f"fps: {clock.get_fps():.2f}",
                   f"distance: {stats['distance']:.2f}",
                   f"bullets: {stats['bullets']}",
                   f"shots: {stats['shots']}",
                   f"hits: {stats['hits']}",
                   f"kills: {stats['kills']}",
                   f"life: {player.life}"]
        current_height = UI_BORDER_OFFSET
        for i in range(len(ui_info)):
            # replace index with blit information
            ui_info[i] = (create_text_surface(UI_FONT_COLOR, FontType.UI, ui_info[i]), (UI_BORDER_OFFSET + 5, current_height))
            # move downwards from last height
            current_height += ui_info[i][0].get_height()
        # blit surfaces
        surface_main.blits(ui_info)
        # if paused overlay fade
        if pause:
            # apply pause overlay
            surface_apply_fade()
            surface_text_pause = create_text_surface(PAUSE_FONT_COLOR, FontType.NORMAL, "Paused")
            surface_main.blit(surface_text_pause, (SURFACE_SIZE - surface_text_pause.get_size()) / 2)
    else:
        # apply game over and restart text
        surface_apply_fade()
        center = SURFACE_CENTER.copy()
        surface_text_gameover = create_text_surface(GAMEOVER_FONT_COLOR, FontType.GAMEOVER, "GAME OVER")
        surface_text_restart = create_text_surface(RESTART_FONT_COLOR, FontType.NORMAL, "Press SPACE to restart...")
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
