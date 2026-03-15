import os
import pygame

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUNDS_DIR = os.path.join(BASE_DIR, "assets", "sounds")

MUSIC_MAP = {
    "menu"     : "floor_1.mp3",
    "floor_1"  : "floor_1.mp3",
    "floor_2"  : "floor_1.mp3",
    "boss_raid": "last_boss_raid.mp3",
}

SFX_MAP = {
    "hit"   : "hit.wav",
    "crit"  : "crit.wav",
    "death" : "death.wav",
    "buy"   : "buy.wav",
}

class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self._current = None
        self._sfx = {}        # { "hit": pygame.mixer.Sound, ... }
        self._load_sfx()

    def _load_sfx(self):
        sfx_dir = os.path.join(SOUNDS_DIR, "sfx")
        for sfx_id, filename in SFX_MAP.items():
            path = os.path.join(sfx_dir, filename)
            if os.path.exists(path):
                self._sfx[sfx_id] = pygame.mixer.Sound(path)
            else:
                print(f"Missing sfx {path}")

    def play_music(self, track_id):
        if track_id == self._current:
            return
        path = os.path.join(SOUNDS_DIR, MUSIC_MAP[track_id])
        pygame.mixer.music.fadeout(800)
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(0.09)
        pygame.mixer.music.play(-1, fade_ms=800)
        self._current = track_id

    def play_sfx(self, sfx_id):
        sound = self._sfx.get(sfx_id)
        if sound:
            sound.set_volume(0.04)
            sound.play()
