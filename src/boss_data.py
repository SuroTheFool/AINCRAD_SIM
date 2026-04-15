import os


# Boss Raid definitions.
#
# Each raid contains :
#   id         : boss floor id (convention : 100 + floor_id)
#   name       : display name of the raid
#   floor_id   : which normal floor this boss belongs to
#   unlocks    : floor INDEX (in FLOORS list) unlocked on victory
#   time_limit : seconds to beat the raid
#   background : subfolder in assets/images/floors/ for the boss room visuals
#   waves      : list of lists — each sublist is one wave of monsters
#                All monsters in a wave must die before the next wave starts
#
# Monster format in waves — same as MONSTER_LIST but inline :
#   name, hp, image_file, display_size, pos (x_base, x_range, y)

BOSS_RAIDS = [
    {
        "id"        : 101,
        "name"      : "Floor 1 Boss — Illfang the Kobold Lord",
        "floor_id"  : 1,       # belongs to Floor 1
        "unlocks"   : 1,       # unlocks FLOORS[1] = Floor 2 on victory
        "time_limit": 120,     # 2 minutes
        "background": os.path.join("floors", "boss_floor_1"),

        "waves": [
            # --- Wave 1 : two Kobold Sentinels ---
            [

                {
                    "name": "Giant slime",
                    "hp": 500,
                    "image_file": "slime_idle.png",
                    "display_size": (500, 540),
                    "pos": (0.86, 0.04, 0.90),
                    "bonus": 5000,
                    "frame_w": 204,
                    "frame_h": 204,
                    "frame_speed": 0.16,
                    "animations": {
                        "idle": {"row": 0, "frame_count": 21},
                    },
                },
                {
                    "name": "Giant slime",
                    "hp": 1000,
                    "image_file": "slime_idle.png",
                    "display_size": (500, 540),
                    "pos": (0.54, 0.04, 0.90),
                    "bonus": 5000,
                    "frame_w": 204,
                    "frame_h": 204,
                    "frame_speed": 0.16,
                    "animations": {
                        "idle": {"row": 0, "frame_count": 21},
                    },
                },

            ],
            # --- Wave 2 : the Boss ---
            [
                {
                    "name"        : "Illfang the Kobold Lord",
                    "hp"          : 3000,
                    "image_file"  : "ilf_first_form.png",
                    "display_size": (615, 430),
                    "pos"         : (0.68, 0.02, 0.83),
                    "bonus"       : 50,
                    "frame_w": 784,
                    "frame_h": 448,
                    "frame_speed": 0.13,
                    "animations": {
                        "idle": {"row": 0, "frame_count": 5},
                    }
                },
                {
                    "name"        : "Kobold Royal guard",
                    "hp"          : 1200,
                    "image_file"  : "royal_guard.png",
                    "display_size": (300, 300),
                    "pos"         : (0.50, 0.02, 0.83),
                    "bonus"       : 50,
                    "frame_w": 204,
                    "frame_h": 203,
                    "frame_speed": 0.13,
                    "animations": {
                        "idle": {"row": 0, "frame_count": 5},
                    }
                },
            ],
            [
                {
                    "name": "Ilf - Awakened",
                    "hp": 6000,
                    "image_file": "final_ilfang_idle.png",
                    "display_size": (560, 480),
                    "pos": (0.67, 0.02, 0.82),
                    "bonus": 0,
                    "frame_w": 204,
                    "frame_h": 169,
                    "frame_speed": 0.13,
                    "animations": {
                        "idle": {"row": 0, "frame_count": 5},
                    }
                },
            ],
        ],
    },
]