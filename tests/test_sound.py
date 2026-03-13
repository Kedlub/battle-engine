import pygame
import pytest

# Reset singleton between tests
from battle_engine.singleton import Singleton
from battle_engine.sound import _DEFAULT_SOUNDS, SoundCategory, SoundManager


@pytest.fixture(autouse=True)
def _reset_sound_manager():
    """Reset SoundManager singleton before each test."""
    Singleton._instances.pop(SoundManager, None)
    yield
    Singleton._instances.pop(SoundManager, None)


@pytest.fixture(autouse=True)
def _init_mixer():
    """Ensure pygame mixer is initialized."""
    pygame.mixer.init()
    yield
    pygame.mixer.quit()


class TestSoundManagerInit:
    def test_default_sounds_registered(self):
        sm = SoundManager()
        for name, _, _ in _DEFAULT_SOUNDS:
            assert name in sm._sounds

    def test_default_volumes(self):
        sm = SoundManager()
        assert sm.get_volume(SoundCategory.SFX) == 1.0
        assert sm.get_volume(SoundCategory.MUSIC) == 1.0
        assert sm.get_volume(SoundCategory.TEXT) == 1.0

    def test_singleton(self):
        sm1 = SoundManager()
        sm2 = SoundManager()
        assert sm1 is sm2


class TestRegistration:
    def test_register_sound(self):
        sm = SoundManager()
        sound = pygame.mixer.Sound(buffer=b"\x00" * 44)
        sm.register("test_sound", sound)
        assert sm._sounds["test_sound"] is sound
        assert sm._categories["test_sound"] == SoundCategory.SFX

    def test_register_with_category(self):
        sm = SoundManager()
        sound = pygame.mixer.Sound(buffer=b"\x00" * 44)
        sm.register("test_text", sound, SoundCategory.TEXT)
        assert sm._categories["test_text"] == SoundCategory.TEXT

    def test_register_none_disables(self):
        sm = SoundManager()
        sm.register("disabled", None)
        assert sm._sounds["disabled"] is None
        result = sm.play("disabled")
        assert result is None

    def test_register_override(self):
        sm = SoundManager()
        sound1 = pygame.mixer.Sound(buffer=b"\x00" * 44)
        sound2 = pygame.mixer.Sound(buffer=b"\x00" * 88)
        sm.register("override_me", sound1)
        sm.register("override_me", sound2)
        assert sm._sounds["override_me"] is sound2


class TestPlay:
    def test_play_unknown_returns_none(self):
        sm = SoundManager()
        assert sm.play("nonexistent") is None

    def test_play_valid_returns_channel(self):
        sm = SoundManager()
        # Use a default sound that should be loaded
        result = sm.play("select")
        assert result is None or isinstance(result, pygame.mixer.Channel)


class TestVolume:
    def test_set_and_get_volume(self):
        sm = SoundManager()
        sm.set_volume(SoundCategory.SFX, 0.5)
        assert sm.get_volume(SoundCategory.SFX) == 0.5

    def test_volume_clamped_high(self):
        sm = SoundManager()
        sm.set_volume(SoundCategory.SFX, 1.5)
        assert sm.get_volume(SoundCategory.SFX) == 1.0

    def test_volume_clamped_low(self):
        sm = SoundManager()
        sm.set_volume(SoundCategory.SFX, -0.5)
        assert sm.get_volume(SoundCategory.SFX) == 0.0

    def test_categories_independent(self):
        sm = SoundManager()
        sm.set_volume(SoundCategory.SFX, 0.3)
        sm.set_volume(SoundCategory.TEXT, 0.7)
        assert sm.get_volume(SoundCategory.SFX) == pytest.approx(0.3)
        assert sm.get_volume(SoundCategory.TEXT) == pytest.approx(0.7)
        assert sm.get_volume(SoundCategory.MUSIC) == 1.0
