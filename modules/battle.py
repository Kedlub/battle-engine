import pygame
import enum

from modules.constants import CONFIRM_BUTTON
from modules.game import GameMode, Game
from modules.player import Player
from modules.util import resource_path, draw_gradient, draw_text, ProgressiveText, Singleton


class BattleState():
    BUTTON_SELECT = 1
    MENU_SELECT = 2
    ATTACKING = 3
    DEFENDING = 4
    DIALOGUE = 5


class Battle(GameMode):
    def __init__(self, game=Game()):
        super().__init__(game)
        self.button_data = []
        self.buttons = []
        self.rounds = []
        self.enemies = []
        self.state = BattleState.BUTTON_SELECT
        self.selected_button = 0
        self.player_stats = PlayerStats(Player(name="Chara", level=19, health=90, max_health=92),
                                        (40, game.surface.get_height() - 80))
        self.player_object = PlayerObject(50, 50, (255, 0, 0))
        self.battle_box = BattleBox(position=(33, game.surface.get_height() / 2 + 9), width=575, height=140)
        battle_rect = self.battle_box.get_internal_rect()
        self.text = ProgressiveText(
            "Hello, I am your enemy. This is a very long sentence to test out the automatic line break that should work here.",
            battle_rect.width - 10, "DTM-Sans", 27, battle_rect.x + 10,
            battle_rect.y + 10, 2)
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
            position_y = screen_height - 47
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
        for enemy in self.enemies:
            enemy.render(surface)
        self.player_stats.render(surface)
        self.battle_box.render(surface)
        self.text.draw(surface)
        self.player_object.render(surface)
        pass

    def update(self, surface):
        self.text.update()
        self.player_object.update()
        if self.text.finished and self.text.target_text != "Now prepare to die...":
            self.text.set_text("Now prepare to die...")
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
                    elif event.key in CONFIRM_BUTTON:
                        # confirm the selection
                        print("confirmed")
                        pass
                pass
            case BattleState.DEFENDING:
                pass
            case _:
                pass
        pass


class Enemy:
    def __init__(self, sprite, name="TestMon", position=(0, 0), rotation=0, health=20):
        self.sprite = sprite
        self.position = position
        self.rotation = rotation
        self.health = health
        self.max_health = health
        self.name = name
        self.acts = []

    def add_act(self, name, func):
        self.acts.append({name: func})

    def update(self, surface):
        pass

    def render(self, surface):
        # Base implementation of render using only one sprite, enemies don't have to use this one sprite,
        # it can instead use different sprites for different body part
        surface.blit(pygame.transform.rotate(self.sprite, self.rotation), self.position)
        pass

    def process_input(self, event):
        pass

    def check(self):
        pass


