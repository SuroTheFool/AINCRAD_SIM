import pygame
import os
from .settings  import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, ASSETS_DIR
from .floor_data import FLOORS
from .boss_data  import BOSS_RAIDS


# --- Overlay dimensions (identiques au shop) ---
OVERLAY_W = 650
OVERLAY_H = 600
OVERLAY_X = SCREEN_WIDTH  // 2 - OVERLAY_W // 2
OVERLAY_Y = SCREEN_HEIGHT // 2 - OVERLAY_H // 2

# --- Colors ---
COLOR_TAB_ACTIVE   = (60,  60,  100)
COLOR_TAB_INACTIVE = (30,  30,  50)
COLOR_ROW_BG       = (35,  35,  60)
COLOR_BTN_GO       = (40,  100, 40)
COLOR_BTN_BOSS     = (140, 30,  30)
COLOR_BTN_LOCKED   = (60,  60,  60)
COLOR_UNLOCKED     = (100, 220, 100)
COLOR_LOCKED       = (180, 60,  60)


def _load_image(filename, size):
    path = os.path.join(ASSETS_DIR, filename)
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()   # ← convert_alpha
        return pygame.transform.scale(img, size)
    else:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill((255, 0, 255, 180))
        return surf


def _create_gradient_surface(width, height, top_color, bottom_color, radius=15):
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


