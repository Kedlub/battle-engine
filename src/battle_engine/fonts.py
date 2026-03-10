import pygame

from ._assets import asset_font_path

font_dictionary = {
    "default": asset_font_path("fonts/DTM-Sans.otf"),
    "attack": asset_font_path("fonts/undertale-attack-font.ttf"),
    "hud": asset_font_path("fonts/undertale-in-game-hud-font.ttf"),
}

font_cache = {}


def register_font(font_name, font_path):
    font_dictionary[font_name] = font_path


def load_font(name, size):
    font_cache_key = f"{name}_{size}"
    if font_cache_key not in font_cache:
        font_cache[font_cache_key] = pygame.font.Font(name, size)
    return font_cache[font_cache_key]


def draw_text(
    surface,
    text,
    size,
    color,
    x,
    y,
    anchor="topleft",
    rotation: int = 0,
    font_name="default",
):
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
