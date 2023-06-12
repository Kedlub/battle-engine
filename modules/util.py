import sys
import os
import pygame


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def draw_gradient(surface, alpha, num_blocks, color, max_height):
    width = surface.get_width()
    height = surface.get_height()
    block_height = max_height / num_blocks
    for index in range(num_blocks):
        color_a = (color[0], color[1], color[2], alpha)
        rect = pygame.Surface((width, height / 2), pygame.SRCALPHA)
        rect.fill(color_a)
        surface.blit(rect, (0, height - max_height + block_height * index + block_height))


font_path = resource_path("assets/fonts/DeterminationMonoWebRegular.ttf")


def draw_text(surface, text, size, color, x, y, centered=False, rotation: int = 0):
    font = pygame.font.Font(font_path, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y)) if centered == True else text_surface.get_rect(midtop=(x, y))
    if rotation != 0:
        rotated_text = pygame.transform.rotate(text_surface, rotation)
        rotated_rect = rotated_text.get_rect(center=text_rect.center)
        surface.blit(rotated_text, rotated_rect)
    else:
        surface.blit(text_surface, text_rect)
