from modules.battle import Battle, Enemy
import pygame

from modules.util import InterpolationManager, Interpolation
from modules.constants import WIDTH, HEIGHT


# Example battle against Papyrus using the Battle class
class PapyrusBattle(Battle):
    def __init__(self):
        super(PapyrusBattle, self).__init__()
        self.enemies = [PapyrusEnemy()]
        self.battle_box.set_encounter_text("A wild papyrus appeared!")
        # InterpolationManager().add_interpolation(
        #     Interpolation(self.battle_box, "y", HEIGHT, self.battle_box.y, 3000, Interpolation.EASE_OUT))
        InterpolationManager().add_interpolation(
            Interpolation(self.player_stats, "y", HEIGHT + 200, self.player_stats.y, 3000, Interpolation.EASE_OUT))
        for i, button in enumerate(self.buttons):
            InterpolationManager().add_interpolation(
                Interpolation(button, "y", HEIGHT + (300 * (i + 1)), button.y, 3000, Interpolation.EASE_OUT))
        self.tick = 0

    def render(self, surface):
        super(PapyrusBattle, self).render(surface)

    def update(self, surface):
        super(PapyrusBattle, self).update(surface)
        self.tick += 1
        if self.tick == 200:
            InterpolationManager().add_interpolation(
                Interpolation(self.player_stats.player, "max_health", self.player_stats.player.max_health, 192, 3000,
                              Interpolation.EASE_OUT))

    def process_input(self, event):
        super(PapyrusBattle, self).process_input(event)


# The Papyrus enemy itself
class PapyrusEnemy(Enemy):
    def __init__(self):
        image = pygame.image.load("examples/assets/papyrus.png")
        super(PapyrusEnemy, self).__init__(image, position=(250, 20))

    def update(self, surface):
        pass

    def render(self, surface):
        super(PapyrusEnemy, self).render(surface)
        pass

    def process_input(self, event):
        pass
