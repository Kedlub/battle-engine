from modules.battle import Battle, Enemy
import pygame


# Example battle against Papyrus using the Battle class
class PapyrusBattle(Battle):
    def __init__(self):
        super(PapyrusBattle, self).__init__()
        self.enemies = [PapyrusEnemy()]

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