class PlayerObject(pygame.sprite.Sprite, metaclass=Singleton):
    def __init__(self, x=0, y=0, color=(255, 0, 0)):
        super().__init__()
        self.image = pygame.image.load(resource_path("assets/battle/soul/soul.png"))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.rotation = 0
        self.speed = 5
        self.game = Game()
        self.set_color(color)

    def set_color(self, color):
        new_surface = pygame.Surface(self.image.get_size())
        new_surface.fill(color)
        new_surface.set_colorkey((0, 0, 0))
        new_surface.set_alpha(self.image.get_alpha())
        new_surface.blit(self.image, (0, 0), None, pygame.BLEND_RGBA_MULT)
        self.image = new_surface.convert_alpha()

    def set_position(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def set_rotation(self, angle):
        self.rotation = angle

    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

    def rotate(self, angle):
        self.rotation += angle

    def update(self):
        if self.game.game_mode.state == BattleState.DEFENDING:
            if self.game.keys_pressed[pygame.K_UP]:
                self.move(0, -1)
            if self.game.keys_pressed[pygame.K_LEFT]:
                self.move(-1, 0)
            if self.game.keys_pressed[pygame.K_DOWN]:
                self.move(0, 1)
            if self.game.keys_pressed[pygame.K_RIGHT]:
                self.move(1, 0)
            if self.game.keys_pressed[pygame.K_q]:
                self.rotate(-5)
            if self.game.keys_pressed[pygame.K_e]:
                self.rotate(5)

    def render(self, surface):
        rotated = pygame.transform.rotate(self.image, self.rotation)
        rotated_rect = rotated.get_rect(center=self.rect.center)
        surface.blit(rotated, rotated_rect)

    def process_input(self, event):
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
        self.height = 21
        self.hp_sprite = pygame.image.load('assets/battle/hp.png')
        self.karma_sprite = pygame.image.load('assets/battle/karma.png')

    def render(self, surface):
        y_offset = 6
        # pygame.draw.rect(surface, (0, 120, 120), (self.position[0], self.position[1], self.width, self.height))
        draw_text(surface, self.player.name, 15, (255, 255, 255), self.position[0], self.position[1] - y_offset,
                  font_name="UT-HUD")
        draw_text(surface, f"LV {str(self.player.level)}", 15, (255, 255, 255), self.position[0] + 100,
                  self.position[1] - y_offset, font_name="UT-HUD")

        hp_bar_full = (192, 0, 0)
        hp_bar_current = (255, 255, 0)

        base_hpbar_pos = self.position[0] + 250

        surface.blit(self.hp_sprite, (base_hpbar_pos - self.hp_sprite.get_width() - 10, self.position[1] + 5))

        pygame.draw.rect(surface, hp_bar_full,
                         (base_hpbar_pos, self.position[1], self.player.max_health, self.height))
        pygame.draw.rect(surface, hp_bar_current,
                         (base_hpbar_pos, self.position[1], self.player.health, self.height))

        draw_text(surface, f"{str(self.player.health)} / {str(self.player.max_health)}", 15, (255, 255, 255),
                  base_hpbar_pos + self.player.max_health + 10, self.position[1] - y_offset, font_name="UT-HUD")

    def update(self):
        pass


class Button(GUIElement):
    default_width = 110

    def __init__(self, inactive_texture, active_texture, position=(0, 0), rotation=0):
        super().__init__(position, rotation)
        self.inactive_texture = pygame.image.load(resource_path(inactive_texture))
        self.active_texture = pygame.image.load(resource_path(active_texture))
        self.height = self.active_texture.get_height()
        self.current_texture = self.inactive_texture

    def set_active(self, active):
        if active:
            player_object = PlayerObject()
            player_object.set_position(self.position[0] + 10, self.position[1] + self.height / 2 - 8)
            self.current_texture = self.active_texture
        else:
            self.current_texture = self.inactive_texture

    def render(self, screen):
        image = pygame.transform.rotate(self.current_texture, self.rotation)
        screen.blit(image, self.position)


class BattleBox(GUIElement):
    def __init__(self, position=(0, 0), width=200, height=100, rotation=0):
        super().__init__(position, rotation)
        self.width = width
        self.height = height
        self.border_thickness = 5
        self.background_color = (0, 0, 0)
        self.border_color = (255, 255, 255)

    def render(self, surface):
        pygame.draw.rect(surface, self.background_color, (self.position[0], self.position[1], self.width, self.height))
        pygame.draw.rect(surface, self.border_color, (self.position[0], self.position[1], self.width, self.height),
                         self.border_thickness)

    def update(self):
        pass

    def get_internal_rect(self):
        return pygame.Rect(self.position[0] + self.border_thickness, self.position[1] + self.border_thickness,
                           self.width - 2 * self.border_thickness, self.height - 2 * self.border_thickness)


class MenuItem:
    def __init__(self, text, action=None, params=None, submenu=None):
        self.text = text
        self.action = action
        self.params = params
        self.submenu = submenu

    def execute(self):
        if self.action is not None and self.params is not None:
            self.action(*self.params)
        elif self.submenu is not None:
            self.submenu.display()


class Menu:
    def __init__(self, title, items=None, parent_menu=None):
        self.title = title
        self.items = items if items is not None else []
        self.parent_menu = parent_menu

    def add_item(self, item):
        self.items.append(item)

    def display(self):
        print(self.title)
        for i, item in enumerate(self.items):
            print(f"{i + 1}. {item.text}")

        choice = int(input("Choose an option: ")) - 1

        if 0 <= choice < len(self.items):
            self.items[choice].execute()
        else:
            print("Invalid option")

        if self.parent_menu is not None:
            self.parent_menu.display()
