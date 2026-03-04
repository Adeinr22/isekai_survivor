import pygame
from os.path import join
from os import walk

window_width, window_height = 1920, 1080
tile_size = 64

# UI Colors
health_color = (255, 0, 0)
health_bg_color = (100, 0, 0)
xp_color = (0, 255, 0)
xp_bg_color = (0, 100, 0)
ui_font_color = (255, 255, 255)
ui_font_size = 36