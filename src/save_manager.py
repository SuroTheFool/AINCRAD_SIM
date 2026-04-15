import json
import os
import sys
import traceback

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVE_PATH = os.path.join(BASE_DIR, "saves", "savegame.json")
LOG_PATH  = os.path.join(BASE_DIR, "error.log")


def _log_error(context: str, exc: Exception):
    """Write error to error.log — works in .exe where console is absent."""
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"\n[{context}]\n")
            traceback.print_exc(file=f)
    except Exception:
        pass


def build_save_data(game):
    """
    Collect all persistent data.
    shop_levels is the single source of truth for player stats.
    skill_owned and skill_slots are now saved separately.
    """
    return {
        "gold"                  : game.gold,
        "current_floor_index"   : game.current_floor_index,
        "current_skin_id"       : game.current_skin["id"],
        "current_end"           : game.player.current_end,
        "shop_levels"           : dict(game.shop.levels),
        "highest_floor_unlocked": game.highest_floor_unlocked,
        # ── Bug fix 3 : active skills persistence ──
        "skill_owned"           : dict(game.shop.skill_owned),
        "skill_slots"           : list(game.player.skill_slots),
        "completed_quests"      : list(game.completed_quests),
    }


def save_game(game):
    try:
        os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
        data = build_save_data(game)
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        _log_error("save_game", e)


def load_game(game):
    if not os.path.exists(SAVE_PATH):
        return False

    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        _log_error("load_game - read file", e)
        return False

    try:
        # --- Economy ---
        game.gold = data.get("gold", 0)

        # --- Floor ---
        game.go_to_floor(data.get("current_floor_index", 0))

        # --- Skin ---
        from .player_data import PLAYER_SKINS
        skin = next(
            (s for s in PLAYER_SKINS if s["id"] == data.get("current_skin_id")),
            PLAYER_SKINS[0]
        )
        game.player.change_skin(skin)

        # --- Shop levels ---
        saved_levels = data.get("shop_levels", {})
        for key in game.shop.levels:
            if key in saved_levels:
                game.shop.levels[key] = saved_levels[key]

        # --- Rebuild stats by replaying all purchased upgrades ---

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

        game.player.current_end = data.get("current_end", game.player.endurance * 10)

        game.highest_floor_unlocked = data.get("highest_floor_unlocked", 0)
        game.completed_quests = set(data.get("completed_quests", []))
        saved_owned = data.get("skill_owned", {})
        for skill_id in game.shop.skill_owned:
            if skill_id in saved_owned:
                game.shop.skill_owned[skill_id] = saved_owned[skill_id]

        saved_slots = data.get("skill_slots", [None] * 5)
        for i, slot in enumerate(saved_slots[:5]):
            game.player.skill_slots[i] = slot

        return True

    except Exception as e:
        _log_error("load_game - restore data", e)
        return False


def save_exists():
    return os.path.exists(SAVE_PATH)