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
        "label"       : "What an Amazing World",
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
                        "pos"         : (0.43, 0.04, 0.78),
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
                        "pos": (0.54, 0.04, 0.78),
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
            {"type": "gold",         "amount": 650},
            {"type": "stat", "stat": "intelligence", "amount": 3},
            # {"type": "hidden_skill", "skill_id": "double_strike"},
        ],
    },

    # ----------------------------------------------------------------
    # FLOOR 1 — Quest 2 : Dark Elf Ambush
    # Kizmel helps wave 1 only — disappears on wave 2 (boss wave)
    # ----------------------------------------------------------------
    {
        "id"          : "floor1_lam2",
        "label"       : "What an Amazing World 2",
        "description" : "Be prepared this quest is not a joke.",
        "floor_id"    : 1,
        "unlocked_by" : "floor1_lam",
        "background"  : os.path.join("floors", "quests"),
        "time_limit"  : 75,

        "waves": [
            {
                "mobs": [
                    {
                        "name"        : "Golem Boar",
                        "hp"          : 80,
                        "image_file"  : "frenzy_glitch_idle.png",
                        "display_size": (200, 200),
                        "pos"         : (0.40, 0.04, 0.78),
                        "frame_w": 498,
                        "frame_h": 498,
                        "frame_speed": 0.12,
                        "animations": {
                            "idle": {"row": 0, "frame_count": 8},
                        },
                        "bonus"       : 10,
                        "dialog"      : {0.3: "GROAR!"},
                    }
                ],
                "allies_present": ["Lam"],
            },
            {
                "mobs": [
                    {
                        "name": "Golem Boar",
                        "hp": 80,
                        "image_file": "frenzy_glitch_idle.png",
                        "display_size": (200, 200),
                        "pos": (0.365, 0.04, 0.78),
                        "frame_w": 498,
                        "frame_h": 498,
                        "frame_speed": 0.12,
                        "animations": {
                            "idle": {"row": 0, "frame_count": 8},
                        },
                        "bonus": 10,
                        "dialog": {0.3: "GROAR!"},
                    },
                    {
                        "name": "Golem Boar",
                        "hp": 80,
                        "image_file": "frenzy_glitch_idle.png",
                        "display_size": (220, 220),
                        "pos": (0.54, 0.01 , 0.82),
                        "frame_w": 498,
                        "frame_h": 498,
                        "frame_speed": 0.12,
                        "animations": {
                            "idle": {"row": 0, "frame_count": 8},
                        },
                        "bonus": 10,
                        "dialog": {0.3: "GROAR!"},
                    },
                ],

                "allies_present": ["Lam"],
            },
            {
                "mobs": [
                    {
                        "name": "Lam",
                        "hp": 500,
                        "image_file": "lam_ennemy_idle.png",
                        "display_size": (170, 330),
                        "pos": (0.63, 0.008, 0.79),
                        "frame_w": 390,
                        "frame_h": 718,
                        "frame_speed": 0.12,
                        "animations": {
                            "idle": {"row": 0, "frame_count": 16},
                        },
                        "bonus": 10,
                        "dialog": {1: "Thank you far taking the aggro, You made things easier for me.",
                                   0.85: "If only you could simply stay at the town and enjoy this world like the others",
                                   0.5: "Wow you don't give up impressive, So it's true that you get stronger When you fight to survive",
                                   0.3: "Promising people like you disturb my sleep, just thinking about returning in the real world make me mad!",
                                   0.1: "Things are about to get serious."
                                   },

                    },

                    {
                        "name": "Golem Boar",
                        "hp": 80,
                        "image_file": "frenzy_glitch_idle.png",
                        "display_size": (200, 200),
                        "pos": (0.365, 0.04, 0.78),
                        "frame_w": 498,
                        "frame_h": 498,
                        "frame_speed": 0.12,
                        "animations": {
                            "idle": {"row": 0, "frame_count": 8},
                        },
                        "bonus": 10,
                        "dialog": {0.3: "GROAR!"},
                    },
{
                        "name": "Dark Slime",
                        "hp": 120,
                        "image_file": "dark_slime_idle.png",
                        "display_size": (150, 120),
                        "pos": (0.52, 0.04, 0.78),
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
                "allies_present": [],
            },
            {
                "mobs": [
                    {
                        "name": "Lam",
                        "hp": 2500,
                        "image_file": "lam_ennemy_idle.png",
                        "display_size": (170, 330),
                        "pos": (0.54, 0.008, 0.79),
                        "frame_w": 390,
                        "frame_h": 718,
                        "frame_speed": 0.12,
                        "animations": {
                            "idle": {"row": 0, "frame_count": 16},
                        },
                        "bonus": 10,
                        "dialog": {1: "I hate taking a human life by my own hands... but you leave me no choice",
                                   0.85: "Pft, you still don't get it ? Once we clear this game do you think the government is going to help us integrate in the society?",
                                   0.7: "We have an opportunity to live without working for the rest of our lives, but you prefer to be utopic",
                                   0.5: "Give up already...",
                                   0.35: "HOW CAN YOU STILL BE HERE, I'M A BETA TESTER ! TAKING DOWN A NEWBIE LIKE YOU SHOULD BE NOTHING",
                                   0.21: "Just cancel the quest my friend, you're not going to take my life right ?",
                                   0.18: "Please stop it.",
                                   0.05: "What a shame... Loosing this perfect world"
                                   },

                    },
                ],
                "allies_present": [],
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
                    "I was a beta-tester , I even made it to the 36th floor",
                    "You have too much potential you might finish this game... I don't like it",
                ],
            },
        ],

        "reward": [
            {"type": "stat",           "stat": "strength",     "amount": 4},
            {"type": "stat",           "stat": "intelligence", "amount": 1},
            {"type": "gold",           "amount": 1040},
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