# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A pygame-based engine for creating Undertale-inspired battle sequences. Python 3.12+, managed with uv. Installable as the `battle_engine` package (src layout with hatchling).

## Commands

```bash
uv sync              # Install dependencies (editable install)
uv run python launch.py  # Run the example Papyrus battle
```

No test suite or linter is configured.

## Project Structure

```
src/battle_engine/       # Installable package
  __init__.py            # Public API re-exports
  _assets.py             # Asset loading via importlib.resources
  constants.py           # Input constants, screen dimensions
  game.py                # Game loop, GameMode base class
  player.py              # Player stats and items
  singleton.py           # Singleton metaclass
  interpolation.py       # Interpolation + InterpolationManager
  text.py                # ProgressiveText + StyledText
  fonts.py               # Font registry, draw_text, draw_text_size
  drawing.py             # draw_gradient
  util.py                # Re-exports from above modules (backward compat)
  overworld.py           # Overworld stub
  battle/                # Battle system subpackage
    __init__.py           # Re-exports all battle classes
    core.py               # Battle, Round
    states.py             # BattleState, ButtonSelectState, MenuSelectState, TargetState, DefendingState
    enemy.py              # Enemy
    objects.py            # PlayerObject, BattleObject
    ui.py                 # GUIElement, HitVisual, TargetUI, PlayerStats, Button, BattleBox, MenuItem, MenuContainer, Menu
  assets/                # Bundled engine assets
    battle/              # UI sprites (buttons, soul, target UI, hit frames)
    fonts/               # DTM-Sans, undertale-attack-font, undertale-in-game-hud-font
examples/
  papyrus/               # Example Papyrus battle
    main.py
    assets/papyrus.png
  testmode.py            # Test mode example
launch.py                # Entry point for Papyrus example
```

## Architecture

The engine uses a **GameMode** pattern where `Game` (singleton) runs the main loop and delegates rendering/update/input to the active `GameMode`.

### Core flow

`Game` → holds one `GameMode` → either `Battle` or `Overworld` (stub)

**Battle system** uses a state stack (`gameStateStack`) to manage phases:
- `ButtonSelectState` → player picks FIGHT/ACT/ITEM/MERCY
- `MenuSelectState` → navigate enemy/act selection menus
- `TargetState` → timing-based attack minigame
- `DefendingState` → dodge enemy projectiles (runs a `Round`)

### Key classes

- **`Game`** (`game.py`) — Singleton. Main loop (30 FPS), window management, screen shake, fullscreen toggle (F4), manages `InterpolationManager` for tweened animations.
- **`Battle`** (`battle/core.py`) — Extends `GameMode`. Contains enemies, buttons, battle box, player object, and the state stack. Subclass this to create custom battles.
- **`Round`** (`battle/core.py`) — Subclass to define enemy attack patterns. Spawns `BattleObject`s that move and collide with the player soul. Has a `time` counter (delta-based) and `end_turn()`.
- **`Enemy`** (`battle/enemy.py`) — Holds sprite, health, acts, hit animation/shake logic. Health bar uses `Interpolation` for smooth drain.
- **`PlayerObject`** (`battle/objects.py`) — Singleton sprite (the soul). Moves with arrow keys inside the `BattleBox` bounds. Collision detection via pygame masks.
- **`Player`** (`player.py`) — Singleton. Stats: name, health, attack, defense, level, items, invulnerability timer.
- **`InterpolationManager` / `Interpolation`** (`interpolation.py`) — Tweening system. Supports LINEAR, EASE_IN, EASE_OUT, EASE_IN_OUT. Animates any object attribute over time.
- **`ProgressiveText`** (`text.py`) — Typewriter-style text with inline commands: `[color:RRGGBB]`, `[font:name]`, `[charspacing:N]`, `[instant]`, `[asterisk]`.

### Asset loading

Engine assets are bundled inside the package at `src/battle_engine/assets/` and loaded via `importlib.resources` through helpers in `_assets.py`:
- `asset_surface(relative)` — load a pygame Surface (e.g. `asset_surface("battle/soul/soul.png")`)
- `asset_font_path(relative)` — get filesystem path for a font
- `asset_frames(prefix)` — load numbered frame sequences (e.g. `asset_frames("battle/hit/knife")`)

### Singleton pattern

`Game`, `Player`, `PlayerObject`, and `InterpolationManager` are all singletons (via `Singleton` metaclass in `singleton.py`). They're accessed by calling the constructor anywhere: `Game()`, `Player()`, etc.

### Creating a new battle

1. Subclass `Battle` — override `select_next_round()` to return a `Round` subclass, and `post_init()` to set up enemies and encounter text.
2. Subclass `Enemy` — set sprite, position, name, health, and acts.
3. Subclass `Round` — override `round_update()` to spawn `BattleObject` projectiles with movement/collision logic.
4. See `examples/papyrus/main.py` for a complete reference.

All imports come from the top-level package: `from battle_engine import Battle, Enemy, Round`

### Input constants (`constants.py`)

- Confirm: Z or Y
- Dismiss: X
- Menu: C
- Movement: Arrow keys
- Fullscreen: F4
