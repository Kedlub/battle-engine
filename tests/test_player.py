from battle_engine.player import Armor, HealingItem, Player, Weapon
from battle_engine.singleton import Singleton


def setup_function():
    Singleton._instances.pop(Player, None)


def test_player_defaults():
    p = Player()
    assert p.name == "Chara"
    assert p.health == 20
    assert p.items == []


def test_player_mutable_default_items():
    """Ensure each Player instance gets its own items list."""
    p1 = Player()
    items_ref = p1.items
    Singleton._instances.pop(Player, None)
    p2 = Player()
    assert p2.items is not items_ref


def test_healing_item():
    p = Player(health=10, max_health=20)
    item = HealingItem("Pie", "Heals 15", 15)
    item.use(p)
    assert p.health == 20  # clamped to max


def test_weapon():
    p = Player()
    weapon = Weapon("Knife", "Sharp", 15)
    weapon.use(p)
    assert p.attack == 15


def test_armor():
    p = Player()
    armor = Armor("Tutu", "Comfy", 10)
    armor.use(p)
    assert p.defense == 10
