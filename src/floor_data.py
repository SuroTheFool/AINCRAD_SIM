import os
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT

FLOORS = [
    {
        "id": 1,
        "name": "Floor 1 — Starting Plains",
        "monsters": [
            {"name": "Goblin", "weight": 30},
            {"name": "Slime", "weight": 30},
            {"name": "Frenzy Boar", "weight": 40},
            {"name": "Hyperactive Slime", "weight": 5},
        ],
        "layers": [
            {
                "file": os.path.join("floors", "floor_1", "sky.png"),
                "pos": (0, 0),
                "size": (2560, 732),
                "scroll_speed": 0.175,

            },
            {
                "file": os.path.join("floors", "floor_1", "ground.png"),
                "pos": (0, SCREEN_HEIGHT - 520),
                "size": (SCREEN_WIDTH, SCREEN_HEIGHT - 200),
                "scroll_speed": 0,
            },
        ],
        "decorations": [
            # {
            #     "file" : "floors/floor_1/circle_entity.png",
            #     "pos"  : (760, SCREEN_HEIGHT - 300),
            #     "size" : (280, 280), },
        ],
    },
    {
        "id": 2,
        "name": "Floor 2 — Westeria ",
        "monsters": [
            {"name": "Goblin", "weight": 20},
            {"name": "Slime", "weight": 80},
        ],
        "layers": [
            {
                "file": os.path.join("floors", "floor_2", "sky.png"),
                "pos": (0, -430),
                "size": (2560, 1000),
                "scroll_speed": 0.179,

            },
            {
                "file": os.path.join("floors", "floor_2", "ground.png"),
                "pos": (-20, SCREEN_HEIGHT - 800),
                "size": (SCREEN_WIDTH * 1.15, SCREEN_HEIGHT * 1.15),
                "scroll_speed": 0,
            },
        ],
        "decorations": [
            {
                "file" : "floors/floor_2/ruins.png",
                "pos"  : (293   , SCREEN_HEIGHT - 615),
                "size" : (730, 415), },
        ],
    },
]
