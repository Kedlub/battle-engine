import sys
import os
import pygame


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


import re


class StyledText:
    def __init__(self, text, color, font_name, font_size, x, y, char_spacing=0):
        self.text = text
        self.color = color
        self.font_name = font_name
        self.font_size = font_size
        self.x = x
        self.y = y
        self.char_spacing = char_spacing


class ProgressiveText:
    def __init__(self, target_text="", max_width=100, font_name="default", font_size=27, x=0, y=0, tick_length=2):
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
        self.char_spacing = 2
        self.instant_command = False
        self.asterisk = False
        self.set_text(target_text)

    def preprocess_target_text(self, target_text):
        index = 0
        command_positions = {}
        clean_text = ""

        while index < len(target_text):
            if target_text[index] == "[":
                command_start = index
                command_end = target_text.find("]", command_start)

                if command_end != -1:
                    commands = target_text[command_start + 1:command_end].split('][')

                    if len(clean_text) not in command_positions:
                        command_positions[len(clean_text)] = []

                    for cmd in commands:
                        command_positions[len(clean_text)].append(cmd)

                    index = command_end + 1
                    continue

            clean_text += target_text[index]
            index += 1

        return command_positions, clean_text

    def update(self):
        if len(self.current_text) < len(self.target_text_clean):
            self.finished = False
            self.tick += 1
            if self.tick >= self.tick_length or self.instant_command:
                self.current_text += self.target_text_clean[len(self.current_text)]
                self.tick = 0
        elif not self.finished:
            self.finished = True

    def draw(self, surface):
        styled_texts = []
        x_offset = self.x
        y_offset = self.y
        current_color = self.color
        current_font_name = self.font_name
        current_char_spacing = self.char_spacing
        line_start_idx = 0

        for idx, char in enumerate(self.current_text):
            cmd_list = self.target_command_positions.get(idx)

            if cmd_list:
                for cmd in cmd_list:
                    key, value = cmd.split(':', 1) if ':' in cmd else (cmd, None)

                    if key == 'color':
                        current_color = tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))
                    elif key == 'font':
                        current_font_name = value
                    elif key == 'charspacing':
                        current_char_spacing = int(value)

            char_width, char_height = draw_text_size(char, self.font_size, font_name=current_font_name)
            x_offset += char_width + current_char_spacing

            if char == ' ':
                word_end_idx = self.current_text.find(' ', idx + 1)
                next_word = self.current_text[idx + 1: word_end_idx if word_end_idx != -1 else len(self.current_text)]
                next_word_width = draw_text_size(next_word, self.font_size, font_name=current_font_name)[0]

                if x_offset + next_word_width > self.max_width:
                    x_offset = self.x
                    y_offset += char_height

            styled_text = StyledText(char, current_color, current_font_name, self.font_size, x_offset, y_offset)
            styled_texts.append(styled_text)

        for styled_text in styled_texts:
            draw_text(surface, styled_text.text, styled_text.font_size, styled_text.color, styled_text.x, styled_text.y,
                      font_name=styled_text.font_name)

    def skip(self):
        self.current_text = self.target_text

    def set_text(self, text):
        self.target_text = text
        self.current_text = ""

        if "[instant]" in self.target_text:
            self.instant_command = True
            self.target_text = self.target_text.replace("[instant]", "")

        if "[asterisk]" in self.target_text:
            self.asterisk = True
            self.target_text = self.target_text.replace("[asterisk]", "")

        self.target_command_positions, self.target_text_clean = self.preprocess_target_text(self.target_text)

        if self.instant_command:
            self.current_text = self.target_text_clean


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
    "default": resource_path("assets/fonts/DTM-Sans.otf"),
    "attack": resource_path("assets/fonts/undertale-attack-font.ttf"),
    "hud": resource_path("assets/fonts/undertale-in-game-hud-font.ttf")
}

font_cache = {}


def register_font(font_name, font_path):
    font_dictionary[font_name] = resource_path(font_path)


def load_font(name, size):
    font_cache_key = f"{name}_{size}"
    if font_cache_key not in font_cache:
        font_cache[font_cache_key] = pygame.font.Font(name, size)
    return font_cache[font_cache_key]


def draw_text(surface, text, size, color, x, y, anchor="topleft", rotation: int = 0, font_name="default"):
    font = load_font(font_dictionary[font_name], size)
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


def draw_text_size(text, size, font_name="default"):
    font = load_font(font_dictionary[font_name], size)
    text_surface = font.render(text, True, (0, 0, 0))
    text_rect = text_surface.get_rect()
    return text_rect.width, text_rect.height
