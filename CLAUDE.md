# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A pygame-based engine for creating Undertale-inspired battle sequences. Python 3.12+, managed with uv.

## Commands

```bash
uv sync              # Install dependencies
uv run python launch.py  # Run the example Papyrus battle
```

No test suite or linter is configured.

## Architecture

The engine uses a **GameMode** pattern where `Game` (singleton) runs the main loop and delegates rendering/update/input to the active `GameMode`.

### Core flow

`Game` → holds one `GameMode` → either `Battle` or `Overworld` (stub)

**Battle system** uses a state stack (`gameStateStack`) to manage phases:
- `ButtonSelectState` → player picks FIGHT/ACT/ITEM/MERCY
- `MenuSelectState` → navigate enemy/act selection menus
- `TargetState` → timing-based attack minigame
- `DefendingState` → dodge enemy projectiles (runs a `Round`)

### Key classes (all in `modules/`)

- **`Game`** (`game.py`) — Singleton. Main loop (30 FPS), window management, screen shake, fullscreen toggle (F4), manages `InterpolationManager` for tweened animations.
- **`Battle`** (`battle.py`) — Extends `GameMode`. Contains enemies, buttons, battle box, player object, and the state stack. Subclass this to create custom battles.
- **`Round`** (`battle.py`) — Subclass to define enemy attack patterns. Spawns `BattleObject`s that move and collide with the player soul. Has a `time` counter (delta-based) and `end_turn()`.
- **`Enemy`** (`battle.py`) — Holds sprite, health, acts, hit animation/shake logic. Health bar uses `Interpolation` for smooth drain.
- **`PlayerObject`** (`battle.py`) — Singleton sprite (the soul). Moves with arrow keys inside the `BattleBox` bounds. Collision detection via pygame masks.
- **`Player`** (`player.py`) — Singleton. Stats: name, health, attack, defense, level, items, invulnerability timer.
- **`InterpolationManager` / `Interpolation`** (`util.py`) — Tweening system. Supports LINEAR, EASE_IN, EASE_OUT, EASE_IN_OUT. Animates any object attribute over time.
- **`ProgressiveText`** (`util.py`) — Typewriter-style text with inline commands: `[color:RRGGBB]`, `[font:name]`, `[charspacing:N]`, `[instant]`, `[asterisk]`.

### Singleton pattern

`Game`, `Player`, `PlayerObject`, and `InterpolationManager` are all singletons (via `Singleton` metaclass in `util.py`). They're accessed by calling the constructor anywhere: `Game()`, `Player()`, etc.

### Creating a new battle

1. Subclass `Battle` — override `select_next_round()` to return a `Round` subclass, and `post_init()` to set up enemies and encounter text.
2. Subclass `Enemy` — set sprite, position, name, health, and acts.
3. Subclass `Round` — override `round_update()` to spawn `BattleObject` projectiles with movement/collision logic.
4. See `examples/papyrus.py` for a complete reference.

### Assets

- `assets/battle/` — UI sprites (buttons, soul, target UI, hit frames)
- `assets/fonts/` — DTM-Sans (default), undertale-attack-font, undertale-in-game-hud-font
- Custom fonts registered via `register_font()` in `util.py`

### Input constants (`constants.py`)

- Confirm: Z or Y
- Dismiss: X
- Menu: C
- Movement: Arrow keys
- Fullscreen: F4
