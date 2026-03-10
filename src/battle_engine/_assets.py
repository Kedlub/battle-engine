from importlib.resources import files
from pathlib import Path

import pygame


def _asset_path(relative: str) -> Path:
    """Resolve an asset-relative path to a real filesystem path."""
    return Path(str(files("battle_engine.assets").joinpath(relative)))


def asset_surface(relative: str) -> pygame.Surface:
    """Load and return a pygame Surface from an asset-relative path."""
    return pygame.image.load(str(_asset_path(relative)))


def asset_font_path(relative: str) -> str:
    """Return the filesystem path (as a string) for a font asset."""
    return str(_asset_path(relative))


def asset_frames(prefix: str, extension: str = "png") -> list[pygame.Surface]:
    """Load numbered frame sequences (e.g. prefix='battle/hit/knife' -> knife1.png, knife2.png, ...)."""
    frames = []
    i = 1
    while True:
        path = _asset_path(f"{prefix}{i}.{extension}")
        if not path.exists():
            break
        frames.append(pygame.image.load(str(path)))
        i += 1
    return frames
