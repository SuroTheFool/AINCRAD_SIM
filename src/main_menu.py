import os
import math
import random
import pygame
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT, ASSETS_DIR


# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
FONT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "fonts", "PixelPurl.ttf"
)
BG_PATH          = os.path.join(ASSETS_DIR, "main_bg.jpg")
MUSIC_PATH       = os.path.join(ASSETS_DIR, "..", "sounds", "menu_music.mp3")
START_SOUND_PATH = os.path.join(ASSETS_DIR, "..", "sounds", "sfx", "start.wav")

# ----------------------------------------- ----------------------------------
# PARAMETERS
# ---------------------------------------------------------------------------
ZOOM_SPEED      = 0.34
ZOOM_AMPLITUDE  = 0.01
ZOOM_BASE       = 1.04
VIBRATE_AMOUNT  = 0.7

COLOR_TITLE        = (255, 255, 255)
COLOR_TITLE_SHADOW = (30, 0, 0)
COLOR_SUBTITLE     = (200, 180, 180)
BLINK_SPEED        = 1

MUSIC_VOLUME       = 0.5
FADE_DURATION      = 0.6
VFX_RING_SPEED     = 420
VFX_RING_DURATION  = 0.55
VFX_FLASH_DURATION = 0.18


class MainMenu:
    def __init__(self, screen: pygame.Surface):
        self.screen  = screen
        self.clock   = pygame.time.Clock()
        self.running = True
        self.result  = "quit"

        self._time = 0.0
        self._vx   = 0.0
        self._vy   = 0.0

        self._triggered    = False
        self._fade_elapsed = 0.0

        self._vfx_active    = False
        self._vfx_elapsed   = 0.0
        self._flash_active  = False
        self._flash_elapsed = 0.0

        self._load_background()
        self._load_fonts()
        self._load_sounds()
        self._start_music()

        self._fade_surf  = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._fade_surf.fill((0, 0, 0))
        self._flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._flash_surf.fill((255, 255, 255))

    # ------------------------------------------------------------------
    # LOADING
    # ------------------------------------------------------------------

    def _load_background(self):
        if os.path.exists(BG_PATH):
            raw = pygame.image.load(BG_PATH).convert()
            self._bg_base = pygame.transform.scale(raw, (SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self._bg_base = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self._bg_base.fill((10, 0, 20))

    def _load_fonts(self):
        if os.path.exists(FONT_PATH):
            self.font_title    = pygame.font.Font(FONT_PATH, 88)
            self.font_subtitle = pygame.font.Font(FONT_PATH, 22)
        else:
            self.font_title    = pygame.font.SysFont("Verdana", 72, bold=True)
            self.font_subtitle = pygame.font.SysFont("Verdana", 20)

    def _load_sounds(self):
        self._start_sound = None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except pygame.error:
            return   # no audio device — silent mode

        try:
            path = os.path.normpath(START_SOUND_PATH)
            if os.path.exists(path):
                self._start_sound = pygame.mixer.Sound(path)
                self._start_sound.set_volume(0.75)
        except pygame.error:
            pass

    def _start_music(self):
        try:
            if not pygame.mixer.get_init():
                return
            path = os.path.normpath(MUSIC_PATH)
            if os.path.exists(path):
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(MUSIC_VOLUME)
                pygame.mixer.music.play(-1, fade_ms=1200)
        except pygame.error:
            pass

    # ------------------------------------------------------------------
    # MAIN LOOP
    # ------------------------------------------------------------------

    def run(self) -> str:
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()

        # ← return is OUTSIDE the while loop
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.fadeout(300)
        except pygame.error:
            pass

        return self.result

    # ------------------------------------------------------------------
    # EVENTS
    # ------------------------------------------------------------------

    def _handle_events(self):
        if self._triggered:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.result  = "quit"
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.result  = "quit"

            if event.type == pygame.KEYDOWN:
                self._trigger_start()

            if event.type == pygame.MOUSEBUTTONDOWN:
                self._trigger_start()

    def _trigger_start(self):
        if self._triggered:
            return
        self._triggered = True
        self.result     = "play"

        try:
            if self._start_sound:
                self._start_sound.play()
        except pygame.error:
            pass

        self._vfx_active    = True
        self._vfx_elapsed   = 0.0
        self._flash_active  = True
        self._flash_elapsed = 0.0

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------

    def _update(self, dt: float):
        self._time += dt

        if not self._triggered:
            self._vx = random.uniform(-VIBRATE_AMOUNT, VIBRATE_AMOUNT)
            self._vy = random.uniform(-VIBRATE_AMOUNT, VIBRATE_AMOUNT)

        if self._vfx_active:
            self._vfx_elapsed += dt
            if self._vfx_elapsed >= VFX_RING_DURATION:
                self._vfx_active = False

        if self._flash_active:
            self._flash_elapsed += dt
            if self._flash_elapsed >= VFX_FLASH_DURATION:
                self._flash_active = False

        if self._triggered:
            self._fade_elapsed += dt
            if self._fade_elapsed >= FADE_DURATION:
                self.running = False

    # ------------------------------------------------------------------
    # DRAW
    # ------------------------------------------------------------------

    def _draw(self):
        zoom  = ZOOM_BASE + math.sin(self._time * ZOOM_SPEED) * ZOOM_AMPLITUDE
        new_w = int(SCREEN_WIDTH  * zoom)
        new_h = int(SCREEN_HEIGHT * zoom)

        zoomed = pygame.transform.scale(self._bg_base, (new_w, new_h))
        blit_x = (SCREEN_WIDTH  - new_w) // 2 + int(self._vx)
        blit_y = (SCREEN_HEIGHT - new_h) // 2 + int(self._vy)
        self.screen.blit(zoomed, (blit_x, blit_y))

        cx = SCREEN_WIDTH  // 2
        cy = SCREEN_HEIGHT // 2

        # Titre
        shadow = self.font_title.render("Link Start", True, COLOR_TITLE_SHADOW)
        self.screen.blit(shadow, shadow.get_rect(center=(cx + 4, cy + 4)))
        title = self.font_title.render("Link Start", True, COLOR_TITLE)
        self.screen.blit(title, title.get_rect(center=(cx, cy)))

        # Sous-texte clignotant
        if not self._triggered:
            blink_on = math.sin(self._time * math.pi * BLINK_SPEED) > 0
            if blink_on:
                sub = self.font_subtitle.render(
                    "| Press any key or click to start |", True, COLOR_SUBTITLE
                )
                self.screen.blit(sub, sub.get_rect(center=(cx, cy + 80)))

        # VFX — anneau expansif
        if self._vfx_active:
            t         = self._vfx_elapsed / VFX_RING_DURATION
            radius    = int(t * VFX_RING_SPEED * VFX_RING_DURATION)
            thickness = max(1, int(6 * (1.0 - t)))
            alpha     = int(255 * (1.0 - t) ** 1.5)

            ring_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (255, 255, 255, alpha),
                               (cx, cy), radius, thickness)
            if radius > 30:
                pygame.draw.circle(ring_surf, (200, 180, 255, int(alpha * 0.5)),
                                   (cx, cy), max(0, radius - 25), max(1, thickness - 2))
            self.screen.blit(ring_surf, (0, 0))

        # VFX — flash blanc
        if self._flash_active:
            t = self._flash_elapsed / VFX_FLASH_DURATION
            flash_a = int(200 * (t / 0.3)) if t < 0.3 else int(200 * (1.0 - (t - 0.3) / 0.7))
            self._flash_surf.set_alpha(flash_a)
            self.screen.blit(self._flash_surf, (0, 0))

        # Fondu noir
        if self._triggered:
            delay    = 0.15
            progress = max(0.0, (self._fade_elapsed - delay) / (FADE_DURATION - delay))
            fade_a   = int(255 * min(1.0, progress ** 1.5))
            self._fade_surf.set_alpha(fade_a)
            self.screen.blit(self._fade_surf, (0, 0))

        pygame.display.flip()