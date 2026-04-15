import os
import pygame

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUNDS_DIR = os.path.join(BASE_DIR, "assets", "sounds")
LOG_PATH   = os.path.join(BASE_DIR, "error.log")

MUSIC_MAP = {
    "menu"     : "floor_1.mp3",
    "floor_1"  : "floor_1.mp3",
    "floor_2"  : "floor_1.mp3",
    "boss_raid": "last_boss_raid.mp3",
}

SFX_MAP = {
    "hit"  : "hit.wav",
    "crit" : "crit.wav",
    "death": "death.wav",
    "buy"  : "buy.wav",
}


class AudioManager:
    def __init__(self):
        self._current_track = None
        self._sfx           = {}
        self._mixer_ok      = False

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self._mixer_ok = True
            self._load_sfx()
        except pygame.error as e:
            self._log(f"Mixer unavailable : {e}")

    # ------------------------------------------------------------------
    # MUSIC
    # ------------------------------------------------------------------

    def play_music(self, track_id):
        if not self._mixer_ok:
            return
        if track_id == self._current_track:
            return
        filename = MUSIC_MAP.get(track_id)
        if filename is None:
            return
        path = os.path.join(SOUNDS_DIR, filename)
        if not os.path.exists(path):
            return
        try:
            pygame.mixer.music.fadeout(800)
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.45)
            pygame.mixer.music.play(-1, fade_ms=800)
            self._current_track = track_id
        except pygame.error as e:
            self._log(f"play_music({track_id}) : {e}")

    def stop_music(self):
        if not self._mixer_ok:
            return
        try:
            pygame.mixer.music.fadeout(800)
            self._current_track = None
        except pygame.error:
            pass

    # ------------------------------------------------------------------
    # SFX
    # ------------------------------------------------------------------

    def play_sfx(self, sfx_id):
        if not self._mixer_ok:
            return
        sound = self._sfx.get(sfx_id)
        if sound:
            try:
                sound.set_volume(0.6)
                sound.play()
            except pygame.error:
                pass

    def _load_sfx(self):
        sfx_dir = os.path.join(SOUNDS_DIR, "sfx")
        for sfx_id, filename in SFX_MAP.items():
            path = os.path.join(sfx_dir, filename)
            if os.path.exists(path):
                try:
                    self._sfx[sfx_id] = pygame.mixer.Sound(path)
                except pygame.error as e:
                    self._log(f"_load_sfx({filename}) : {e}")

    # ------------------------------------------------------------------
    # HELPER
    # ------------------------------------------------------------------

    def _log(self, message: str):
        try:
            with open(LOG_PATH, "a", encoding="utf-8") as f:
                f.write(f"[AudioManager] {message}\n")
        except Exception:
            pass