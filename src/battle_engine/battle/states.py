from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from ..constants import CONFIRM_BUTTON, DISMISS_BUTTON
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
            battle.gameStateStack.pop()
            battle.gameStateStack.append(ButtonSelectState())
            return
        battle.player_object.update()
        self.current_round.update()

    def show_soul(self) -> bool:
        return True
