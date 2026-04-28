# AINCRAD SIMULATOR

## Project Description
- **Game Genre:** Idle Clicker, MMORPG-inspired

AINCRAD SIMULATOR is a cookie-clicker style idle game built with Python and Pygame, set in the floating castle Aincrad from Sword Art Online. You are a player trapped in the virtual world, who must fight through monster-filled floors by clicking to deal damage. Each kill rewards Magic Stones — the in-game currency — which can be spent in the shop to permanently upgrade combat stats.

The game features a floor progression system, timed boss raids with multiple enemy waves, animated sprites, quest rooms with ally characters, an active skill system, and a full save/load system. A built-in statistics tracker records gameplay data across sessions and can be analyzed through a standalone `analysis.py` program.

The core gameplay loop is: **click monster → earn Magic Stones → buy upgrades → challenge boss → unlock next floor → repeat.**

---

## Installation

To clone this project:
```sh
git clone https://github.com/SuroTheFool/AINCRAD_SIM
cd AINCRAD_SIM
```

To create and run a Python virtual environment:

**Windows:**
```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**Mac:**
```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Running Guide

After activating the Python environment, run the game with:

**Windows:**
```bat
python main.py
```

**Mac:**
```sh
python3 main.py
```

To open the statistics analysis program (independently from the game):

```bat
python analysis.py
```

---

## Tutorial / Usage

### Controls
| Key | Action |
|-----|--------|
| `Left Click` | Attack the current monster |
| `1` `2` `3` `4` `5` | Activate equipped skill in slot |
| `ESC` | Open pause menu / close shop |

### How to Play
1. Launch the game and press **PLAY** from the title screen
2. Click on the monster to deal damage and kill it
3. Each kill rewards Magic Stones scaled by monster HP and your gold multiplier
4. Open the **Shop** (bottom right) to spend Magic Stones on upgrades
5. Upgrade **STR**, **INT**, and **END** in the Stats tab to increase your power
6. Purchase and equip **Active Skills** in the Skills tab — bind them to slots 1–5
7. Press **B** to challenge the floor boss in a timed raid
8. Defeat the boss to unlock the next floor
9. Progress is automatically saved on quit

### Tips
- Intelligence scales damage multiplicatively via √INT — it is the most impactful stat late game
- Endurance regenerates over time — manage it carefully when using active skills
- Boss raids are timed — upgrade your stats before attempting them
- Check `analysis.py` after a few sessions to see your damage progression and skill usage patterns

---

## Game Features

- **Multi-floor progression** — Each floor has its own layered background and monster pool with weighted spawn probabilities
- **Boss Raids** — Timed multi-wave encounters that unlock the next floor on victory
- **Quest Rooms** — Story-driven combat encounters with ally characters and dialog bubbles
- **Shop System** — Three tabs: Upgrades, Skills, Stats — with floor-gated unlock system
- **Active Skill System** — 3 purchasable active skills equippable across 5 slots, triggered by keys 1–5
- **Animated Sprites** — Full sprite sheet animation for player, monsters, and allies
- **Save / Load System** — Full game state persistence via JSON
- **Statistics Tracker** — Gameplay events logged to `saves/stats.csv` across all sessions
- **Data Analysis Program** — Standalone `analysis.py` with 5 visualization tabs built in Tkinter
- **Audio System** — Background music per floor with SFX for hits, crits, kills, and purchases

---

## Project Structure

```
AINCRAD_SIM/
├── main.py                  ← Entry point
├── analysis.py              ← Standalone statistics viewer (Tkinter)
├── assets/
│   ├── fonts/
│   ├── images/              ← All sprites and UI images
│   └── sounds/              ← Music and SFX
├── saves/
│   ├── savegame.json        ← Game state save file
│   └── stats.csv            ← Statistics CSV (appended each session)
└── src/
    ├── game.py              ← Main game loop and controller
    ├── entities.py          ← Player, Monster, Mob, Ally classes
    ├── shop.py              ← Shop overlay and upgrade logic
    ├── floor.py             ← Floor layout and monster spawning
    ├── boss_room.py         ← Boss raid encounter system
    ├── quest_room.py        ← Quest encounter system
    ├── skill_bar.py         ← In-game HUD for active skills
    ├── stats_tracker.py     ← CSV data recording
    ├── save_manager.py      ← Save and load logic
    ├── menu.py              ← Pause menu
    ├── audio_manager.py     ← Music and SFX management
    ├── settings.py          ← Screen size, paths, colors
    ├── shop_data.py         ← Upgrade definitions
    ├── skill_data.py        ← Skill definitions
    ├── floor_data.py        ← Floor definitions
    ├── boss_data.py         ← Boss raid definitions
    └── quest_data.py        ← Quest definitions
```

---
---



## Known Bugs

- No major bugs known at this time. 
- *To report a bug, please open an Issue on the repository.*
## External Sources & Credits

This project utilizes several third-party assets to enhance the immersive experience of Aincrad.

### Visuals & UI
- **Typography**: [PixelPurl.ttf](https://fontlink-if-available.com) — A custom pixel font used for the UI and Magic Stones counter.
- **Icons**: [Flaticon](https://www.flaticon.com/) — High-quality UI icons provided by **Smashicons**.
- **Generative AI**: Used for specific environmental textures and concept art.
- **Original Assets**: All character and monster sprites were custom-designed for this project.

### Music (BGM)
- **Main Menu**: *"Game MainMenu Music (4th Album)"* by **Orwa Farran** (Copyright Free).
- **First Floor**: *"Happy Village Town"* via **Motion Array**.
- **Boss raid / Quest**: *Endless Storm* by **Makai-symphony** via **BreakingCopyright** (Royalty Free).

### Sound Effects (SFX)
- **System Start**: *"Game Started"* by **EilasSFX** via [Freesound.org](https://freesound.org).
- **Combat**: *"Sword Slash Sound Effect"* by **Barogs Gaming** (No Copyright).
- **Kills**: *"Big Explosion"* via **Lightning Editor** (Creative Commons).
- **Shop**: *"Pop Sound Effect"* via **UniversalSoundEffects** (Creative Commons).

---

---

## Unfinished Works


This project is under the MIT LICENSE because implementing 100 floor alone take too much time.
If you are ambitious enough to make 100 floor on this pygame feel free to use my code
---