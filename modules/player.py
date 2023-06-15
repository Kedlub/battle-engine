class Player:
    def __init__(self, name="Chara", health=20, max_health=20, attack=5, defense=5, level=1, items=[]):
        self.name = name
        self.health = health
        self.max_health = max_health
        self.invulnerability_time = 0
        self.attack = attack
        self.defense = defense
        self.level = level
        self.items = items

class Item:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def use(self, player):
        raise NotImplementedError("Subclasses must implement this method.")

class HealingItem(Item):
    def __init__(self, name, description, healing_value):
        super().__init__(name, description)
        self.healing_value = healing_value

    def use(self, player):
        player.health = min(player.max_health, player.health + self.healing_value)

class Weapon(Item):
    def __init__(self, name, description, damage):
        super().__init__(name, description)
        self.damage = damage

    def use(self, player):
        player.attack = self.damage

class Armor(Item):
    def __init__(self, name, description, armor_value):
        super().__init__(name, description)
        self.armor_value = armor_value

    def use(self, player):
        player.defense = self.armor_value