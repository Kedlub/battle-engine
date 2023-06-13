class Player:
    def __init__(self, name, health, max_health, invulnerability_time, attack, defense, level, items):
        self.name = name
        self.health = health
        self.max_health = max_health
        self.invulnerability_time = invulnerability_time
        self.attack = attack
        self.defense = defense
        self.level = level
        self.items = items
