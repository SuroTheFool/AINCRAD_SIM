import os

# ---- SCREEN SETTINGS -----

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "AINCRAD SIMULATOR"

# ----- COLORS CHART -----

COLOR_BG      = (15, 15, 25)      # Dark Blue for the sky
COLOR_WHITE   = (255, 255, 255)
COLOR_ACCENT  = (180, 50, 50)     # Red color


# ---- Path ----

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "images")

