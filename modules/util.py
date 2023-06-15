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
    def __init__(self, target_text, max_width, font_name, font_size, x, y, tick_length):
        self.target_text = target_text
        self.current_text = ""
        self.max_width = max_width
        self.font_name = font_name
        self.font_size = font_size
        self.lines = []
        self.x = x
        self.y = y
        self.color = (255, 255, 255)
        self.tick_length = tick_length
        self.tick = 0
        self.finished = False

    def update(self):
        if len(self.current_text) < len(self.target_text):
            self.finished = False
            self.tick += 1
            if self.tick >= self.tick_length:
                self.current_text += self.target_text[len(self.current_text)]
                self.tick = 0
                self.lines = self.split_text(self.current_text)
        elif not self.finished:
            self.finished = True

    def split_text(self, text):
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            if current_line:
                test_line = current_line + " " + word
            else:
                test_line = word

            line_width, _ = draw_text_size(test_line, self.font_size, font_name=self.font_name)

            if line_width > self.max_width:
                lines.append(current_line)
                current_line = word
            else:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def draw(self, surface):
        for index, line in enumerate(self.lines):
            draw_text(surface, line, self.font_size, self.color, self.x, self.y + index * self.font_size)

    def skip(self):
        self.current_text = self.target_text

    def set_text(self, text):
        self.target_text = text
        self.current_text = ""


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


def draw_text_size(text, size, font_name="DTM-Sans"):
    font = pygame.font.Font(font_dictionary[font_name], size)
    text_surface = font.render(text, True, (0, 0, 0))
    text_rect = text_surface.get_rect()
    return text_rect.width, text_rect.height
