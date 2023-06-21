from modules.battle import Battle, Enemy
import pygame

from modules.util import InterpolationManager, Interpolation
from modules.constants import WIDTH


# Example battle against Papyrus using the Battle class
class PapyrusBattle(Battle):
    def __init__(self):
        super(PapyrusBattle, self).__init__()
        self.enemies = [PapyrusEnemy()]
        self.battle_box.set_encounter_text("A wild papyrus appeared!")
        InterpolationManager().add_interpolation(
            Interpolation(self.buttons[0], "y", 450, 100, 5000, Interpolation.EASE_OUT))
        InterpolationManager().add_interpolation(
            Interpolation(self.battle_box, "width", 575, 300, 2000, Interpolation.EASE_OUT))
        InterpolationManager().add_interpolation(
            Interpolation(self.battle_box, "x", 33, WIDTH / 2 - 150, 2000, Interpolation.EASE_OUT))
        InterpolationManager().add_interpolation(
            Interpolation(self.buttons[1], "y", 450, 200, 5000, Interpolation.EASE_OUT))
        InterpolationManager().add_interpolation(
            Interpolation(self.buttons[1], "x", self.buttons[1].x, self.buttons[0].x, 5000, Interpolation.EASE_OUT))

    def render(self, surface):
        super(PapyrusBattle, self).render(surface)

    def update(self, surface):
        super(PapyrusBattle, self).update(surface)

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
