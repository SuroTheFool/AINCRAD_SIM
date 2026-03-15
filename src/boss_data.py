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
                    "name"        : "Kobold Sentinel",
                    "hp"          : 300,
                    "image_file"  : "ilfang_first_form.png",
                    "display_size": (220, 220),
                    "pos"         : (0.55, 0.02, 0.72),
                    "bonus"       : 0,
                },
                {
                    "name"        : "Kobold Sentinel",
                    "hp"          : 300,
                    "image_file"  : "kobold_sentinel.png",
                    "display_size": (220, 280),
                    "pos"         : (0.75, 0.02, 0.72),
                    "bonus"       : 0,
                },
            ],
            # --- Wave 2 : the Boss ---
            [
                {
                    "name"        : "Illfang the Kobold Lord",
                    "hp"          : 2000,
                    "image_file"  : "ilfang_angry.png",
                    "display_size": (380, 380),
                    "pos"         : (0.68, 0.02, 0.68),
                    "bonus"       : 50,
                },
            ],
        ],
    },
]