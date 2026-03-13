from __future__ import annotations

import pygame

from .._assets import asset_frames
from ..drawing import draw_gradient
from ..game import Game, GameMode
from ..player import Player
from .enemy import Enemy
from .objects import BattleObject, PlayerObject
from .states import (
    BattleState,
    ButtonSelectState,
    DefendingState,
    GameOverState,
    VictoryState,
)
from .ui import BattleBox, Button, PlayerStats


class Battle(GameMode):
    def __init__(self, game: Game = Game()) -> None:
        super().__init__(game)
        self.button_data: list[dict[str, str]] = []
        self.buttons: list[Button] = []
        self.current_round: Round | None = None
        self.enemies: list[Enemy] = []
        self.gameStateStack: list[BattleState] = [ButtonSelectState()]
        self.selected_button: int = 0
        self.player_stats = PlayerStats(
            Player(name="Chara", level=19, health=90, max_health=92),
            (40, game.surface.get_height() - 80),
        )
        self.player_object = PlayerObject(50, 50, (255, 0, 0))
        self.battle_box = BattleBox(
            position=(33, game.surface.get_height() / 2 + 9), width=575, height=140
        )
        self.add_default_buttons()
        self.hit_visual: list[pygame.Surface] = asset_frames("battle/hit/knife")
        self.objects: list[BattleObject] = []
        self._defeated_enemies: list[Enemy] = []
        self._game_over: bool = False

    def post_init(self) -> None:
        pass

    def add_default_buttons(self) -> None:
        self.add_button("battle/button/fight0.png", "battle/button/fight1.png")
        self.add_button("battle/button/act0.png", "battle/button/act1.png")
        self.add_button("battle/button/item0.png", "battle/button/item1.png")
        self.add_button("battle/button/mercy0.png", "battle/button/mercy1.png")
        self.create_buttons()

    def calculate_spacing(self, num_of_buttons: int, screen_width: int) -> float:
        button_space_evenly = (screen_width - num_of_buttons * Button.default_width) / (
            num_of_buttons + 1
        )
        return button_space_evenly

    def select_next_round(self) -> Round | None:
        pass

    def attack_enemy(self, enemy: Enemy) -> None:
        if enemy in self.enemies:
            from .states import TargetState

            state = TargetState(enemy)
            self.gameStateStack.append(state)

    def on_victory(self) -> None:
        """Called when all enemies are defeated. Override for custom behavior."""
        total_exp = sum(e.exp_reward for e in self._defeated_enemies)
        total_gold = sum(e.gold_reward for e in self._defeated_enemies)
        self.gameStateStack.append(VictoryState(total_exp, total_gold))

    def on_exit(self) -> None:
        """Called to leave the battle. Override to transition elsewhere."""
        Game().running = False

    def use_item(self, item: str) -> None:
        pass

    def add_button(self, inactive_texture: str, active_texture: str) -> None:
        self.button_data.append(
            {"inactive": inactive_texture, "active": active_texture}
        )

    def create_buttons(self) -> None:
        screen_width = self.game.surface.get_width()
        screen_height = self.game.surface.get_height()
        num_buttons = len(self.button_data)
        button_spacing = self.calculate_spacing(num_buttons, screen_width)

        for i, data in enumerate(self.button_data):
            position_x = button_spacing + (Button.default_width + button_spacing) * i
            position_y = screen_height - 47
            position = (position_x, position_y)
            self.buttons.append(Button(data["inactive"], data["active"], position))

        self.select_button(0)

    def init(self, game: Game) -> None:
        self.game = game

    def render(self, surface: pygame.Surface) -> None:
        draw_gradient(surface, 25, 6, (255, 255, 255), surface.get_height() / 2)
        for button in self.buttons:
            button.render(surface)
        for enemy in self.enemies:
            if not enemy.dead:
                enemy.render(surface)
        self.player_stats.render(surface)
        self.battle_box.render(surface)
        if self.gameStateStack:
            self.gameStateStack[-1].render(self, surface)
            for obj in self.objects:
                obj.render(surface)
            if self.gameStateStack[-1].show_soul():
                self.player_object.render(surface)

    def update(self, surface: pygame.Surface) -> None:
        if self.gameStateStack:
            self.gameStateStack[-1].update(self)
        for enemy in self.enemies:
            enemy.update(surface)
        for obj in self.objects:
            obj.update()
        self.battle_box.update()

        # Track defeated enemies for reward calculation
        for enemy in self.enemies:
            if enemy.dead and enemy not in self._defeated_enemies:
                self._defeated_enemies.append(enemy)

        # Central player death check (takes priority over everything)
        if (
            not self._game_over
            and self.player_stats.player.health <= 0
            and not isinstance(self.gameStateStack[-1], GameOverState)
        ):
            self._game_over = True
            self.gameStateStack.append(GameOverState())

    def select_button(self, button: int) -> None:
        self.buttons[self.selected_button].set_active(False)
        self.selected_button = button % len(self.buttons)
        self.buttons[self.selected_button].set_active(True)

    def unselect_all_buttons(self) -> None:
        for button in self.buttons:
            button.set_active(False)

    def is_active_state(self, state: BattleState) -> bool:
        return bool(self.gameStateStack and self.gameStateStack[-1] == state)

    def process_input(self, event: pygame.event.Event) -> None:
        if self.gameStateStack:
            self.gameStateStack[-1].process_input(self, event)

    def add_object(self, obj: BattleObject) -> None:
        self.objects.append(obj)

    def end_round(self) -> None:
        if not self.current_round:
            self.current_round = self.select_next_round()
        self.gameStateStack.append(DefendingState())


class Round:
    def __init__(self, battle: Battle) -> None:
        self.objects: list[BattleObject] = []
        self.time: float = 0
        self.active: bool = True
        self.battle = battle

    def start(self) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        for obj in self.objects:
            obj.render(surface)

    def update(self) -> None:
        self.time += Game().delta_time
        self.round_update()
        self.objects = [obj for obj in self.objects if not obj.destroyed]
        for obj in self.objects:
            obj.update()

    def round_update(self) -> None:
        pass

    def process_input(self, event: pygame.event.Event) -> None:
        pass

    def add_object(self, obj: BattleObject) -> None:
        self.objects.append(obj)

    def end_turn(self) -> None:
        self.active = False
        Game().battle.player_stats.player.invulnerability_time = 0
