import pygame
import enum
from modules.game import GameMode
from modules.player import Player
from modules.util import resource_path, draw_gradient, draw_text


class BattleState():
    BUTTON_SELECT = 1
    MENU_SELECT = 2
    ATTACKING = 3
    DEFENDING = 4
    DIALOGUE = 5


class Battle(GameMode):
    def __init__(self, game):
        super().__init__(game)
        self.button_data = []
        self.buttons = []
        self.state = BattleState.BUTTON_SELECT
        self.selected_button = 0
        self.player_stats = PlayerStats(Player("Arzyk", 50, 150, 0, 30, 30, 5, []),
                                        (35, game.surface.get_height() - 100))
        self.add_default_buttons()

    def add_default_buttons(self):
        self.add_button("assets/battle/button/fight0.png", "assets/battle/button/fight1.png")
        self.add_button("assets/battle/button/act0.png", "assets/battle/button/act1.png")
        self.add_button("assets/battle/button/item0.png", "assets/battle/button/item1.png")
        self.add_button("assets/battle/button/mercy0.png", "assets/battle/button/mercy1.png")
        self.create_buttons()

    def calculate_spacing(self, num_of_buttons, screen_width):
        button_space_evenly = (screen_width - num_of_buttons * Button.default_width) / (num_of_buttons + 1)
        return button_space_evenly

    def add_button(self, inactive_texture, active_texture):
        self.button_data.append({"inactive": inactive_texture, "active": active_texture})

    def create_buttons(self):
        screen_width = self.game.surface.get_width()
        screen_height = self.game.surface.get_height()
        num_buttons = len(self.button_data)
        button_spacing = self.calculate_spacing(num_buttons, screen_width)

        for i, data in enumerate(self.button_data):
            position_x = button_spacing + (Button.default_width + button_spacing) * i
            position_y = screen_height - 60
            position = (position_x, position_y)
            self.buttons.append(Button(data["inactive"], data["active"], position))

        self.select_button(0)

    def init(self, game):
        self.game = game

    def render(self, surface):
        # Implement Battle mode rendering here
        draw_gradient(surface, 25, 6, (255, 255, 255), surface.get_height() / 2)
        for button in self.buttons:
            button.render(surface)
        self.player_stats.render(surface)
        pass

    def update(self, surface):
        pass

    def select_button(self, button):
        self.buttons[self.selected_button].set_active(False)
        self.selected_button = button % len(self.buttons)
        self.buttons[self.selected_button].set_active(True)

    def process_input(self, event):
        # Implement input handling in Battle mode here
        match self.state:
            case BattleState.BUTTON_SELECT:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.select_button(self.selected_button - 1)
                    elif event.key == pygame.K_RIGHT:
                        self.select_button(self.selected_button + 1)
                pass
            case _:
                pass
        pass


class GUIElement:
    def __init__(self, position=(0, 0), rotation=0):
        self.position = position
        self.rotation = rotation

    def set_position(self, x, y):
        self.position = (x, y)

    def set_rotation(self, rotation):
        self.rotation = rotation

    def interpolate(self, target_position, target_rotation, t):
        x1, y1 = self.position
        x2, y2 = target_position
        self.set_position(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t)
        self.set_rotation(self.rotation + (target_rotation - self.rotation) * t)

    def update(self):
        raise NotImplementedError("update method should be implemented in derived classes")

    def render(self, screen):
        raise NotImplementedError("render method should be implemented in derived classes")


class PlayerStats(GUIElement):
    def __init__(self, player, position):
        super().__init__(position)
        self.player = player
        self.width = 570
        self.height = 25

    def render(self, surface):
        # pygame.draw.rect(surface, (0, 120, 120), (self.position[0], self.position[1], self.width, self.height))
        draw_text(surface, self.player.name, 16, (255, 255, 255), self.position[0], self.position[1] - 5,
                  font_name="UT-HUD")
        draw_text(surface, f"Lv. {str(self.player.level)}", 16, (255, 255, 255), self.position[0] + 100,
                  self.position[1] - 5, font_name="UT-HUD")

        hp_bar_full = (255, 0, 0)
        hp_bar_current = (255, 255, 0)

        base_hpbar_pos = self.position[0] + 250

        pygame.draw.rect(surface, hp_bar_full,
                         (base_hpbar_pos, self.position[1], self.player.max_health, self.height))
        pygame.draw.rect(surface, hp_bar_current,
                         (base_hpbar_pos, self.position[1], self.player.health, self.height))

        draw_text(surface, f"{str(self.player.health)}/{str(self.player.max_health)}", 12, (255, 255, 255),
                  base_hpbar_pos + self.player.max_health + 10, self.position[1], font_name="UT-HUD")

    def update(self):
        pass


class Button(GUIElement):
    default_width = 110

    def __init__(self, inactive_texture, active_texture, position=(0, 0), rotation=0):
        super().__init__(position, rotation)
        self.inactive_texture = pygame.image.load(resource_path(inactive_texture))
        self.active_texture = pygame.image.load(resource_path(active_texture))
        self.current_texture = self.inactive_texture

    def set_active(self, active):
        if active:
            self.current_texture = self.active_texture
        else:
            self.current_texture = self.inactive_texture

    def render(self, screen):
        image = pygame.transform.rotate(self.current_texture, self.rotation)
        screen.blit(image, self.position)
