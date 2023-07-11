import pygame
import enum
import random
import os
import math

from modules.constants import CONFIRM_BUTTON, DISMISS_BUTTON, WIDTH
from modules.game import GameMode, Game
from modules.player import Player
from modules.util import resource_path, draw_gradient, draw_text, ProgressiveText, Singleton, draw_text_size, \
    InterpolationManager, Interpolation


class BattleState:
    def handle_input(self, battle, event):
        pass

    def update(self, battle):
        pass

    def render(self, battle, surface):
        pass

    def show_soul(self):
        return True


class Battle(GameMode):
    def __init__(self, game=Game(), init_default=True):
        super().__init__(game)
        self.button_data = []
        self.buttons = []
        self.rounds = []
        self.enemies = []
        self.gameStateStack = [ButtonSelectState()]
        self.selected_button = 0
        self.player_stats = PlayerStats(Player(name="Chara", level=19, health=90, max_health=92),
                                        (40, game.surface.get_height() - 80))
        self.player_object = PlayerObject(50, 50, (255, 0, 0))
        self.battle_box = BattleBox(position=(33, game.surface.get_height() / 2 + 9), width=575, height=140)
        battle_rect = self.battle_box.get_internal_rect()
        self.add_default_buttons()
        self.hit_visual = HitVisual.load_frames("assets/battle/hit/knife")
        self.objects = []

    def post_init(self):
        pass

    def add_default_buttons(self):
        self.add_button("assets/battle/button/fight0.png", "assets/battle/button/fight1.png")
        self.add_button("assets/battle/button/act0.png", "assets/battle/button/act1.png")
        self.add_button("assets/battle/button/item0.png", "assets/battle/button/item1.png")
        self.add_button("assets/battle/button/mercy0.png", "assets/battle/button/mercy1.png")
        self.create_buttons()

    def calculate_spacing(self, num_of_buttons, screen_width):
        button_space_evenly = (screen_width - num_of_buttons * Button.default_width) / (num_of_buttons + 1)
        return button_space_evenly

    def attack_enemy(self, enemy):
        if enemy in self.enemies:
            state = TargetState(enemy)
            self.gameStateStack.append(state)

    def use_item(self, item):
        # TODO: implement item usage
        pass

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
        if self.gameStateStack:
            self.gameStateStack[-1].render(self, surface)
            for obj in self.objects:
                obj.render(surface)
            if self.gameStateStack[-1].show_soul():
                self.player_object.render(surface)
        pass

    def update(self, surface):
        if self.gameStateStack:
            self.gameStateStack[-1].update(self)
        for enemy in self.enemies:
            enemy.update(surface)
        for obj in self.objects:
            obj.update()
        # self.player_object.update()
        self.battle_box.update()
        pass

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
        # Implement input handling in Battle mode here
        if self.gameStateStack:
            self.gameStateStack[-1].process_input(self, event)
        pass


