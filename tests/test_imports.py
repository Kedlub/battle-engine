"""Smoke tests: verify all public API symbols are importable."""

import importlib


def _check_attrs(module_name, names):
    mod = importlib.import_module(module_name)
    for name in names:
        assert hasattr(mod, name), f"{module_name}.{name} missing"


def test_top_level_exports():
    _check_attrs(
        "battle_engine",
        [
            "Armor",
            "Battle",
            "BattleBox",
            "BattleObject",
            "BattleState",
            "Button",
            "CONFIRM_BUTTON",
            "DISMISS_BUTTON",
            "Enemy",
            "GUIElement",
            "Game",
            "GameMode",
            "HEIGHT",
            "HealingItem",
            "HitVisual",
            "Interpolation",
            "InterpolationManager",
            "Item",
            "MENU_BUTTON",
            "Menu",
            "MenuContainer",
            "MenuItem",
            "Player",
            "PlayerObject",
            "PlayerStats",
            "ProgressiveText",
            "Round",
            "Singleton",
            "TargetUI",
            "WIDTH",
            "Weapon",
            "asset_font_path",
            "asset_frames",
            "asset_surface",
            "draw_gradient",
            "draw_text",
            "draw_text_size",
            "register_font",
        ],
    )


def test_submodule_exports():
    _check_attrs("battle_engine.singleton", ["Singleton"])
    _check_attrs(
        "battle_engine.interpolation",
        ["Interpolation", "InterpolationManager"],
    )
    _check_attrs("battle_engine.text", ["ProgressiveText", "StyledText"])
    _check_attrs(
        "battle_engine.fonts",
        ["draw_text", "draw_text_size", "register_font"],
    )
    _check_attrs("battle_engine.drawing", ["draw_gradient"])
    _check_attrs("battle_engine.battle.core", ["Battle", "Round"])
    _check_attrs(
        "battle_engine.battle.states",
        [
            "BattleState",
            "ButtonSelectState",
            "DefendingState",
            "MenuSelectState",
            "TargetState",
        ],
    )
    _check_attrs("battle_engine.battle.enemy", ["Enemy"])
    _check_attrs(
        "battle_engine.battle.objects",
        ["PlayerObject", "BattleObject"],
    )
    _check_attrs(
        "battle_engine.battle.ui",
        ["BattleBox", "Button", "Menu", "MenuItem"],
    )


def test_util_backward_compat():
    """util.py should re-export everything for backward compatibility."""
    _check_attrs(
        "battle_engine.util",
        [
            "Singleton",
            "Interpolation",
            "InterpolationManager",
            "ProgressiveText",
            "StyledText",
            "draw_text",
            "draw_text_size",
            "draw_gradient",
            "register_font",
        ],
    )
