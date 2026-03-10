import pygame

from ..game import Game
from ..interpolation import InterpolationManager, Interpolation
from .ui import HitVisual


class Enemy:
    def __init__(self, sprite, name="TestMon", position=(0, 0), rotation=0, health=20):
        self.sprite = sprite
        self.position = position
        self.base_position = position
        self.rotation = rotation
        self.health = health
        self.current_health = health
        self.max_health = health
        self.name = name
        self.acts = []
        self.hit_power = 0
        self.shake_ticks = 0
        self.being_attacked = False
        self.hit_visual = HitVisual(5, Game().game_mode.hit_visual)
        self.healthbar_ticks = 0
        rect = self.get_rect()
        self.health_bar_width = 200
        self.health_bar_height = 15
        self.health_bar_position = (
            rect.centerx - self.health_bar_width / 2,
            rect.y - self.health_bar_height - 5,
        )

    def get_rect(self):
        width, height = self.sprite.get_size()
        return pygame.Rect(self.position[0], self.position[1], width, height)

    def add_act(self, name, func):
        self.acts.append({name: func})

    def update(self, surface):
        if self.being_attacked:
            if not self.hit_visual.active and not self.shake_ticks:
                power_ratio = min(self.hit_power / float(self.max_health), 1.0)
                self.shake_dist = int(power_ratio * (self.sprite.get_width() / 2))
                self.shake_speed = max(1, int(20 * power_ratio))
                self.shake_ticks = 6 * self.shake_speed
                self.health -= self.hit_power
                InterpolationManager().add_interpolation(
                    Interpolation(
                        self, "current_health", self.current_health, self.health, 1000
                    )
                )
                self.healthbar_ticks = 100
            elif self.hit_visual.active:
                self.hit_visual.update()

        if self.shake_ticks > 0:
            self.shake_ticks -= 1
            if self.shake_ticks % self.shake_speed == 0:
                sign = 1 if (self.shake_ticks / self.shake_speed) % 2 == 0 else -1
                shake_offset = sign * self.shake_dist
                self.position = (
                    self.base_position[0] + shake_offset,
                    self.base_position[1],
                )
                self.shake_dist *= 0.9
            if self.shake_ticks == 0:
                self.shake_dist = 0
                self.position = self.base_position
                self.being_attacked = False
                from .states import DefendingState

                Game().game_mode.gameStateStack[-1].target.hide()
                Game().game_mode.gameStateStack.append(DefendingState())

    def hit(self, damage):
        self.being_attacked = True
        self.hit_visual.activate(self.get_rect())
        self.hit_power = damage

    def render(self, surface):
        surface.blit(pygame.transform.rotate(self.sprite, self.rotation), self.position)
        if self.hit_visual.active:
            self.hit_visual.render(surface)
        if self.healthbar_ticks > 0:
            self.healthbar_ticks -= 1
            self.draw_health_bar(surface)

    def draw_health_bar(self, surface):
        health_bar_x = self.health_bar_position[0]
        health_bar_y = self.health_bar_position[1]
        max_health_bar_color = (255, 0, 0)
        current_health_bar_color = (0, 255, 0)

        max_health_width = self.health_bar_width
        current_health_width = (
            self.current_health / self.max_health
        ) * self.health_bar_width

        pygame.draw.rect(
            surface,
            max_health_bar_color,
            (health_bar_x, health_bar_y, max_health_width, self.health_bar_height),
        )

        pygame.draw.rect(
            surface,
            current_health_bar_color,
            (health_bar_x, health_bar_y, current_health_width, self.health_bar_height),
        )
