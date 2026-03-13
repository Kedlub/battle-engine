from __future__ import annotations

import random
from typing import TYPE_CHECKING

import pygame

from ..constants import CONFIRM_BUTTON, DISMISS_BUTTON
from ..fonts import draw_text
from ..game import Game
from .ui import Menu, MenuContainer, MenuItem, TargetUI

if TYPE_CHECKING:
    from .core import Battle
    from .enemy import Enemy


class BattleState:
    def process_input(self, battle: Battle, event: pygame.event.Event) -> None:
        pass

    def update(self, battle: Battle) -> None:
        pass

    def render(self, battle: Battle, surface: pygame.Surface) -> None:
        pass

    def show_soul(self) -> bool:
        return True


class ButtonSelectState(BattleState):
    def render(self, battle: Battle, surface: pygame.Surface) -> None:
        battle.battle_box.render_text(surface)

    def update(self, battle: Battle) -> None:
        for button in battle.buttons:
            button.move_player()

    def process_input(self, battle: Battle, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                battle.select_button(battle.selected_button - 1)
            elif event.key == pygame.K_RIGHT:
                battle.select_button(battle.selected_button + 1)
            elif event.key in CONFIRM_BUTTON:
                if battle.selected_button == 0:
                    menu = Menu()
                    for enemy in battle.enemies:
                        item = MenuItem(enemy.name)
                        item.action = lambda e=enemy: battle.attack_enemy(e)
                        menu.add_item(item)
                    battle.gameStateStack.append(MenuSelectState(menu))
                elif battle.selected_button == 1:
                    menu = Menu()
                    for enemy in battle.enemies:
                        submenu = Menu()
                        for act in enemy.acts:
                            submenu.add_item(act)
                        item = MenuItem(enemy.name)
                        item.action = lambda: battle.gameStateStack.append(
                            MenuSelectState(submenu)
                        )
                        menu.add_item(item)
                    battle.gameStateStack.append(MenuSelectState(menu))
                elif battle.selected_button == 2:
                    battle.battle_box.set_encounter_text("You don't have any items.")
                elif battle.selected_button == 3:
                    battle.battle_box.set_encounter_text(
                        "You tried to spare the enemy, "
                        "but it didn't seem to understand."
                    )


class MenuSelectState(BattleState):
    def __init__(self, menu: Menu) -> None:
        battle_rect = Game().battle.battle_box.get_internal_rect()
        self.menu = MenuContainer(
            x=battle_rect.x,
            y=battle_rect.y,
            width=battle_rect.width,
            height=battle_rect.height,
        )
        self.menu.set_menu(menu)

    def render(self, battle: Battle, surface: pygame.Surface) -> None:
        self.menu.render(surface)

    def process_input(self, battle: Battle, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.menu.select_next_in_row(-1)
            elif event.key == pygame.K_RIGHT:
                self.menu.select_next_in_row(1)
            elif event.key == pygame.K_UP:
                self.menu.select_next_in_column(-1)
            elif event.key == pygame.K_DOWN:
                self.menu.select_next_in_column(1)
            elif event.key in CONFIRM_BUTTON:
                self.menu.run_selected_item()
            elif event.key == DISMISS_BUTTON:
                battle.gameStateStack.pop()


class TargetState(BattleState):
    def __init__(self, enemy: Enemy) -> None:
        super().__init__()
        self.target = TargetUI(Game().battle.battle_box, enemy.max_health)
        self.enemy = enemy
        self.target.show()

    def render(self, battle: Battle, surface: pygame.Surface) -> None:
        self.target.render(surface)

    def process_input(self, battle: Battle, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in CONFIRM_BUTTON and self.target.active:
                battle.current_round = battle.select_next_round()
                self.target.active = False
                power = self.target.get_hit_power()
                self.enemy.hit(power)

    def update(self, battle: Battle) -> None:
        self.target.update()

    def show_soul(self) -> bool:
        return False


class DefendingState(BattleState):
    def __init__(self) -> None:
        super().__init__()
        self.current_round = Game().battle.current_round

    def render(self, battle: Battle, surface: pygame.Surface) -> None:
        self.current_round.render(surface)

    def process_input(self, battle: Battle, event: pygame.event.Event) -> None:
        self.current_round.process_input(event)

    def update(self, battle: Battle) -> None:
        if not self.current_round.active:
            battle.objects.clear()
            battle.gameStateStack.pop()
            battle.gameStateStack.append(ButtonSelectState())
            return
        battle.player_object.update()
        self.current_round.update()

    def show_soul(self) -> bool:
        return True


class _DustParticle:
    """A row of pixels that has broken off and drifts upward."""

    def __init__(self, surface: pygame.Surface, x: float, y: float) -> None:
        self.surface = surface
        self.x = x
        self.y = y
        self.vx: float = random.uniform(-0.5, 0.5)
        self.vy: float = random.uniform(-1.5, -0.3)
        self.alpha: float = 255

    def update(self) -> None:
        self.x += self.vx
        self.y += self.vy
        self.alpha = max(0, self.alpha - 6)

    def render(self, surface: pygame.Surface) -> None:
        if self.alpha <= 0:
            return
        frag = self.surface.copy()
        frag.set_alpha(int(self.alpha))
        surface.blit(frag, (int(self.x), int(self.y)))


class _ShatterEffect:
    """Top-to-bottom dissolve: pixel rows break off sequentially and drift up."""

    def __init__(
        self,
        sprite: pygame.Surface,
        position: tuple[int, int],
        rows_per_group: int = 2,
        delay_per_group: float = 30,
    ) -> None:
        self.position = position
        self.rows_per_group = rows_per_group
        self.delay_per_group = delay_per_group

        w, h = sprite.get_size()
        self.width = w
        self.height = h
        # Copy sprite so we can erase rows progressively
        self.remaining = sprite.copy()
        self.particles: list[_DustParticle] = []
        self.timer: float = 0
        self.next_row: int = 0  # next row to dissolve (from top)
        self.finished = False

    def update(self, delta_time: float) -> None:
        self.timer += delta_time

        # Dissolve rows from top to bottom based on timer
        rows_to_reveal = int(self.timer / self.delay_per_group) * self.rows_per_group
        while self.next_row < min(rows_to_reveal, self.height):
            row_end = min(self.next_row + self.rows_per_group, self.height)
            row_h = row_end - self.next_row

            # Extract the row strip as a particle
            strip = pygame.Surface((self.width, row_h), pygame.SRCALPHA)
            strip.blit(
                self.remaining,
                (0, 0),
                pygame.Rect(0, self.next_row, self.width, row_h),
            )

            # Erase from the remaining sprite
            self.remaining.fill(
                (0, 0, 0, 0),
                pygame.Rect(0, self.next_row, self.width, row_h),
            )

            px = self.position[0]
            py = self.position[1] + self.next_row
            self.particles.append(_DustParticle(strip, px, py))

            self.next_row = row_end

        for p in self.particles:
            p.update()

        all_dissolved = self.next_row >= self.height
        all_faded = (
            all(p.alpha <= 0 for p in self.particles) if self.particles else False
        )
        self.finished = all_dissolved and all_faded

    def render(self, surface: pygame.Surface) -> None:
        # Draw whatever rows haven't dissolved yet
        if self.next_row < self.height:
            surface.blit(self.remaining, self.position)
        # Draw floating dust particles
        for p in self.particles:
            p.render(surface)


def _create_soul_shatter_fragments(
    sprite: pygame.Surface,
    position: tuple[int, int],
    grid_size: int = 3,
) -> list[_DustParticle]:
    """Split a small sprite (soul) into grid fragments that drift upward."""
    w, h = sprite.get_size()
    frag_w = w // grid_size
    frag_h = h // grid_size
    fragments: list[_DustParticle] = []

    for row in range(grid_size):
        for col in range(grid_size):
            rect = pygame.Rect(col * frag_w, row * frag_h, frag_w, frag_h)
            frag_surface = pygame.Surface((frag_w, frag_h), pygame.SRCALPHA)
            frag_surface.blit(sprite, (0, 0), rect)

            fx = position[0] + col * frag_w
            fy = position[1] + row * frag_h
            p = _DustParticle(frag_surface, fx, fy)
            # Soul fragments scatter outward and fall down
            p.vx = random.uniform(-2, 2)
            p.vy = random.uniform(0.5, 3)
            p.alpha = 255
            fragments.append(p)

    return fragments


class EnemyDeathState(BattleState):
    """Plays enemy death animation, shows optional death text, handles victory check."""

    PHASE_SHATTER = 0
    PHASE_TEXT = 1
    PHASE_DONE = 2

    def __init__(self, enemy: Enemy) -> None:
        super().__init__()
        self.enemy = enemy
        self.phase = self.PHASE_SHATTER
        self.shatter = _ShatterEffect(
            pygame.transform.rotate(enemy.sprite, enemy.rotation),
            enemy.position,
        )
        self.timer: float = 0

    def update(self, battle: Battle) -> None:
        delta = Game().delta_time
        self.timer += delta

        if self.phase == self.PHASE_SHATTER:
            self.shatter.update(delta)
            if self.shatter.finished:
                death_text = self.enemy.on_death()
                if death_text:
                    battle.battle_box.set_encounter_text(death_text)
                    self.phase = self.PHASE_TEXT
                else:
                    self.phase = self.PHASE_DONE

        elif self.phase == self.PHASE_TEXT:
            if battle.battle_box.is_encounter_text_finished():
                self.phase = self.PHASE_DONE

        if self.phase == self.PHASE_DONE:
            if self.enemy in battle.enemies:
                battle.enemies.remove(self.enemy)
            battle.gameStateStack.pop()
            if not battle.enemies:
                battle.on_victory()
            else:
                battle.gameStateStack.append(DefendingState())

    def render(self, battle: Battle, surface: pygame.Surface) -> None:
        if self.phase == self.PHASE_SHATTER:
            self.shatter.render(surface)
        elif self.phase == self.PHASE_TEXT:
            battle.battle_box.render_text(surface)

    def process_input(self, battle: Battle, event: pygame.event.Event) -> None:
        if self.phase == self.PHASE_TEXT and event.type == pygame.KEYDOWN:
            if (
                event.key in CONFIRM_BUTTON
                and battle.battle_box.is_encounter_text_finished()
            ):
                self.phase = self.PHASE_DONE

    def show_soul(self) -> bool:
        return False


class GameOverState(BattleState):
    """Player soul shatters, screen fades to black, GAME OVER text."""

    PHASE_SHATTER = 0
    PHASE_FADE = 1
    PHASE_TEXT = 2

    def __init__(self) -> None:
        super().__init__()
        self.phase = self.PHASE_SHATTER
        player_object = Game().battle.player_object
        soul_sprite = player_object.sprite.copy()
        soul_pos = (player_object.rect.x, player_object.rect.y)
        self.fragments = _create_soul_shatter_fragments(soul_sprite, soul_pos)
        self.timer: float = 0
        self.fade_alpha: float = 0
        self.fade_surface: pygame.Surface | None = None

    def update(self, battle: Battle) -> None:
        self.timer += Game().delta_time

        if self.phase == self.PHASE_SHATTER:
            for frag in self.fragments:
                frag.update()
            if all(f.alpha <= 0 for f in self.fragments):
                self.phase = self.PHASE_FADE
                self.timer = 0

        elif self.phase == self.PHASE_FADE:
            self.fade_alpha = min(255, self.fade_alpha + 5)
            if self.fade_alpha >= 255:
                self.phase = self.PHASE_TEXT
                self.timer = 0

        elif self.phase == self.PHASE_TEXT:
            if self.timer >= 3000:
                Game().running = False

    def render(self, battle: Battle, surface: pygame.Surface) -> None:
        if self.phase == self.PHASE_SHATTER:
            for frag in self.fragments:
                frag.render(surface)

        if self.phase in (self.PHASE_FADE, self.PHASE_TEXT):
            if self.fade_surface is None:
                self.fade_surface = pygame.Surface(surface.get_size())
                self.fade_surface.fill((0, 0, 0))
            self.fade_surface.set_alpha(int(self.fade_alpha))
            surface.blit(self.fade_surface, (0, 0))

        if self.phase == self.PHASE_TEXT:
            cx = surface.get_width() // 2
            cy = surface.get_height() // 2
            draw_text(surface, "GAME OVER", 40, (255, 0, 0), cx, cy, anchor="center")

    def show_soul(self) -> bool:
        return False


class VictoryState(BattleState):
    """Shows reward text and waits for confirm to exit battle."""

    def __init__(self, exp: int = 0, gold: int = 0) -> None:
        super().__init__()
        self.exp = exp
        self.gold = gold
        self.confirmed = False
        parts: list[str] = ["[asterisk] YOU WON!"]
        if exp > 0:
            parts.append(f"  You earned {exp} EXP.")
        if gold > 0:
            parts.append(f"  You earned {gold} gold.")
        self.reward_text = "\n".join(parts)
        self._text_set = False

    def update(self, battle: Battle) -> None:
        if not self._text_set:
            battle.battle_box.set_encounter_text(self.reward_text)
            self._text_set = True

        if self.confirmed:
            battle.gameStateStack.pop()
            battle.on_exit()

    def render(self, battle: Battle, surface: pygame.Surface) -> None:
        battle.battle_box.render_text(surface)

    def process_input(self, battle: Battle, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in CONFIRM_BUTTON:
            if battle.battle_box.is_encounter_text_finished():
                self.confirmed = True

    def show_soul(self) -> bool:
        return False
