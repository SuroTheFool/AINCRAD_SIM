# quest_data.py
# ============================================================
# Wave format change :
#   Each wave is now a dict with two keys :
#     "mobs"           : list of mob data dicts
#     "allies_present" : list of ally names active this wave
#                        empty list = no allies this wave
# ============================================================

import os

QUESTS = [

    # ----------------------------------------------------------------
    # FLOOR 1 — Quest 1 : The First Trial
    # ----------------------------------------------------------------
    {
        "id"          : "floor1_lam",
        "label"       : "What an amazing World 1",
        "description" : "Defeat the monster that doesn't belong to this floor with Lam help.",
        "floor_id"    : 1,
        "unlocked_by" : None,
        "background"  : os.path.join("floors", "quests"),
        "time_limit"  : 90,

        "waves": [
            {
                "mobs": [
                    {
                        "name"        : "Dark Slime",
                        "hp"          : 100,
                        "image_file"  : "dark_slime_idle.png",
                        "display_size": (210, 150),
                        "pos"         : (0.50, 0.04, 0.78),
                        "frame_w": 528,
                        "frame_h": 403,
                        "frame_speed": 0.12,
                        "animations": {
                            "idle": {"row": 0, "frame_count": 12},
                        },
                        "bonus"       : 10,
                        "dialog"      : {
                            1.0 : "Blurb blurb blurb (Oh 2 Noobs,I'm really lucky today)",
                            0.2 : "BLURB BLURB FDKJHSDFJ BLURB ! (I'm going to die for REAL !)",
                        },
                    },
                ],
                "allies_present": ["Lam"],   # Lam fighting in this wave
            },
            {
                "mobs": [
                    {
                        "name": "Dark Slime",
                        "hp": 120,
                        "image_file": "dark_slime_idle.png",
                        "display_size": (150, 120),
                        "pos": (0.58, 0.04, 0.78),
                        "frame_w": 528,
                        "frame_h": 403,
                        "frame_speed": 0.12,
                        "animations": {
                            "idle": {"row": 0, "frame_count": 12},
                        },
                        "bonus": 10,
                        "dialog": {
                            1.0: "BLOU",
                        },
                    },
                    {
                        "name": "Dark Slime",
                        "hp": 120,
                        "image_file": "dark_slime_idle.png",
                        "display_size": (150, 120),
                        "pos": (0.38, 0.04, 0.78),
                        "frame_w": 528,
                        "frame_h": 403,
                        "frame_speed": 0.12,
                        "animations": {
                            "idle": {"row": 0, "frame_count": 12},
                        },
                        "bonus": 10,
                        "dialog": {
                            1.0: "Bluib (nah we'd win)",
                            0.2: "Bleurp",
                    },
                    }


                ],
                "allies_present": ["Lam"],   # Lam stays for wave 2
            },
            {
                "mobs": [
                    {
                        "name": "Dark Slime",
                        "hp": 120,
                        "image_file": "dark_slime_idle.png",
                        "display_size": (360, 293),
                        "pos": (0.54g, 0.04, 0.78),
                        "frame_w": 528,
                        "frame_h": 403,
                        "frame_speed": 0.12,
                        "animations": {
                            "idle": {"row": 0, "frame_count": 12},
                        },
                        "bonus": 10,
                        "dialog": {
                            1.0: "BLOU",
                        },
                    },
                ],
                "allies_present": ["Lam"],   # Lam stays for wave 2
            },
        ],

        "allies": [
            {
                "name"        : "Lam",
                "image_file"  : "lam_idle.png",
                "display_size": (280, 520),
                "pos"         : (0.64, 1.045),
                "frame_w": 364,
                "frame_h": 656,
                "frame_speed": 0.12,
                "animations": {
                    "idle": {"row": 0, "frame_count": 9},
                },
                "auto_dps"    : 8,
                "dps_interval": 1.2,
                "dialog"      : [
                    "Hi my friend! Don't worry I'm a pro at this game, I'll carry you",
                    "This world is amazing right ? I never want to get home",
                    "This level of detail... It's so much better than the real world"
                ],
            },
        ],

        "reward": [
            {"type": "gold",         "amount": 3400},
            {"type": "stat", "stat": "intelligence", "amount": 3},
            # {"type": "hidden_skill", "skill_id": "double_strike"},
        ],
    },

    # ----------------------------------------------------------------
    # FLOOR 1 — Quest 2 : Dark Elf Ambush
    # Kizmel helps wave 1 only — disappears on wave 2 (boss wave)
    # ----------------------------------------------------------------
    {
        "id"          : "floor1_ambush",
        "label"       : "Dark Elf Ambush",
        "description" : "Survive the ambush in the catacombs.",
        "floor_id"    : 1,
        "unlocked_by" : "floor1_trial",
        "background"  : os.path.join("floors", "boss_floor_1"),
        "time_limit"  : 75,

        "waves": [
            {
                "mobs": [
                    {
                        "name"        : "Dark Elf Scout",
                        "hp"          : 80,
                        "image_file"  : "goblin_idle.png",
                        "display_size": (180, 220),
                        "pos"         : (0.60, 0.04, 0.78),
                        "bonus"       : 5,
                        "dialog"      : {0.3: "Retreat !"},
                    },
                    {
                        "name"        : "Dark Elf Scout",
                        "hp"          : 80,
                        "image_file"  : "goblin_idle.png",
                        "display_size": (180, 220),
                        "pos"         : (0.75, 0.04, 0.78),
                        "bonus"       : 5,
                        "dialog"      : {0.3: None},
                    },
                    {
                        "name"        : "Dark Elf Scout",
                        "hp"          : 80,
                        "image_file"  : "goblin_idle.png",
                        "display_size": (180, 220),
                        "pos"         : (0.85, 0.02, 0.78),
                        "bonus"       : 5,
                        "dialog"      : None,
                    },
                ],
                "allies_present": ["Kizmel"],   # Kizmel helps wave 1
            },
            {
                "mobs": [
                    {
                        "name"        : "Dark Elf Commander",
                        "hp"          : 450,
                        "image_file"  : "ilfang_angry.png",
                        "display_size": (260, 310),
                        "pos"         : (0.68, 0.02, 0.80),
                        "bonus"       : 50,
                        "dialog"      : {
                            0.6 : "You insects...",
                            0.3 : "I underestimated you.",
                            0.1 : "This floor... will be your grave.",
                        },
                    },
                ],
                "allies_present": [],           # Kizmel gone — you face the boss alone
            },
        ],

        "allies": [
            {
                "name"        : "Kizmel",
                "image_file"  : "kizmel_idle.png",
                "display_size": (180, 220),
                "pos"         : (0.30, 0.82),
                "frame_w"     : None,
                "frame_h"     : None,
                "frame_speed" : 0.12,
                "animations"  : None,
                "auto_dps"    : 10,
                "dps_interval": 1.0,
                "dialog"      : [
                    "I'll handle the scouts !",
                    None,   # Kizmel says nothing on wave 2 — she's already gone
                ],
            },
        ],

        "reward": [
            {"type": "stat",           "stat": "strength",     "amount": 2},
            {"type": "stat",           "stat": "intelligence", "amount": 1},
            {"type": "hidden_upgrade", "skill_id": "double_strike"},
        ],
    },

    # ----------------------------------------------------------------
    # FLOOR 1 — Quest 3 : Elven Legacy
    # No allies at all
    # ----------------------------------------------------------------
    {
        "id"          : "floor1_legacy",
        "label"       : "Elven Legacy",
        "description" : "Protect the ancient elven monument.",
        "floor_id"    : 1,
        "unlocked_by" : "floor1_ambush",
        "background"  : os.path.join("floors", "boss_floor_1"),
        "time_limit"  : 100,

        "waves": [
            {
                "mobs": [
                    {
                        "name"        : "Stone Golem",
                        "hp"          : 200,
                        "image_file"  : "frenzy_boar.png",
                        "display_size": (300, 240),
                        "pos"         : (0.65, 0.03, 0.80),
                        "bonus"       : 20,
                        "dialog"      : {0.5: "GROAR", 0.2: None},
                    },
                ],
                "allies_present": [],
            },
            {
                "mobs": [
                    {
                        "name"        : "Stone Golem",
                        "hp"          : 200,
                        "image_file"  : "frenzy_boar.png",
                        "display_size": (300, 240),
                        "pos"         : (0.60, 0.03, 0.80),
                        "bonus"       : 20,
                        "dialog"      : None,
                    },
                    {
                        "name"        : "Stone Golem",
                        "hp"          : 200,
                        "image_file"  : "frenzy_boar.png",
                        "display_size": (300, 240),
                        "pos"         : (0.80, 0.02, 0.80),
                        "bonus"       : 20,
                        "dialog"      : None,
                    },
                ],
                "allies_present": [],
            },
        ],

        "allies": [],   # no allies for this quest

        "reward": [
            {"type": "gold", "amount": 1200},
            {"type": "stat", "stat": "endurance", "amount": 3},
        ],
    },
]


# ============================================================
# HELPERS
# ============================================================

def get_quests_for_floor(floor_id: int) -> list:
    return [q for q in QUESTS if q["floor_id"] == floor_id]


def get_available_quests(floor_id: int, completed_ids: set) -> list:
    result = []
    for q in QUESTS:
        if q["floor_id"] != floor_id:
            continue
        if q["id"] in completed_ids:
            continue
        prereq = q.get("unlocked_by")
        if prereq is None or prereq in completed_ids:
            result.append(q)
    return result


def get_quest_by_id(quest_id: str):
    return next((q for q in QUESTS if q["id"] == quest_id), None)