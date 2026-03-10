import pygame

from ._assets import asset_font_path

font_dictionary: dict[str, str] = {
    "default": asset_font_path("fonts/DTM-Sans.otf"),
    "attack": asset_font_path("fonts/undertale-attack-font.ttf"),
    "hud": asset_font_path("fonts/undertale-in-game-hud-font.ttf"),
}

font_cache: dict[str, pygame.font.Font] = {}


def register_font(font_name: str, font_path: str) -> None:
    font_dictionary[font_name] = font_path


def load_font(name: str, size: int) -> pygame.font.Font:
    font_cache_key = f"{name}_{size}"
    if font_cache_key not in font_cache:
        font_cache[font_cache_key] = pygame.font.Font(name, size)
    return font_cache[font_cache_key]


def draw_text(
    surface: pygame.Surface,
    text: str,
    size: int,
    color: tuple[int, int, int],
    x: float,
    y: float,
    anchor: str = "topleft",
    rotation: int = 0,
    font_name: str = "default",
) -> None:
    font = load_font(font_dictionary[font_name], size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    ix, iy = int(x), int(y)
    match anchor:
        case "center":
            text_rect.center = (ix, iy)
        case "topleft":
            text_rect.topleft = (ix, iy)
        case "midleft":
            text_rect.midleft = (ix, iy)
        case "topright":
            text_rect.topright = (ix, iy)
        case "midright":
            text_rect.midright = (ix, iy)
    if rotation != 0:
        rotated_text = pygame.transform.rotate(text_surface, rotation)
        rotated_rect = rotated_text.get_rect(center=text_rect.center)
        surface.blit(rotated_text, rotated_rect)
    else:
        surface.blit(text_surface, text_rect)


def draw_text_size(text: str, size: int, font_name: str = "default") -> tuple[int, int]:
    font = load_font(font_dictionary[font_name], size)
    text_surface = font.render(text, True, (0, 0, 0))
    text_rect = text_surface.get_rect()
    return text_rect.width, text_rect.height
