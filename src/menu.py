import pygame
import os
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, ASSETS_DIR
from .save_manager import save_game, load_game, save_exists


# --- Menu overlay dimensions ---
MENU_W = 400
MENU_H = 420
MENU_X = SCREEN_WIDTH  // 2 - MENU_W // 2
MENU_Y = SCREEN_HEIGHT // 2 - MENU_H // 2


def _create_gradient_surface(width, height, top_color, bottom_color, radius=15):
    """Same gradient helper as in shop.py."""
    gradient = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        a = int(top_color[3] + (bottom_color[3] - top_color[3]) * ratio)
        pygame.draw.line(gradient, (r, g, b, a), (0, y), (width, y))
    mask = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius)
    mask.blit(gradient, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pygame.draw.rect(mask, (255, 255, 255, 80), mask.get_rect(), width=2, border_radius=radius)
    return mask


class Menu:
    """
    Pause menu overlay.
    Opens with ESC or the menu button (top-left).
    Contains : Save, Load, and Log Out (save + quit).
    """

    def __init__(self):
        self.is_open     = False
        self.show_feedback = ""      # Temporary message ("Saved !", "Loaded !")
        self.feedback_timer = 0      # Frames remaining to show the message

        # --- Fonts ---
        self.font_title    = pygame.font.SysFont("Verdana", 26, bold=True)
        self.font_btn      = pygame.font.SysFont("Verdana", 18, bold=True)
        self.font_feedback = pygame.font.SysFont("Verdana", 15)

        # --- Background ---
        self.bg = _create_gradient_surface(
            MENU_W, MENU_H,
            top_color=(30, 30, 60, 245),
            bottom_color=(10, 10, 30, 255),
            radius=20
        )

        # --- Menu button (top-left, opens the menu) ---
        self.menu_btn_rect = pygame.Rect(15, 15, 44, 44)

        # --- Close button (X, top-right of overlay) ---
        self.close_btn_rect = pygame.Rect(
            MENU_X + MENU_W - 40, MENU_Y + 10, 30, 30
        )

        # --- Action buttons ---
        # We define them once — centered horizontally in the overlay
        btn_w, btn_h = 280, 52
        btn_x        = MENU_X + MENU_W // 2 - btn_w // 2

        self.btn_save    = pygame.Rect(btn_x, MENU_Y + 100, btn_w, btn_h)
        self.btn_load    = pygame.Rect(btn_x, MENU_Y + 175, btn_w, btn_h)
        self.btn_logout  = pygame.Rect(btn_x, MENU_Y + 300, btn_w, btn_h)

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def toggle(self):
        self.is_open = not self.is_open

    def handle_click(self, mouse_pos, game):
        """
        Process a click and return a string action for Game to handle :
            "save"    → saved successfully
            "load"    → loaded successfully
            "logout"  → save and quit
            None      → no relevant action
        """
        # Menu button (top-left burger icon)
        if self.menu_btn_rect.collidepoint(mouse_pos):
            self.toggle()
            return None

        if not self.is_open:
            return None

        # Close button
        if self.close_btn_rect.collidepoint(mouse_pos):
            self.is_open = False
            return None

        # Save
        if self.btn_save.collidepoint(mouse_pos):
            save_game(game)
            self._show_feedback("Game saved !")
            return "save"

        # Load
        if self.btn_load.collidepoint(mouse_pos):
            if save_exists():
                load_game(game)
                self.is_open = False
                self._show_feedback("Game loaded !")
                return "load"
            else:
                self._show_feedback("No save file found !")
                return None

        # Log out — save then quit
        if self.btn_logout.collidepoint(mouse_pos):
            save_game(game)
            return "logout"

        return None

    def update(self):
        """Countdown the feedback message timer."""
        if self.feedback_timer > 0:
            self.feedback_timer -= 1
            if self.feedback_timer == 0:
                self.show_feedback = ""

    # ------------------------------------------------------------------
    # DRAW
    # ------------------------------------------------------------------

    def draw_menu_button(self, screen):
        """Draw the burger icon (≡) in the top-left corner."""
        pygame.draw.rect(screen, (40, 40, 70), self.menu_btn_rect, border_radius=8)
        pygame.draw.rect(screen, COLOR_WHITE,  self.menu_btn_rect, 2, border_radius=8)

        # Three horizontal lines = burger icon
        lx  = self.menu_btn_rect.x + 9
        ly  = self.menu_btn_rect.y
        lw  = 26
        for offset in [14, 22, 30]:
            pygame.draw.line(screen, COLOR_WHITE,
                             (lx, ly + offset), (lx + lw, ly + offset), 3)

    def draw_overlay(self, screen):
        if not self.is_open:
            # Still draw feedback message even if menu is closed
            self._draw_feedback(screen)
            return

        # Background
        screen.blit(self.bg, (MENU_X, MENU_Y))

        # Title
        title      = self.font_title.render("MENU", True, COLOR_WHITE)
        title_shadow = self.font_title.render("MENU", True, (0, 0, 0))
        title_rect = title.get_rect(midtop=(MENU_X + MENU_W // 2, MENU_Y + 20))
        screen.blit(title_shadow, (title_rect.x + 2, title_rect.y + 2))
        screen.blit(title, title_rect)

        # Close button (X lines)
        pygame.draw.line(screen, COLOR_WHITE,
                         (self.close_btn_rect.left + 5,  self.close_btn_rect.top + 5),
                         (self.close_btn_rect.right - 5, self.close_btn_rect.bottom - 5), 3)
        pygame.draw.line(screen, COLOR_WHITE,
                         (self.close_btn_rect.left + 5,  self.close_btn_rect.bottom - 5),
                         (self.close_btn_rect.right - 5, self.close_btn_rect.top + 5), 3)

        # Action buttons
        self._draw_button(screen, self.btn_save,   "SAVE GAME",  (50, 100, 50))
        self._draw_button(screen, self.btn_load,   "LOAD GAME",
                          (50, 70, 120) if save_exists() else (60, 60, 60))
        self._draw_button(screen, self.btn_logout, "LOG OUT",    (140, 30, 30))

        # Separator line above Log Out
        sep_y = self.btn_logout.top - 20
        pygame.draw.line(screen, (255, 255, 255, 60),
                         (MENU_X + 30, sep_y), (MENU_X + MENU_W - 30, sep_y), 1)

        self._draw_feedback(screen)

    # ------------------------------------------------------------------
    # PRIVATE
    # ------------------------------------------------------------------

    def _draw_button(self, screen, rect, label, color):
        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255, 60), rect, 1, border_radius=8)
        surf = self.font_btn.render(label, True, COLOR_WHITE)
        screen.blit(surf, surf.get_rect(center=rect.center))

    def _show_feedback(self, message):
        self.show_feedback  = message
        self.feedback_timer = 120   # 2 seconds at 60 FPS

    def _draw_feedback(self, screen):
        if not self.show_feedback:
            return
        surf = self.font_feedback.render(self.show_feedback, True, (180, 255, 180))
        screen.blit(surf, surf.get_rect(
            midtop=(SCREEN_WIDTH // 2, MENU_Y + MENU_H + 10)
        ))