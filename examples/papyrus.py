import random
from modules.battle import Battle, Enemy, BattleObject, Round, MenuItem
import pygame

from modules.game import Game
from modules.util import InterpolationManager, Interpolation
from modules.constants import WIDTH, HEIGHT


# Example battle against Papyrus using the Battle class
class PapyrusBattle(Battle):
    def __init__(self):
        super(PapyrusBattle, self).__init__()
        self.tick = 0

    def select_next_round(self):
        return TestRound(self)

    def post_init(self):
        self.enemies = [PapyrusEnemy()]
        self.battle_box.set_encounter_text("A wild papyrus appeared!")
        # InterpolationManager().add_interpolation(
        #     Interpolation(self.battle_box, "y", HEIGHT, self.battle_box.y, 3000, Interpolation.EASE_OUT))
        InterpolationManager().add_interpolation(
            Interpolation(self.player_stats, "y", HEIGHT + 200, self.player_stats.y, 3000, Interpolation.EASE_OUT))
        for i, button in enumerate(self.buttons):
            InterpolationManager().add_interpolation(
                Interpolation(button, "y", HEIGHT + (300 * (i + 1)), button.y, 3000, Interpolation.EASE_OUT))

    def render(self, surface):
        super(PapyrusBattle, self).render(surface)

    def update(self, surface):
        super(PapyrusBattle, self).update(surface)
        self.tick += 1
        if self.tick == 50:
            InterpolationManager().add_interpolation(
                Interpolation(self.player_stats.player, "max_health", self.player_stats.player.max_health, 192, 3000,
                              Interpolation.EASE_OUT))

    def process_input(self, event):
        super(PapyrusBattle, self).process_input(event)


# The Papyrus enemy itself
class PapyrusEnemy(Enemy):
    def __init__(self):
        image = pygame.image.load("examples/assets/papyrus.png")
        super(PapyrusEnemy, self).__init__(image, position=(250, 40), name="Papyrus", health=100)
        self.acts = [MenuItem("Wave", self.wave)]
        self.battle = Battle()

    def wave(self):
        self.battle.battle_box.set_encounter_text("You wave at Papyrus. He waves back.")
        self.battle.end_round()

    def update(self, surface):
        super(PapyrusEnemy, self).update(surface)
        pass

    def render(self, surface):
        super(PapyrusEnemy, self).render(surface)
        pass

    def process_input(self, event):
        pass


class TestBone(BattleObject):
    def __init__(self, position=(0, 0), rotation=0):
        sprite = pygame.Surface((10, 60))
        sprite.fill((255, 255, 255))
        damage = 10
        super(TestBone, self).__init__(sprite, position, rotation, damage)

    def update(self):
        self.position = [int(self.position[0] - (150 * (Game().delta_time / 1000))), int(self.position[1])]
        super(TestBone, self).update()
        
    def render(self, surface):
        surface.blit(self.sprite, self.position)

class TestRound(Round):
    def __init__(self, battle):
        super(TestRound, self).__init__(battle)
        self.last_spawn_time = 0

    def round_update(self):
        # spawn bone every approximately 1.5 seconds, as it uses delta time
        if self.time - self.last_spawn_time >= 500:
            battle_rect = self.battle.battle_box.get_internal_rect()
            # randomly choose if it will be an upper bone or a lower bone, by selecting but battle_rect.y or battle_rect.y + battle_rect.height
            if random.randint(0, 1) == 0:
                bone = TestBone((battle_rect.x + battle_rect.width, battle_rect.y))
            else:
                bone = TestBone((battle_rect.x + battle_rect.width, battle_rect.y + battle_rect.height / 2))
            self.add_object(bone)
            self.last_spawn_time = self.time
        if self.time >= 7000:
            # Action to end the turn
            self.battle.battle_box.set_encounter_text("A lot of low quality bones fill the room.")
            self.end_turn()