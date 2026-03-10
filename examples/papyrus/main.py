import random
from pathlib import Path

import pygame

from battle_engine import (
    HEIGHT,
    Battle,
    BattleObject,
    Enemy,
    Game,
    Interpolation,
    InterpolationManager,
    MenuItem,
    Round,
)

_ASSETS_DIR = Path(__file__).parent / "assets"


class PapyrusBattle(Battle):
    def __init__(self):
        super().__init__()
        self.tick = 0

    def select_next_round(self):
        return TestRound(self)

    def post_init(self):
        self.enemies = [PapyrusEnemy()]
        self.battle_box.set_encounter_text("A wild papyrus appeared!")
        InterpolationManager().add_interpolation(
            Interpolation(
                self.player_stats,
                "y",
                HEIGHT + 200,
                self.player_stats.y,
                3000,
                Interpolation.EASE_OUT,
            )
        )
        for i, button in enumerate(self.buttons):
            InterpolationManager().add_interpolation(
                Interpolation(
                    button,
                    "y",
                    HEIGHT + (300 * (i + 1)),
                    button.y,
                    3000,
                    Interpolation.EASE_OUT,
                )
            )

    def render(self, surface):
        super().render(surface)

    def update(self, surface):
        super().update(surface)
        self.tick += 1
        if self.tick == 50:
            InterpolationManager().add_interpolation(
                Interpolation(
                    self.player_stats.player,
                    "max_health",
                    self.player_stats.player.max_health,
                    192,
                    3000,
                    Interpolation.EASE_OUT,
                )
            )

    def process_input(self, event):
        super().process_input(event)


class PapyrusEnemy(Enemy):
    def __init__(self):
        image = pygame.image.load(str(_ASSETS_DIR / "papyrus.png"))
        super().__init__(
            image, position=(250, 40), name="Papyrus", health=100
        )
        self.acts = [MenuItem("Wave", self.wave)]
        self.battle = Battle()

    def wave(self):
        self.battle.battle_box.set_encounter_text("You wave at Papyrus. He waves back.")
        self.battle.end_round()

    def update(self, surface):
        super().update(surface)

    def render(self, surface):
        super().render(surface)


class TestBone(BattleObject):
    def __init__(self, position=(0, 0), rotation=0):
        sprite = pygame.Surface((10, 60))
        sprite.fill((255, 255, 255))
        damage = 10
        super().__init__(sprite, position, rotation, damage)

    def update(self):
        self.position = [
            int(self.position[0] - (150 * (Game().delta_time / 1000))),
            int(self.position[1]),
        ]
        super().update()

    def render(self, surface):
        surface.blit(self.sprite, self.position)


class TestRound(Round):
    def __init__(self, battle):
        super().__init__(battle)
        self.last_spawn_time = 0

    def round_update(self):
        if self.time - self.last_spawn_time >= 500:
            battle_rect = self.battle.battle_box.get_internal_rect()
            if random.randint(0, 1) == 0:
                bone = TestBone((battle_rect.x + battle_rect.width, battle_rect.y))
            else:
                bone = TestBone(
                    (
                        battle_rect.x + battle_rect.width,
                        battle_rect.y + battle_rect.height / 2,
                    )
                )
            self.add_object(bone)
            self.last_spawn_time = self.time
        if self.time >= 7000:
            self.battle.battle_box.set_encounter_text(
                "A lot of low quality bones fill the room."
            )
            self.end_turn()
