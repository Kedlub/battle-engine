---
name: fetch-sprites
description: Download sprite sheets from Spriters Resource and other sprite sources
---

# Fetch Sprites

Download sprite sheets for the battle engine from online sprite resources.

## Primary Source: Spriters Resource

### How it works

Spriters Resource hosts community-submitted sprite sheets organized by platform and game.

**URL structure:**
- Browse page: `https://www.spriters-resource.com/{platform}/{game}/`
- Sheet detail: `https://www.spriters-resource.com/{platform}/{game}/sheet/{sheet_id}/`
- **Direct download:** `https://www.spriters-resource.com/media/assets/{folder_id}/{sheet_id}.png`

The `folder_id` is a two-digit number found on the sheet detail page (in the image src). It is NOT the same as the sheet_id.

### Step-by-step workflow

1. **Search for the game's sprite page:**
   Use Exa web search to find the game on spriters-resource.com:
   ```
   exa: "spriters-resource.com {game_name} sprites"
   ```

2. **Browse available sheets:**
   Use WebFetch on the game's page to list all available sprite sheets and their IDs:
   ```
   WebFetch: https://www.spriters-resource.com/{platform}/{game}/
   Prompt: "List all sprite sheet entries with their names and sheet IDs (the number in /sheet/XXXXX/)"
   ```

3. **Inspect a specific sheet:**
   Use WebFetch on the sheet detail page to get the exact download path:
   ```
   WebFetch: https://www.spriters-resource.com/{platform}/{game}/sheet/{sheet_id}/
   Prompt: "Extract the sprite sheet image URL from this page. Look for the image src in /media/assets/ path. Also describe what sprites are included."
   ```

4. **Download the sprite sheet:**
   ```bash
   curl -sL -o output.png "https://www.spriters-resource.com/media/assets/{folder_id}/{sheet_id}.png"
   ```

5. **Verify the download:**
   ```bash
   file output.png  # Should say "PNG image data"
   ```
   Then use the Read tool to visually inspect the downloaded image.

6. **Extract individual sprites** (if needed):
   Use the `extract-sprites` agent (`.claude/agents/extract-sprites.md`) to handle
   cropping. It understands Spriters Resource's two-layer background system
   (document bg vs sprite bounding boxes) and uses ImageMagick for extraction.

   ```
   Agent(subagent_type="extract-sprites", prompt="Extract [sprites] from [sheet path] to [output dir]")
   ```

### Known Undertale sheets

| Sheet Name | Sheet ID | Folder ID | Contents |
|---|---|---|---|
| The Human Souls | 77110 | 74 | Heart sprites: main, small, flee, break, debris/shards for all soul colors |
| Game Over | 122103 | 119 | GAME OVER text (422x182, white outlined letters) |
| Battle Menu | 76661 | 74 | Battle UI buttons and elements |
| Attack Effects | 77983 | 75 | Hit/attack visual effects |
| Miscellaneous Sprites | 81451 | 78 | Various game sprites |

### Finding the folder_id

The folder_id is NOT predictable from the sheet_id. To find it:
1. WebFetch the sheet detail page at `/sheet/{sheet_id}/`
2. Look for the image URL in the page which contains `/media/assets/{folder_id}/{sheet_id}.png`
3. Extract the folder_id from that path

### Important notes

- The `/download/{sheet_id}/` endpoint does NOT work (returns 404) — always use `/media/assets/` path
- Files are always PNG format
- Sprite sheets often have colored backgrounds (e.g., purple/magenta) as transparency indicators
- Always visually verify downloads with the Read tool before using
- Some sprites are procedurally generated in-game and won't be in sprite sheets

## Alternative Sources

If Spriters Resource doesn't have what you need:

- **The Cutting Room Floor** (tcrf.net) — unused/debug sprites, extracted game data
- **DeviantArt** — fan-made sprite sheets (search: "{game} sprite sheet")
- **Direct game extraction** — for games you own, tools like UndertalePatcher can export sprites

## Destination

Downloaded sprites for the battle engine should go into:
```
src/battle_engine/assets/battle/
```

Organize by category (e.g., `soul/`, `gameover/`, `effects/`).
