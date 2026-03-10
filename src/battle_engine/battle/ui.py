from __future__ import annotations

import random
from collections.abc import Callable

import pygame

from .._assets import asset_surface
from ..fonts import draw_text, draw_text_size
from ..game import Game
from ..interpolation import Interpolation, InterpolationManager
from ..player import Player
from ..text import ProgressiveText


class GUIElement:
    def __init__(
        self,
        position: tuple[float, float] = (0, 0),
        rotation: float = 0,
    ) -> None:
        self.x, self.y = position
        self.rotation = rotation

    def set_position(self, x: float, y: float) -> None:
        self.x, self.y = (x, y)

    def set_rotation(self, rotation: float) -> None:
        self.rotation = rotation

    def interpolate(
        self,
        target_position: tuple[float, float],
        target_rotation: float,
        t: float,
    ) -> None:
        x1, y1 = self.x, self.y
        x2, y2 = target_position
        self.set_position(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t)
        self.set_rotation(self.rotation + (target_rotation - self.rotation) * t)

    def update(self) -> None:
        raise NotImplementedError(
            "update method should be implemented in derived classes"
        )

    def render(self, surface: pygame.Surface) -> None:
        raise NotImplementedError(
            "render method should be implemented in derived classes"
        )


class HitVisual(GUIElement):
    def __init__(self, speed: int, frames: list[pygame.Surface]) -> None:
        super().__init__()
        self.speed = speed
        self.frame = 0
        self.active = False
        self.frames = frames

    def activate(self, rect: pygame.Rect) -> None:
        self.active = True
        self.frame = 0
        self.x = rect.centerx - self.frames[0].get_width() / 2
        self.y = rect.centery - self.frames[0].get_height() / 2

    def update(self) -> None:
        if not self.active:
            return
        self.frame += 1
        if self.frame >= len(self.frames) * self.speed:
            self.active = False

    def render(self, surface: pygame.Surface) -> None:
        if not self.active:
            return
        frame_index = self.frame // self.speed
        surface.blit(self.frames[frame_index], (self.x, self.y))


