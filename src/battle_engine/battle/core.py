import pygame

from ..game import GameMode, Game
from ..player import Player
from ..constants import CONFIRM_BUTTON, DISMISS_BUTTON, WIDTH
from ..drawing import draw_gradient
from ..fonts import draw_text
from .._assets import asset_surface, asset_frames
from ..interpolation import InterpolationManager, Interpolation
from .ui import PlayerStats, Button, BattleBox
from .objects import PlayerObject
from .states import ButtonSelectState, DefendingState


class Battle(GameMode):
    def __init__(self, game=Game()):
        super().__init__(game)
        self.button_data = []
        self.buttons = []
        self.current_round = None
        self.enemies = []
        self.gameStateStack = [ButtonSelectState()]
        self.selected_button = 0
        self.player_stats = PlayerStats(
            Player(name="Chara", level=19, health=90, max_health=92),
            (40, game.surface.get_height() - 80),
        )
        self.player_object = PlayerObject(50, 50, (255, 0, 0))
        self.battle_box = BattleBox(
            position=(33, game.surface.get_height() / 2 + 9), width=575, height=140
        )
        self.add_default_buttons()
        self.hit_visual = asset_frames("battle/hit/knife")
        self.objects = []

    def post_init(self):
        pass

    def add_default_buttons(self):
        self.add_button(
            "battle/button/fight0.png", "battle/button/fight1.png"
        )
        self.add_button(
            "battle/button/act0.png", "battle/button/act1.png"
        )
        self.add_button(
            "battle/button/item0.png", "battle/button/item1.png"
        )
        self.add_button(
            "battle/button/mercy0.png", "battle/button/mercy1.png"
        )
        self.create_buttons()

    def calculate_spacing(self, num_of_buttons, screen_width):
        button_space_evenly = (screen_width - num_of_buttons * Button.default_width) / (
            num_of_buttons + 1
        )
        return button_space_evenly

    def select_next_round(self):
        pass

    def attack_enemy(self, enemy):
        if enemy in self.enemies:
            from .states import TargetState

            state = TargetState(enemy)
            self.gameStateStack.append(state)

    def use_item(self, item):
        pass

    def add_button(self, inactive_texture, active_texture):
        self.button_data.append(
            {"inactive": inactive_texture, "active": active_texture}
        )

    def create_buttons(self):
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

    def init(self, game):
        self.game = game

    def render(self, surface):
        draw_gradient(surface, 25, 6, (255, 255, 255), surface.get_height() / 2)
        for button in self.buttons:
            button.render(surface)
        for enemy in self.enemies:
            enemy.render(surface)
        self.player_stats.render(surface)
        self.battle_box.render(surface)
        if self.gameStateStack:
            self.gameStateStack[-1].render(self, surface)
            for obj in self.objects:
                obj.render(surface)
            if self.gameStateStack[-1].show_soul():
                self.player_object.render(surface)

    def update(self, surface):
        if self.gameStateStack:
            self.gameStateStack[-1].update(self)
        for enemy in self.enemies:
            enemy.update(surface)
        for obj in self.objects:
            obj.update()
        self.battle_box.update()

    def select_button(self, button):
        self.buttons[self.selected_button].set_active(False)
        self.selected_button = button % len(self.buttons)
        self.buttons[self.selected_button].set_active(True)

    def unselect_all_buttons(self):
        for button in self.buttons:
            button.set_active(False)

    def is_active_state(self, state):
        return self.gameStateStack and self.gameStateStack[-1] == state

    def process_input(self, event):
        if self.gameStateStack:
            self.gameStateStack[-1].process_input(self, event)

    def add_object(self, obj):
        self.objects.append(obj)

    def end_round(self):
        if not self.current_round:
            self.current_round = self.select_next_round()
        self.gameStateStack.append(DefendingState())


class Round:
    def __init__(self, battle):
        self.objects = []
        self.time = 0
        self.active = True
        self.battle = battle

    def start(self):
        pass

    def render(self, surface):
        for obj in self.objects:
            obj.render(surface)

    def update(self):
        self.time += Game().delta_time
        self.round_update()
        self.objects = [obj for obj in self.objects if not obj.destroyed]
        for obj in self.objects:
            obj.update()

    def round_update(self):
        pass

    def process_input(self, event):
        pass

    def add_object(self, obj):
        self.objects.append(obj)

    def end_turn(self):
        self.active = False
        Game().game_mode.player_stats.player.invulnerability_time = 0