class FloorButton:
    """
    Floor navigator button + overlay.
    Two tabs : TRAVEL (change floor) and BOSS (challenge boss).

    Placed directly above the shop button — same width (180x89).
    """

    def __init__(self, shop_btn_rect):
        self.is_open      = False
        self.active_tab   = "travel"   # "travel" | "boss"

        # --- Fonts ---
        self.font_title = pygame.font.SysFont("Verdana", 24, bold=True)
        self.font_tab   = pygame.font.SysFont("Verdana", 16, bold=True)
        self.font_item  = pygame.font.SysFont("Verdana", 16, bold=True)
        self.font_desc  = pygame.font.SysFont("Verdana", 13)
        self.font_btn   = pygame.font.SysFont("Verdana", 14, bold=True)

        # --- Floor button image ---
        # 856x422 → displayed at 180x89 (same ratio as shop widget)
        self.floor_btn_img  = _load_image("floor_widget.png", (180, 89))

        # Placed directly ABOVE the shop button
        # shop_btn_rect.top = Y of the top edge of the shop button
        # We subtract 10px gap between the two buttons
        self.floor_btn_rect = self.floor_btn_img.get_rect(
            bottomright=(SCREEN_WIDTH - 15, shop_btn_rect.top - 10)
        )

        # --- Overlay background ---
        self.overlay_bg = _create_gradient_surface(
            OVERLAY_W, OVERLAY_H,
            top_color=(30, 50, 80, 245),
            bottom_color=(10, 20, 50, 255),
            radius=20
        )

        # --- Tab rects (inside the overlay) ---
        tab_y     = OVERLAY_Y + 55
        tab_h     = 38
        tab_w     = OVERLAY_W // 2 - 20
        self.tab_travel_rect = pygame.Rect(OVERLAY_X + 10,          tab_y, tab_w, tab_h)
        self.tab_boss_rect   = pygame.Rect(OVERLAY_X + tab_w + 30,  tab_y, tab_w, tab_h)

        # --- Close button ---
        self.close_btn_rect = pygame.Rect(
            OVERLAY_X + OVERLAY_W - 40, OVERLAY_Y + 10, 30, 30
        )

        # --- Action button rects (populated during draw) ---
        # travel tab : { floor_index : pygame.Rect }
        # boss tab   : { floor_id    : pygame.Rect }
        self.go_btn_rects   = {}
        self.boss_btn_rects = {}
        self._update_btn_rects()

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def handle_click(self, mouse_pos, game):
        """
        Process a click.
        Returns "travel" + index, "boss" + floor_id, or None.
        """
        # Floor button toggle
        if self.floor_btn_rect.collidepoint(mouse_pos):
            self.is_open = not self.is_open
            return None

        if not self.is_open:
            return None

        # Close button
        if self.close_btn_rect.collidepoint(mouse_pos):
            self.is_open = False
            return None

        # Tab switching
        if self.tab_travel_rect.collidepoint(mouse_pos):
            self.active_tab = "travel"
            return None
        if self.tab_boss_rect.collidepoint(mouse_pos):
            self.active_tab = "boss"
            return None

        # --- TRAVEL tab : GO buttons ---
        if self.active_tab == "travel":
            for floor_index, rect in self.go_btn_rects.items():
                if rect.collidepoint(mouse_pos):
                    # Only allow travel to unlocked floors
                    if floor_index <= game.highest_floor_unlocked:
                        game.go_to_floor(floor_index)
                        self.is_open = False
                    return None

        # --- BOSS tab : CHALLENGE buttons ---
        if self.active_tab == "boss":
            for floor_id, rect in self.boss_btn_rects.items():
                if rect.collidepoint(mouse_pos):
                    # Find the floor_index for this floor_id
                    floor_index = next(
                        (i for i, f in enumerate(FLOORS) if f["id"] == floor_id), None
                    )
                    # Only allow boss challenge if the floor is unlocked
                    if floor_index is not None and floor_index <= game.highest_floor_unlocked:
                        game.start_boss_raid(floor_id)
                        self.is_open = False
                    return None

        return None

    # ------------------------------------------------------------------
    # DRAW
    # ------------------------------------------------------------------

    def draw_floor_button(self, screen):
        """Draw the floor widget button."""
        screen.blit(self.floor_btn_img, self.floor_btn_rect)

    def draw_overlay(self, screen, game):
        if not self.is_open:
            return

        # Background
        screen.blit(self.overlay_bg, (OVERLAY_X, OVERLAY_Y))

        # Title
        title        = self.font_title.render("FLOOR NAVIGATOR", True, COLOR_WHITE)
        title_shadow = self.font_title.render("FLOOR NAVIGATOR", True, (0, 0, 0))
        title_rect   = title.get_rect(midtop=(OVERLAY_X + OVERLAY_W // 2, OVERLAY_Y + 12))
        screen.blit(title_shadow, (title_rect.x + 2, title_rect.y + 2))
        screen.blit(title, title_rect)

        # Close button
        pygame.draw.line(screen, COLOR_WHITE,
                         (self.close_btn_rect.left + 5,  self.close_btn_rect.top + 5),
                         (self.close_btn_rect.right - 5, self.close_btn_rect.bottom - 5), 3)
        pygame.draw.line(screen, COLOR_WHITE,
                         (self.close_btn_rect.left + 5,  self.close_btn_rect.bottom - 5),
                         (self.close_btn_rect.right - 5, self.close_btn_rect.top + 5), 3)

        # --- Tabs ---
        self._draw_tab(screen, self.tab_travel_rect, "TRAVEL", self.active_tab == "travel")
        self._draw_tab(screen, self.tab_boss_rect,   "BOSS",   self.active_tab == "boss")

        # --- Content ---
        if self.active_tab == "travel":
            self._draw_travel_tab(screen, game)
        else:
            self._draw_boss_tab(screen, game)

    # ------------------------------------------------------------------
    # PRIVATE — Draw helpers
    # ------------------------------------------------------------------

    def _draw_tab(self, screen, rect, label, is_active):
        color = COLOR_TAB_ACTIVE if is_active else COLOR_TAB_INACTIVE
        pygame.draw.rect(screen, color, rect, border_radius=8)
        if is_active:
            pygame.draw.rect(screen, COLOR_WHITE, rect, 1, border_radius=8)
        surf = self.font_tab.render(label, True, COLOR_WHITE)
        screen.blit(surf, surf.get_rect(center=rect.center))

    def _draw_travel_tab(self, screen, game):
        """List all floors with a GO button for unlocked ones."""
        row_y = OVERLAY_Y + 110

        for i, floor in enumerate(FLOORS):
            unlocked   = i <= game.highest_floor_unlocked
            row_rect   = pygame.Rect(OVERLAY_X + 20, row_y, OVERLAY_W - 40, 72)
            pygame.draw.rect(screen, COLOR_ROW_BG, row_rect, border_radius=6)

            # Lock / unlock indicator
            status_color = COLOR_UNLOCKED if unlocked else COLOR_LOCKED
            status_text  = "UNLOCKED" if unlocked else "LOCKED"
            status_surf  = self.font_desc.render(status_text, True, status_color)
            screen.blit(status_surf, (OVERLAY_X + 30, row_y + 10))

            # Floor name
            name_surf = self.font_item.render(floor["name"], True, COLOR_WHITE)
            screen.blit(name_surf, (OVERLAY_X + 30, row_y + 32))

            # GO button
            btn_rect  = self.go_btn_rects[i]
            btn_color = COLOR_BTN_GO if unlocked else COLOR_BTN_LOCKED
            pygame.draw.rect(screen, btn_color, btn_rect, border_radius=6)
            btn_label = self.font_btn.render("GO" if unlocked else "🔒", True, COLOR_WHITE)
            screen.blit(btn_label, btn_label.get_rect(center=btn_rect.center))

            row_y += 82

    def _draw_boss_tab(self, screen, game):
        """List all boss raids with a CHALLENGE button."""
        row_y = OVERLAY_Y + 110

        for raid in BOSS_RAIDS:
            # Find the floor index for this raid
            floor_index = next(
                (i for i, f in enumerate(FLOORS) if f["id"] == raid["floor_id"]), None
            )
            unlocked   = floor_index is not None and floor_index <= game.highest_floor_unlocked
            row_rect   = pygame.Rect(OVERLAY_X + 20, row_y, OVERLAY_W - 40, 90)
            pygame.draw.rect(screen, COLOR_ROW_BG, row_rect, border_radius=6)

            # Raid name
            name_surf = self.font_item.render(raid["name"], True, COLOR_WHITE)
            screen.blit(name_surf, (OVERLAY_X + 30, row_y + 10))

            # Time limit info
            minutes   = raid["time_limit"] // 60
            secs      = raid["time_limit"] % 60
            time_surf = self.font_desc.render(
                f"Time limit : {minutes}:{secs:02d}  —  {len(raid['waves'])} wave(s)",
                True, (180, 180, 220)
            )
            screen.blit(time_surf, (OVERLAY_X + 30, row_y + 36))

            # Status
            status_color = COLOR_UNLOCKED if unlocked else COLOR_LOCKED
            status_text  = "AVAILABLE" if unlocked else "LOCKED"
            status_surf  = self.font_desc.render(status_text, True, status_color)
            screen.blit(status_surf, (OVERLAY_X + 30, row_y + 60))

            # CHALLENGE button
            btn_rect  = self.boss_btn_rects[raid["floor_id"]]
            btn_color = COLOR_BTN_BOSS if unlocked else COLOR_BTN_LOCKED
            pygame.draw.rect(screen, btn_color, btn_rect, border_radius=6)
            btn_label = self.font_btn.render(
                "CHALLENGE" if unlocked else "LOCKED", True, COLOR_WHITE
            )
            screen.blit(btn_label, btn_label.get_rect(center=btn_rect.center))

            row_y += 102

    # ------------------------------------------------------------------
    # PRIVATE — Rect pre-computation
    # ------------------------------------------------------------------

    def _update_btn_rects(self):
        """Pre-compute all button rects — same pattern as Shop."""

        # Travel tab GO buttons
        row_y = OVERLAY_Y + 110
        for i in range(len(FLOORS)):
            self.go_btn_rects[i] = pygame.Rect(
                OVERLAY_X + OVERLAY_W - 130, row_y + 18, 100, 36
            )
            row_y += 82

        # Boss tab CHALLENGE buttons
        row_y = OVERLAY_Y + 110
        for raid in BOSS_RAIDS:
            self.boss_btn_rects[raid["floor_id"]] = pygame.Rect(
                OVERLAY_X + OVERLAY_W - 150, row_y + 22, 120, 40
            )
            row_y += 102