import sys
import os
import pygame


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ProgressiveText:
    def __init__(self, target_text, max_width, font_name, font_size, x, y):
        self.target_text = target_text
        self.current_text = ""
        self.max_width = max_width
        self.font_name = font_name
        self.font_size = font_size
        self.x = x
        self.y = y
        self.color = (255, 255, 255)

    def update(self):
        if len(self.current_text) < len(self.target_text):
            self.current_text += self.target_text[len(self.current_text)]

    def draw(self, surface):
        lines = [self.current_text[i:i + self.max_width] for i in range(0, len(self.current_text), self.max_width)]
        for index, line in enumerate(lines):
            draw_text(surface, line, self.font_size, self.color, self.x, self.y + index * self.font_size)

    def skip(self):
        self.current_text = self.target_text


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


font_path = resource_path("assets/fonts/DTM-Sans.otf")

font_dictionary = {
    "DTM-Sans": resource_path("assets/fonts/DTM-Sans.otf"),
    "UT-Attack": resource_path("assets/fonts/undertale-attack-font.ttf"),
    "UT-HUD": resource_path("assets/fonts/undertale-in-game-hud-font.ttf")
}


def draw_text(surface, text, size, color, x, y, anchor="topleft", rotation: int = 0, font_name="DTM-Sans"):
    font = pygame.font.Font(font_dictionary[font_name], size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    match anchor:
        case "center":
            text_rect.center = (x, y)
        case "topleft":
            text_rect.topleft = (x, y)
        case "midleft":
            text_rect.midleft = (x, y)
        case "topright":
            text_rect.topright = (x, y)
        case "midright":
            text_rect.midright = (x, y)
    if rotation != 0:
        rotated_text = pygame.transform.rotate(text_surface, rotation)
        rotated_rect = rotated_text.get_rect(center=text_rect.center)
        surface.blit(rotated_text, rotated_rect)
    else:
        surface.blit(text_surface, text_rect)
