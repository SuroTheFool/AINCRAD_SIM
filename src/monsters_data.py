MONSTER_LIST = [
    # {
    #     "name"        : "Goblin",
    #     "hp"          : 100,
    #     "image_file"  : "goblin.png",
    #     "display_size": (320, 320),
    #     "pos": (0.796, 0.86),
    #     "bonus" : 0
    # },
    {
        "name"        : "Slime",
        "hp"          : 50,
        "image_file"  : "slime_idle.png",
        "display_size": (240, 263),
        "pos": (0.7, 0.89),
        "bonus" : 2000,
        "frame_w": 204,
        "frame_h": 204,
        "frame_speed": 0.16,
        "animations": {
            "idle": {"row": 0, "frame_count": 21},
        }
    },
    {
        "name"        : "Hyperactive Slime",
        "hp"          : 250,
        "image_file"  : "slime_idle.png",
        "display_size": (100, 100),
        "pos": (0.6, 0.835),
        "bonus" : 200,
        "frame_w": 204,
        "frame_h": 204,
        "frame_speed": 0.60,
        "animations": {
            "idle": {"row": 0, "frame_count": 21},
        }
    },
    {
        "name": "Frenzy Boar",
        "hp": 80,
        "image_file": "frenzy_boar_idle.png",
        "display_size": (230, 230),
        "pos": (0.67    , 0.87),
        "bonus" : 0,
        "frame_w": 236,
        "frame_h": 236,
        "frame_speed": 0.064,
        "animations": {
            "idle": {"row": 0, "frame_count": 8},
            # "hurt" : {"row": 1, "frame_count": 2},
            # "death": {"row": 2, "frame_count": 5},
        },
    },
{
    "name"        : "Goblin",
    "hp"          : 200,
    "image_file"  : "goblin_idle.png",
    "display_size": (285, 300),
    "pos"         : (0.7, 0.90),
    "bonus"       : 5,
    "frame_w"     : 204,
    "frame_h"     : 204,
    "frame_speed" : 0.12,
    "animations"  : {
        "idle" : {"row": 0, "frame_count": 8},
        # "hurt" : {"row": 1, "frame_count": 2},
        # "death": {"row": 2, "frame_count": 5},
    },
}
]