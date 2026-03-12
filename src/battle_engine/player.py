from __future__ import annotations

from .singleton import Singleton


class Player(metaclass=Singleton):
    def __init__(
        self,
        name: str = "Chara",
        health: int = 20,
        max_health: int = 20,
        attack: int = 5,
        defense: int = 5,
        level: int = 1,
        items: list[Item] | None = None,
    ) -> None:
        self.name = name
        self.health = health
        self.max_health = max_health
        self.invulnerability_time: int = 0
        self.attack = attack
        self.defense = defense
        self.level = level
        self.items: list[Item] = items if items is not None else []


class Item:
    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    def use(self, player: Player) -> None:
        raise NotImplementedError("Subclasses must implement this method.")


class HealingItem(Item):
    def __init__(self, name: str, description: str, healing_value: int) -> None:
        super().__init__(name, description)
        self.healing_value = healing_value

    def use(self, player: Player) -> None:
        player.health = min(player.max_health, player.health + self.healing_value)


class Weapon(Item):
    def __init__(self, name: str, description: str, damage: int) -> None:
        super().__init__(name, description)
        self.damage = damage

    def use(self, player: Player) -> None:
        player.attack = self.damage


class Armor(Item):
    def __init__(self, name: str, description: str, armor_value: int) -> None:
        super().__init__(name, description)
        self.armor_value = armor_value

    def use(self, player: Player) -> None:
        player.defense = self.armor_value