class ButtonSelectState(BattleState):
    def render(self, battle, surface):
        battle.battle_box.render_text(surface)

    def update(self, battle):
        for button in battle.buttons:
            button.move_player()

    def process_input(self, battle, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                battle.select_button(battle.selected_button - 1)
            elif event.key == pygame.K_RIGHT:
                battle.select_button(battle.selected_button + 1)
            elif event.key in CONFIRM_BUTTON:
                # confirm the selection
                menu = Menu()
                for enemy in battle.enemies:
                    item = MenuItem(enemy.name)
                    item.action = lambda: battle.attack_enemy(enemy)
                    menu.add_item(item)
                battle.gameStateStack.append(MenuSelectState(menu))


class MenuSelectState(BattleState):
    def __init__(self, menu):
        battle_rect = Game().game_mode.battle_box.get_internal_rect()
        self.menu = MenuContainer(x=battle_rect.x, y=battle_rect.y, width=battle_rect.width, height=battle_rect.height)
        self.menu.set_menu(menu)

    def render(self, battle, surface):
        self.menu.render(surface)

    def process_input(self, battle, event):
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
    def __init__(self, enemy):
        super().__init__()
        self.target = TargetUI(Game().game_mode.battle_box, enemy.max_health)
        self.enemy = enemy
        self.target.show()

    def render(self, battle, surface):
        self.target.render(surface)

    def process_input(self, battle, event):
        if event.type == pygame.KEYDOWN:
            if event.key in CONFIRM_BUTTON and self.target.active:
                self.target.active = False
                power = self.target.get_hit_power()
                self.enemy.hit(power)

    def update(self, battle):
        self.target.update()

    def show_soul(self):
        return False

class DefendingState(BattleState):
    def render(self, battle, surface):
        # TODO: Implement defending state rendering, maybe none is needed? We have the battle.objects list, which can contain the projectiles
        pass

    def process_input(self, battle, event):
        pass

    def update(self, battle):
        battle.player_object.update()

    def show_soul(self):
        return True
    

class BattleObject:
    def __init__(self, sprite, position=(0, 0), rotation=0):
        self.sprite = sprite
        self.position = position
        self.rotation = rotation
        self.mask = pygame.mask.from_surface(self.sprite)

    def update(self):
        # Update the mask after rotating the image
        self.mask = pygame.mask.from_surface(pygame.transform.rotate(self.sprite, self.rotation))

    def collides_with(self, other):
        # Calculate the offset between the two objects
        offset = (other.position[0] - self.position[0], other.position[1] - self.position[1])

        # Check if the masks overlap
        return self.mask.overlap(other.mask, offset) is not None

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
        self.health_bar_position = (rect.centerx - self.health_bar_width / 2, rect.y - self.health_bar_height - 5)

    def get_rect(self):
        width, height = self.sprite.get_size()
        return pygame.Rect(self.position[0], self.position[1], width, height)

    def add_act(self, name, func):
        self.acts.append({name: func})

    def update(self, surface):
        if self.being_attacked:
            if not self.hit_visual.active and not self.shake_ticks:
                # If the hit visual has finished, start the shake and deal damage if it hasn't started yet
                power_ratio = min(self.hit_power / float(self.max_health), 1.0)
                self.shake_dist = int(power_ratio * (self.sprite.get_width() / 2))
                self.shake_speed = max(1, int(20 * power_ratio))
                self.shake_ticks = 6 * self.shake_speed
                # Subtract the hit power from the enemy's health
                # Alternatively, this might be done based on the outcome of the shake animation
                self.health -= self.hit_power
                self.healthbar_ticks = 100
            elif self.hit_visual.active:
                # Update the hit_visual
                self.hit_visual.update()

        # The shake update stays the same
        if self.shake_ticks > 0:
            self.shake_ticks -= 1
            if self.shake_ticks % self.shake_speed == 0:
                sign = 1 if (self.shake_ticks / self.shake_speed) % 2 == 0 else -1
                shake_offset = sign * self.shake_dist
                self.position = (self.base_position[0] + shake_offset, self.base_position[1])
                self.shake_dist *= 0.9
            if self.shake_ticks == 0:
                self.shake_dist = 0
                self.position = self.base_position
                self.being_attacked = False
                Game().game_mode.gameStateStack[-1].target.hide()
                Game().game_mode.gameStateStack.append(DefendingState())

    def hit(self, damage):
        self.being_attacked = True
        self.hit_visual.activate(self.get_rect())
        self.hit_power = damage

    def render(self, surface):
        # Base implementation of render using only one sprite, enemies don't have to use this one sprite,
        # it can instead use different sprites for different body part
        surface.blit(pygame.transform.rotate(self.sprite, self.rotation), self.position)
        if self.hit_visual.active:
            self.hit_visual.render(surface)
        if self.healthbar_ticks > 0:
            self.healthbar_ticks -= 1
            self.draw_health_bar(surface)
        pass

    def draw_health_bar(self, surface):
        health_bar_x = self.health_bar_position[0]
        health_bar_y = self.health_bar_position[1]
        max_health_bar_color = (255, 0, 0)
        current_health_bar_color = (0, 255, 0)

        max_health_width = self.health_bar_width
        current_health_width = (self.health / self.max_health) * self.health_bar_width

        # Draw the red background representing the maximum health
        pygame.draw.rect(surface, max_health_bar_color,
                        (health_bar_x, health_bar_y, max_health_width, self.health_bar_height))

        # Draw the green foreground representing the current health
        pygame.draw.rect(surface, current_health_bar_color,
                        (health_bar_x, health_bar_y, current_health_width, self.health_bar_height))


    def process_input(self, event):
        pass

    def check(self):
        pass


class PlayerObject(pygame.sprite.Sprite, metaclass=Singleton):
    def __init__(self, x=0, y=0, color=(255, 0, 0)):
        super().__init__()
        self.sprite = pygame.image.load(resource_path("assets/battle/soul/soul.png"))
        self.rect = self.sprite.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.rotation = 0
        self.speed = 5
        self.game = Game()
        self.set_color(color)

    def set_color(self, color):
        new_surface = pygame.Surface(self.sprite.get_size())
        new_surface.fill(color)
        new_surface.set_colorkey((0, 0, 0))
        new_surface.set_alpha(self.sprite.get_alpha())
        new_surface.blit(self.sprite, (0, 0), None, pygame.BLEND_RGBA_MULT)
        self.sprite = new_surface.convert_alpha()

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

    # a function to detect collision with the battle_box boundaries, or with an object in self.objects that has a collision box
    # and adjust the player's position accordingly
    def check_collision(self):
        battle_rect = self.game.game_mode.battle_box.get_internal_rect()
        # check if the player is colliding with the battle_box boundary
        self.rect.left = max(self.rect.left, battle_rect.left)
        self.rect.right = min(self.rect.right, battle_rect.right)
        self.rect.top = max(self.rect.top, battle_rect.top)
        self.rect.bottom = min(self.rect.bottom, battle_rect.bottom)

    def update(self):
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
        self.check_collision()

    def render(self, surface):
        rotated = pygame.transform.rotate(self.sprite, self.rotation)
        rotated_rect = rotated.get_rect(center=self.rect.center)
        surface.blit(rotated, rotated_rect)

    def process_input(self, event):
        pass


class GUIElement:
    def __init__(self, position=(0, 0), rotation=0):
        self.x, self.y = position
        self.rotation = rotation

    def set_position(self, x, y):
        self.x, self.y = (x, y)

    def set_rotation(self, rotation):
        self.rotation = rotation

    def interpolate(self, target_position, target_rotation, t):
        x1, y1 = self.x, self.y
        x2, y2 = target_position
        self.set_position(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t)
        self.set_rotation(self.rotation + (target_rotation - self.rotation) * t)

    def update(self):
        raise NotImplementedError("update method should be implemented in derived classes")

    def render(self, screen):
        raise NotImplementedError("render method should be implemented in derived classes")


class HitVisual(GUIElement):
    def __init__(self, speed, frames):
        super().__init__()
        self.speed = speed
        self.frame = 0
        self.active = False
        self.frames = frames

    def activate(self, rect):
        self.active = True
        self.frame = 0
        self.x = rect.centerx - self.frames[0].get_width() / 2
        self.y = rect.centery - self.frames[0].get_height() / 2

    @staticmethod
    def load_frames(path):
        frames = []
        i = 1
        while True:
            try:
                frames.append(pygame.image.load(resource_path(f"{path}{i}.png")))
                i += 1
            except FileNotFoundError:
                break
        return frames

    def update(self):
        if not self.active:
            return
        self.frame += 1
        if self.frame >= len(self.frames) * self.speed:
            self.active = False

    def render(self, surface):
        if not self.active:
            return
        frame_index = self.frame // self.speed
        surface.blit(self.frames[frame_index], (self.x, self.y))


class TargetUI(GUIElement):
    def __init__(self, battle_box, enemy_max_health):
        super().__init__()
        bg_sprite = pygame.image.load(resource_path("assets/battle/target/target.png"))
        aim_sprite1 = pygame.image.load(resource_path("assets/battle/target/target_aim1.png"))
        aim_sprite2 = pygame.image.load(resource_path("assets/battle/target/target_aim2.png"))
        self.background = bg_sprite
        self.aim_cursor = [aim_sprite1, aim_sprite2]
        self.direction = random.choice([-1, 1])
        self.battle_box = battle_box
        self.rect = battle_box.get_internal_rect()
        self.cursor_pos = self.rect.left if self.direction == 1 else self.rect.right
        self.shown = False
        self.show_cursor = True
        self.active = False
        self.frame_counter = 0
        self.speed = 5
        self.alpha = 255
        self.enemy_max_health = enemy_max_health
        self.hide_interpolation = Interpolation(self, "alpha", 255, 0, 3000, Interpolation.LINEAR)
        self.scale_interpolation = Interpolation(self.rect, "width", self.rect.width, self.rect.width // 5, 3000)
        self.move_interpolation = Interpolation(self.rect, "x", self.rect.x, self.rect.x + (self.rect.width // 5) * 2,
                                                3000)

    def process_event(self, event):
        pass

    def get_hit_power(self):
        return (1 - abs(self.cursor_pos - self.rect.centerx) / float(self.rect.width // 2)) * (self.enemy_max_health / 8)

    def update(self):
        if self.active:
            self.cursor_pos += self.direction * self.speed
            if self.cursor_pos in (self.rect.left, self.rect.right):
                self.direction *= -1

    def render(self, surface):
        if self.shown:
            self.background.fill((255, 255, 255, self.alpha), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(pygame.transform.scale(self.background, self.rect.size), self.rect)
            aim = self.aim_cursor[self.frame_counter // 5]
            aim.fill((255, 255, 255, self.alpha), special_flags=pygame.BLEND_RGBA_MULT)
            if self.show_cursor:
                surface.blit(aim, (self.cursor_pos, self.rect.y))
            self.frame_counter += 1
            if self.frame_counter // 5 >= len(self.aim_cursor):
                self.frame_counter = 0
            if self.alpha == 0:
                self.shown = False
                Game().game_mode.objects.remove(self)

    def show(self):
        self.hit_power = 0
        self.direction = random.choice([-1, 1])
        self.rect = self.battle_box.get_internal_rect()
        self.cursor_pos = self.rect.left if self.direction == 1 else self.rect.right
        self.alpha = 255
        self.shown = True
        self.show_cursor = True
        self.active = True
        self.hide_interpolation = Interpolation(self, "alpha", 255, 0, 3000, Interpolation.LINEAR)
        self.scale_interpolation = Interpolation(self.rect, "width", self.rect.width, self.rect.width // 5, 3000)
        self.move_interpolation = Interpolation(self.rect, "x", self.rect.x, self.rect.x + (self.rect.width // 5) * 2,
                                                3000)
        pass

    def hide(self):
        Game().game_mode.objects.append(self)
        self.show_cursor = False
        InterpolationManager().add_interpolation(self.hide_interpolation)
        InterpolationManager().add_interpolation(self.scale_interpolation)
        InterpolationManager().add_interpolation(self.move_interpolation)


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
        # pygame.draw.rect(surface, (0, 120, 120), (self.x, self.y, self.width, self.height))
        draw_text(surface, self.player.name, 15, (255, 255, 255), self.x, self.y - y_offset,
                  font_name="hud")
        draw_text(surface, f"LV {str(self.player.level)}", 15, (255, 255, 255), self.x + 100,
                  self.y - y_offset, font_name="hud")

        hp_bar_full = (192, 0, 0)
        hp_bar_current = (255, 255, 0)

        base_hpbar_pos = self.x + 250

        surface.blit(self.hp_sprite, (base_hpbar_pos - self.hp_sprite.get_width() - 10, self.y + 5))

        pygame.draw.rect(surface, hp_bar_full,
                         (base_hpbar_pos, self.y, self.player.max_health, self.height))
        pygame.draw.rect(surface, hp_bar_current,
                         (base_hpbar_pos, self.y, self.player.health, self.height))

        draw_text(surface, f"{str(self.player.health)} / {str(self.player.max_health)}", 15, (255, 255, 255),
                  base_hpbar_pos + self.player.max_health + 10, self.y - y_offset, font_name="hud")

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
            self.current_texture = self.active_texture
        else:
            self.current_texture = self.inactive_texture

    def update(self):
        pass

    def move_player(self):
        if self.current_texture == self.active_texture:
            player_object = PlayerObject()
            player_object.set_position(self.x + 10, self.y + self.height / 2 - 8)

    def render(self, screen):
        image = pygame.transform.rotate(self.current_texture, self.rotation)
        screen.blit(image, (self.x, self.y))


class BattleBox(GUIElement):
    def __init__(self, position=(0, 0), width=200, height=100, rotation=0):
        super().__init__(position, rotation)
        self.width = width
        self.height = height
        self.border_thickness = 5
        self.background_color = (0, 0, 0)
        self.border_color = (255, 255, 255)
        rect = self.get_internal_rect()
        self.text = ProgressiveText(x=rect.x + 5, y=rect.y + 5, max_width=rect.width - 10)
        self.menu = None
        self.current_menu_page = 0

    def render_text(self, surface):
        self.text.draw(surface)

    def render(self, surface):
        pygame.draw.rect(surface, self.background_color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, self.border_color, (self.x, self.y, self.width, self.height),
                         self.border_thickness)

    def update(self):
        rect = self.get_internal_rect()
        self.text.x = rect.x + 5
        self.text.y = rect.y + 5
        self.text.max_width = rect.width - 10
        self.text.update()
        pass

    def get_internal_rect(self):
        return pygame.Rect(self.x + self.border_thickness, self.y + self.border_thickness,
                           self.width - 2 * self.border_thickness, self.height - 2 * self.border_thickness)

    def set_encounter_text(self, text):
        self.text.set_text(text)

    def is_encounter_text_finished(self):
        return self.text.finished

    def open_menu(self, menu):
        self.menu = menu


class MenuItem:
    def __init__(self, text, action=None, submenu=None):
        self.text = text
        self.action = action
        self.submenu = submenu

    def execute(self):
        if self.action is not None:
            self.action()
        elif self.submenu is not None:
            self.submenu.display()


class MenuContainer:
    def __init__(self, menu=None, x=0, y=0, width=200, height=200, columns=2, spacing=5, font_size=27):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font_size = font_size
        self.spacing = spacing
        self.columns = columns
        self.active_menu = None
        self.set_menu(menu)

    def set_menu(self, menu):
        self.active_menu = menu
        self.select_item(0)

    def items_per_page(self):
        remaining_height = self.height - draw_text_size("Sample", self.font_size)[1]
        row_items = 0

        while remaining_height > 0:
            remaining_height -= draw_text_size("Sample", self.font_size)[1] + self.spacing
            if remaining_height > 0:
                row_items += 1

        return row_items * self.columns

    def get_items_for_page(self, page_number):
        start_index = (page_number - 1) * self.items_per_page()
        end_index = start_index + self.items_per_page()
        return self.active_menu.items[start_index:end_index]

    def get_page_number_by_index(self, index):
        items_per_page = self.items_per_page()
        return index // items_per_page + 1

    def get_total_page_count(self):
        items_count = len(self.active_menu.items)
        items_per_page = self.items_per_page()
        total_pages = items_count // items_per_page
        if items_count % items_per_page > 0:
            total_pages += 1
        return total_pages

    def get_heart_position(self):
        x = self.x + 60 - 30
        y = self.y + 5 + 8
        items_on_current_page = self.get_items_for_page(
            self.get_page_number_by_index(self.active_menu.selected_index))
        selected_item = self.active_menu.get_selected_item()

        for item in items_on_current_page:
            if item == selected_item:
                return x, y
            _, height = draw_text_size(item.text, self.font_size)
            y += height + 5
            if y - self.y > self.height - self.font_size * 2:
                x += 200
                y = self.y + 5 + 8

        return x, y

    def get_column_range(self, column_number):
        items_per_page = self.items_per_page()
        items_per_row = items_per_page // self.columns
        start_index = column_number * items_per_row
        end_index = start_index + items_per_row
        total_items = len(self.active_menu.items)

        if start_index < total_items:
            return list(range(start_index, min(end_index, total_items)))
        else:
            return []

    def select_next_in_row(self, direction):
        items_per_row = self.items_per_page() // self.columns
        new_index = self.active_menu.selected_index + (direction * items_per_row)
        self.select_item(new_index)

    def select_next_in_column(self, direction):
        items_per_row = self.items_per_page() // self.columns
        column_number = self.active_menu.selected_index // items_per_row
        column_range = self.get_column_range(column_number)
        current_index_in_column = column_range.index(self.active_menu.selected_index)

        new_index_in_column = (current_index_in_column + direction) % len(column_range)
        new_index = column_range[new_index_in_column]

        self.select_item(new_index)

    def select_item(self, index):
        if self.active_menu is not None:
            total_items = len(self.active_menu.items)
            clamped_index = max(0, min(index, total_items - 1))
            self.active_menu.selected_index = clamped_index
            player_object = PlayerObject()
            player_object.set_position(*self.get_heart_position())

    def run_selected_item(self):
        self.active_menu.get_selected_item().execute()

    def render(self, surface):
        if self.active_menu is None:
            return
        x = self.x + 60
        y = self.y + 5
        items_on_current_page = self.get_items_for_page(
            self.get_page_number_by_index(self.active_menu.selected_index))
        for item in items_on_current_page:
            if y - self.y > self.height - self.font_size * 2:
                x += 200
                y = self.y + 5
            name = f"* {item.text}"
            width, height = draw_text_size(name, self.font_size)
            draw_text(surface, name, self.font_size, (255, 255, 255),
                      x, y)
            y += height + 5

        y = self.y + self.height - self.font_size - 10
        page_count = self.get_total_page_count()
        page_number = self.get_page_number_by_index(self.active_menu.selected_index)
        if page_count > 1:
            draw_text(surface, f"PAGE {page_number}", self.font_size, (255, 255, 255),
                      x, y)

    def update(self):
        pass  # logic for updating the menu like input handling goes here


class Menu:
    def __init__(self, title="", items=None, parent_menu=None):
        self.title = title
        self.items = items if items is not None else []
        self.parent_menu = parent_menu
        self.selected_index = 0

    def add_item(self, item):
        self.items.append(item)

    def select_item(self, index):
        self.selected_index = index

    def get_selected_item(self):
        return self.items[self.selected_index]