class TargetUI(GUIElement):
    def __init__(self, battle_box: BattleBox, enemy_max_health: int) -> None:
        super().__init__()
        bg_sprite = asset_surface("battle/target_ui/target.png")
        aim_sprite1 = asset_surface("battle/target_ui/target_aim1.png")
        aim_sprite2 = asset_surface("battle/target_ui/target_aim2.png")
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
        self.speed = 10
        self.alpha = 255
        self.enemy_max_health = enemy_max_health
        self.hit_power: float = 0
        self.hide_interpolation: Interpolation | None = None
        self.scale_interpolation: Interpolation | None = None
        self.move_interpolation: Interpolation | None = None

    def get_hit_power(self) -> float:
        return (
            1 - abs(self.cursor_pos - self.rect.centerx) / float(self.rect.width // 2)
        ) * (self.enemy_max_health / 8)

    def update(self) -> None:
        if self.active:
            self.cursor_pos += self.direction * self.speed
            if self.cursor_pos in (self.rect.left, self.rect.right):
                self.direction *= -1

    def render(self, surface: pygame.Surface) -> None:
        if self.shown:
            self.background.fill(
                (255, 255, 255, self.alpha), special_flags=pygame.BLEND_RGBA_MULT
            )
            surface.blit(
                pygame.transform.scale(self.background, self.rect.size), self.rect
            )
            aim = self.aim_cursor[self.frame_counter // 5]
            aim.fill((255, 255, 255, self.alpha), special_flags=pygame.BLEND_RGBA_MULT)
            if self.show_cursor:
                surface.blit(aim, (self.cursor_pos, self.rect.y))
            self.frame_counter += 1
            if self.frame_counter // 5 >= len(self.aim_cursor):
                self.frame_counter = 0
            if self.alpha == 0:
                self.shown = False
                Game().battle.objects.remove(self)

    def show(self) -> None:
        self.hit_power = 0
        self.direction = random.choice([-1, 1])
        self.rect = self.battle_box.get_internal_rect()
        self.cursor_pos = self.rect.left if self.direction == 1 else self.rect.right
        self.alpha = 255
        self.shown = True
        self.show_cursor = True
        self.active = True
        self.hide_interpolation = Interpolation(
            self, "alpha", 255, 0, 3000, Interpolation.LINEAR
        )
        self.scale_interpolation = Interpolation(
            self.rect, "width", self.rect.width, self.rect.width // 5, 3000
        )
        self.move_interpolation = Interpolation(
            self.rect, "x", self.rect.x, self.rect.x + (self.rect.width // 5) * 2, 3000
        )

    def hide(self) -> None:
        Game().battle.objects.append(self)
        self.show_cursor = False
        InterpolationManager().add_interpolation(self.hide_interpolation)
        InterpolationManager().add_interpolation(self.scale_interpolation)
        InterpolationManager().add_interpolation(self.move_interpolation)


class PlayerStats(GUIElement):
    def __init__(self, player: Player, position: tuple[float, float]) -> None:
        super().__init__(position)
        self.player = player
        self.width = 570
        self.height = 21
        self.hp_sprite = asset_surface("battle/hp.png")
        self.karma_sprite = asset_surface("battle/karma.png")

    def render(self, surface: pygame.Surface) -> None:
        y_offset = 6
        draw_text(
            surface,
            self.player.name,
            15,
            (255, 255, 255),
            self.x,
            self.y - y_offset,
            font_name="hud",
        )
        draw_text(
            surface,
            f"LV {str(self.player.level)}",
            15,
            (255, 255, 255),
            self.x + 100,
            self.y - y_offset,
            font_name="hud",
        )

        hp_bar_full = (192, 0, 0)
        hp_bar_current = (255, 255, 0)

        base_hpbar_pos = self.x + 250

        surface.blit(
            self.hp_sprite,
            (base_hpbar_pos - self.hp_sprite.get_width() - 10, self.y + 5),
        )

        pygame.draw.rect(
            surface,
            hp_bar_full,
            (base_hpbar_pos, self.y, self.player.max_health, self.height),
        )
        pygame.draw.rect(
            surface,
            hp_bar_current,
            (base_hpbar_pos, self.y, self.player.health, self.height),
        )

        draw_text(
            surface,
            f"{str(self.player.health)} / {str(self.player.max_health)}",
            15,
            (255, 255, 255),
            base_hpbar_pos + self.player.max_health + 10,
            self.y - y_offset,
            font_name="hud",
        )

    def update(self) -> None:
        pass


class Button(GUIElement):
    default_width = 110

    def __init__(
        self,
        inactive_texture: str,
        active_texture: str,
        position: tuple[float, float] = (0, 0),
        rotation: float = 0,
    ) -> None:
        super().__init__(position, rotation)
        self.inactive_texture = asset_surface(inactive_texture)
        self.active_texture = asset_surface(active_texture)
        self.height = self.active_texture.get_height()
        self.current_texture = self.inactive_texture

    def set_active(self, active: bool) -> None:
        if active:
            self.current_texture = self.active_texture
        else:
            self.current_texture = self.inactive_texture

    def update(self) -> None:
        pass

    def move_player(self) -> None:
        if self.current_texture == self.active_texture:
            from .objects import PlayerObject

            player_object = PlayerObject()
            player_object.set_position(self.x + 10, self.y + self.height / 2 - 8)

    def render(self, surface: pygame.Surface) -> None:
        image = pygame.transform.rotate(self.current_texture, self.rotation)
        surface.blit(image, (self.x, self.y))


class BattleBox(GUIElement):
    def __init__(
        self,
        position: tuple[float, float] = (0, 0),
        width: int = 200,
        height: int = 100,
        rotation: float = 0,
    ) -> None:
        super().__init__(position, rotation)
        self.width = width
        self.height = height
        self.border_thickness = 5
        self.background_color = (0, 0, 0)
        self.border_color = (255, 255, 255)
        rect = self.get_internal_rect()
        self.text = ProgressiveText(
            x=rect.x + 14, y=rect.y + 5, max_width=rect.width - 28
        )
        self.menu: MenuContainer | None = None
        self.current_menu_page = 0

    def render_text(self, surface: pygame.Surface) -> None:
        self.text.draw(surface)

    def render(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(
            surface, self.background_color, (self.x, self.y, self.width, self.height)
        )
        pygame.draw.rect(
            surface,
            self.border_color,
            (self.x, self.y, self.width, self.height),
            self.border_thickness,
        )

    def update(self) -> None:
        rect = self.get_internal_rect()
        self.text.x = rect.x + 14
        self.text.y = rect.y + 5
        self.text.max_width = rect.width - 28
        self.text.update()

    def get_internal_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.x + self.border_thickness,
            self.y + self.border_thickness,
            self.width - 2 * self.border_thickness,
            self.height - 2 * self.border_thickness,
        )

    def set_encounter_text(self, text: str) -> None:
        self.text.set_text(text)

    def is_encounter_text_finished(self) -> bool:
        return self.text.finished

    def open_menu(self, menu: MenuContainer) -> None:
        self.menu = menu


class MenuItem:
    def __init__(
        self,
        text: str,
        action: Callable[[], None] | None = None,
        submenu: Menu | None = None,
    ) -> None:
        self.text = text
        self.action = action
        self.submenu = submenu

    def execute(self) -> None:
        if self.action is not None:
            self.action()
        elif self.submenu is not None:
            self.submenu.display()


class MenuContainer:
    def __init__(
        self,
        menu: Menu | None = None,
        x: int = 0,
        y: int = 0,
        width: int = 200,
        height: int = 200,
        columns: int = 2,
        spacing: int = 5,
        font_size: int = 27,
    ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font_size = font_size
        self.spacing = spacing
        self.columns = columns
        self.active_menu: Menu | None = None
        self.set_menu(menu)

    def set_menu(self, menu: Menu | None) -> None:
        self.active_menu = menu
        self.select_item(0)

    def items_per_page(self) -> int:
        assert self.active_menu is not None
        remaining_height = self.height - draw_text_size("Sample", self.font_size)[1]
        row_items = 0

        while remaining_height > 0:
            remaining_height -= (
                draw_text_size("Sample", self.font_size)[1] + self.spacing
            )
            if remaining_height > 0:
                row_items += 1

        return row_items * self.columns

    def get_items_for_page(self, page_number: int) -> list[MenuItem]:
        assert self.active_menu is not None
        start_index = (page_number - 1) * self.items_per_page()
        end_index = start_index + self.items_per_page()
        return self.active_menu.items[start_index:end_index]

    def get_page_number_by_index(self, index: int) -> int:
        items_per_page = self.items_per_page()
        return index // items_per_page + 1

    def get_total_page_count(self) -> int:
        assert self.active_menu is not None
        items_count = len(self.active_menu.items)
        items_per_page = self.items_per_page()
        total_pages = items_count // items_per_page
        if items_count % items_per_page > 0:
            total_pages += 1
        return total_pages

    def get_heart_position(self) -> tuple[float, float]:
        assert self.active_menu is not None
        x = self.x + 60 - 30
        y = self.y + 5 + 8
        items_on_current_page = self.get_items_for_page(
            self.get_page_number_by_index(self.active_menu.selected_index)
        )
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

    def get_column_range(self, column_number: int) -> list[int]:
        assert self.active_menu is not None
        items_per_page = self.items_per_page()
        items_per_row = items_per_page // self.columns
        start_index = column_number * items_per_row
        end_index = start_index + items_per_row
        total_items = len(self.active_menu.items)

        if start_index < total_items:
            return list(range(start_index, min(end_index, total_items)))
        else:
            return []

    def select_next_in_row(self, direction: int) -> None:
        assert self.active_menu is not None
        items_per_row = self.items_per_page() // self.columns
        new_index = self.active_menu.selected_index + (direction * items_per_row)
        self.select_item(new_index)

    def select_next_in_column(self, direction: int) -> None:
        assert self.active_menu is not None
        items_per_row = self.items_per_page() // self.columns
        column_number = self.active_menu.selected_index // items_per_row
        column_range = self.get_column_range(column_number)
        current_index_in_column = column_range.index(self.active_menu.selected_index)

        new_index_in_column = (current_index_in_column + direction) % len(column_range)
        new_index = column_range[new_index_in_column]

        self.select_item(new_index)

    def select_item(self, index: int) -> None:
        if self.active_menu is not None:
            total_items = len(self.active_menu.items)
            clamped_index = max(0, min(index, total_items - 1))
            self.active_menu.selected_index = clamped_index
            from .objects import PlayerObject

            player_object = PlayerObject()
            player_object.set_position(*self.get_heart_position())

    def run_selected_item(self) -> None:
        assert self.active_menu is not None
        self.active_menu.get_selected_item().execute()

    def render(self, surface: pygame.Surface) -> None:
        if self.active_menu is None:
            return
        x = self.x + 60
        y = self.y + 5
        items_on_current_page = self.get_items_for_page(
            self.get_page_number_by_index(self.active_menu.selected_index)
        )
        for item in items_on_current_page:
            if y - self.y > self.height - self.font_size * 2:
                x += 200
                y = self.y + 5
            name = f"* {item.text}"
            width, height = draw_text_size(name, self.font_size)
            draw_text(surface, name, self.font_size, (255, 255, 255), x, y)
            y += height + 5

        y = self.y + self.height - self.font_size - 10
        page_count = self.get_total_page_count()
        page_number = self.get_page_number_by_index(self.active_menu.selected_index)
        if page_count > 1:
            draw_text(
                surface, f"PAGE {page_number}", self.font_size, (255, 255, 255), x, y
            )

    def update(self) -> None:
        pass


class Menu:
    def __init__(
        self,
        title: str = "",
        items: list[MenuItem] | None = None,
        parent_menu: Menu | None = None,
    ) -> None:
        self.title = title
        self.items: list[MenuItem] = items if items is not None else []
        self.parent_menu = parent_menu
        self.selected_index: int = 0

    def add_item(self, item: MenuItem) -> None:
        self.items.append(item)

    def select_item(self, index: int) -> None:
        self.selected_index = index

    def get_selected_item(self) -> MenuItem:
        return self.items[self.selected_index]

    def display(self) -> None:
        pass
