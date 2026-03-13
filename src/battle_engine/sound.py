from __future__ import annotations

from enum import Enum

import pygame

from ._assets import _asset_path
from .singleton import Singleton


class SoundCategory(Enum):
    SFX = "sfx"
    MUSIC = "music"
    TEXT = "text"


# Default sounds bundled with the engine: (engine_name, filename, category)
_DEFAULT_SOUNDS: list[tuple[str, str, SoundCategory]] = [
    ("select", "snd_squeak.wav", SoundCategory.SFX),
    ("confirm", "snd_select.wav", SoundCategory.SFX),
    ("damage", "snd_hurt1.wav", SoundCategory.SFX),
    ("hit", "snd_damage.wav", SoundCategory.SFX),
    ("heal", "snd_heal_c.wav", SoundCategory.SFX),
    ("slash", "snd_laz.wav", SoundCategory.SFX),
    ("heartbreak", "snd_break1.wav", SoundCategory.SFX),
    ("heartshatter", "snd_break2.wav", SoundCategory.SFX),
    ("battlefall", "snd_battlefall.wav", SoundCategory.SFX),
    ("levelup", "snd_levelup.wav", SoundCategory.SFX),
    ("txt_default1", "SND_TXT1.wav", SoundCategory.TEXT),
    ("txt_default2", "SND_TXT2.wav", SoundCategory.TEXT),
]


class SoundManager(metaclass=Singleton):
    def __init__(self) -> None:
        self._sounds: dict[str, pygame.mixer.Sound | None] = {}
        self._categories: dict[str, SoundCategory] = {}
        self._volumes: dict[SoundCategory, float] = {
            SoundCategory.SFX: 1.0,
            SoundCategory.MUSIC: 1.0,
            SoundCategory.TEXT: 1.0,
        }

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.set_num_channels(16)
        except pygame.error:
            pass

        self._load_defaults()

    def _load_defaults(self) -> None:
        for name, filename, category in _DEFAULT_SOUNDS:
            try:
                path = _asset_path(f"audio/{filename}")
                sound = pygame.mixer.Sound(str(path))
                self._sounds[name] = sound
                self._categories[name] = category
            except (pygame.error, FileNotFoundError):
                pass

    def register(
        self,
        name: str,
        sound: pygame.mixer.Sound | None,
        category: SoundCategory = SoundCategory.SFX,
    ) -> None:
        self._sounds[name] = sound
        self._categories[name] = category

    def register_from_file(
        self,
        name: str,
        path: str,
        category: SoundCategory = SoundCategory.SFX,
    ) -> None:
        try:
            sound = pygame.mixer.Sound(path)
            self.register(name, sound, category)
        except pygame.error:
            pass

    def play(
        self, name: str, channel: pygame.mixer.Channel | None = None
    ) -> pygame.mixer.Channel | None:
        sound = self._sounds.get(name)
        if sound is None:
            return None
        category = self._categories.get(name, SoundCategory.SFX)
        volume = self._volumes.get(category, 1.0)
        sound.set_volume(volume)
        try:
            if channel is not None:
                channel.play(sound)
                return channel
            return sound.play()
        except pygame.error:
            return None

    def set_volume(self, category: SoundCategory, volume: float) -> None:
        self._volumes[category] = max(0.0, min(1.0, volume))

    def get_volume(self, category: SoundCategory) -> float:
        return self._volumes.get(category, 1.0)

    def play_music(self, path: str, loops: int = -1, fade_ms: int = 0) -> None:
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self._volumes[SoundCategory.MUSIC])
            pygame.mixer.music.play(loops, fade_ms=fade_ms)
        except pygame.error:
            pass

    def stop_music(self, fade_ms: int = 0) -> None:
        try:
            if fade_ms > 0:
                pygame.mixer.music.fadeout(fade_ms)
            else:
                pygame.mixer.music.stop()
        except pygame.error:
            pass

    def pause_music(self) -> None:
        try:
            pygame.mixer.music.pause()
        except pygame.error:
            pass

    def unpause_music(self) -> None:
        try:
            pygame.mixer.music.unpause()
        except pygame.error:
            pass
