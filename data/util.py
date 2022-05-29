import sys
import pygame
from .constants import FPS


def scale_fps(input,):
    """scales framerate dependent values"""
    return input / FPS


def end_program():
    """exits the script immediately"""
    pygame.quit()
    sys.exit()
