import json
import os

# Save file location — in a "saves" folder at the project root
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVE_PATH = os.path.join(BASE_DIR, "saves", "savegame.json")


def build_save_data(game):
    """
    Collect all data that needs to be saved.
    Called by game before quitting or when player saves manually.

    NOTE: player_stats are NOT saved separately anymore.
    shop_levels is the single source of truth — stats are rebuilt
    from scratch on load by replaying all purchased upgrades.
    Only current_end is saved separately (it's not an upgrade level).
    """
    return {
        "gold"                  : game.gold,
        "current_floor_index"   : game.current_floor_index,
        "current_skin_id"       : game.current_skin["id"],
        "current_end"           : game.player.current_end,   # not rebuilt from levels
        "shop_levels"           : dict(game.shop.levels),    # includes STR/INT/END levels
        "highest_floor_unlocked": game.highest_floor_unlocked,
    }


def save_game(game):
    os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
    data = build_save_data(game)
    with open(SAVE_PATH, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Game saved to {SAVE_PATH}")


def load_game(game):
    if not os.path.exists(SAVE_PATH):
        print("No save file found.")
        return False

    with open(SAVE_PATH, "r") as f:
        data = json.load(f)

    # --- Economy ---
    game.gold = data["gold"]

    # --- Floor ---
    game.go_to_floor(data["current_floor_index"])

    # --- Skin ---
    from .player_data import PLAYER_SKINS
    skin = next(
        (s for s in PLAYER_SKINS if s["id"] == data["current_skin_id"]),
        PLAYER_SKINS[0]
    )
    game.player.change_skin(skin)
    # change_skin() calls __init__ → resets all stats to base values ✅

    # --- Restore shop levels ---
    game.shop.levels = data["shop_levels"]

    # --- Rebuild stats by replaying all purchased upgrades ---
    # This avoids any double-application bug.
    # We replay UPGRADES first, then STATS_UPGRADES.
    from .shop_data import UPGRADES, STATS_UPGRADES

    for upgrade in UPGRADES:
        uid   = upgrade["id"]
        level = game.shop.levels.get(uid, 0)
        for _ in range(level):
            game.shop._apply_upgrade(uid, game.player, UPGRADES)

    for upgrade in STATS_UPGRADES:
        uid   = upgrade["id"]
        level = game.shop.levels.get(uid, 0)
        for _ in range(level):
            game.shop._apply_upgrade(uid, game.player, STATS_UPGRADES)

    # --- Endurance current value (regen state, not a level) ---
    game.player.current_end = data.get("current_end", game.player.endurance * 10)

    # --- Progression ---
    game.highest_floor_unlocked = data.get("highest_floor_unlocked", 0)

    print("Game loaded successfully.")
    return True


def save_exists():
    """Check if a save file exists — used by the menu to enable/disable Load button."""
    return os.path.exists(SAVE_PATH)