import pygame
import os
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT, ASSETS_DIR
from .skill_data import ACTIVE_SKILLS

# ------------------------------------------------------------------
# Layout constants
# ------------------------------------------------------------------
SLOT_SIZE    = 64          # width & height of each skill slot square
SLOT_GAP     = 10          # gap between slots
SLOT_COUNT   = 5

# Total bar width = 5 slots + 4 gaps
BAR_W = SLOT_COUNT * SLOT_SIZE + (SLOT_COUNT - 1) * SLOT_GAP

# Horizontal center of the skill bar on screen
BAR_CENTER_X = SCREEN_WIDTH // 2

# Bottom of the slot row — sits just above the bottom HUD area
SLOT_ROW_BOTTOM = SCREEN_HEIGHT - 18

# Y positions derived from slot row
SLOT_Y     = SLOT_ROW_BOTTOM - SLOT_SIZE          # top-left y of slots
END_BAR_H  = 12                                    # endurance bar height
END_BAR_Y  = SLOT_Y - END_BAR_H - 6               # bar sits 6px above slots
END_BAR_X  = BAR_CENTER_X - BAR_W // 2            # aligned with slots

# Colors
COLOR_SLOT_BG       = (30,  10,  10,  200)   # empty slot background
COLOR_SLOT_BORDER   = (140, 60,  60,  255)   # slot border
COLOR_SLOT_ACTIVE   = (255, 200, 60,  255)   # border when effect is running
COLOR_SLOT_NO_END   = (80,  30,  30,  200)   # not enough endurance
COLOR_KEY_LABEL     = (200, 200, 200)
COLOR_END_FILL      = (80,  180, 255)
COLOR_END_BG        = (20,  20,  60,  200)
COLOR_END_TEXT      = (200, 230, 255)
COLOR_TIMER_BAR     = (255, 180, 50)
COLOR_WHITE         = (255, 255, 255)
COLOR_DARK          = (15,  10,  10)

# Key labels shown on each slot
KEY_LABELS = ["1", "2", "3", "4", "5"]

# Pygame key constants for 1-5 (work regardless of CAPS LOCK)
SKILL_KEYS = [
    pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
    pygame.K_KP1, pygame.K_KP2, pygame.K_KP3, pygame.K_KP4, pygame.K_KP5,
]
# K_1..K_5 = top row,  K_KP1..K_KP5 = numpad (bonus)


def _load_icon(filename, size):
    path = os.path.join(ASSETS_DIR, filename)
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill((255, 0, 255, 160))
    return surf


class SkillBar:
    """
    - Slots display the equipped skill icon + key label
    - A duration bar drains inside the slot while effect is active
    - Slot darkens when endurance is insufficient
    - Keys 1-5 (top row + numpad) fire skills, CAPS LOCK independent
    """

    def __init__(self):
        # Pre-load all active skill icons
        self.icons = {
            s["id"]: _load_icon(s["icon"], (SLOT_SIZE - 8, SLOT_SIZE - 8))
            for s in ACTIVE_SKILLS
        }

        # Fonts
        self.font_key   = pygame.font.SysFont("Verdana", 12, bold=True)
        self.font_label = pygame.font.SysFont("Verdana", 10)
        self.font_end   = pygame.font.SysFont("Verdana", 11, bold=True)
        self.font_cost  = pygame.font.SysFont("Verdana", 10)

        # Pre-compute slot rects
        self.slot_rects = self._build_slot_rects()

        # Endurance bar rect
        self.end_bar_rect = pygame.Rect(END_BAR_X, END_BAR_Y, BAR_W, END_BAR_H)

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def handle_keydown(self, event, player, monster=None):
        """
        Call this from Game._handle_events() on KEYDOWN.
        Fires the skill mapped to keys 1-5 (top row) or numpad 1-5.

        Returns (damage, skill_id) or (None, skill_id) or (None, None).
        CAPS LOCK does not affect digit keys — pygame.K_1..K_5 are
        layout-independent (they respond to the physical key, not the
        character produced).
        """
        # Map key → slot index
        slot_index = None
        top_row  = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]
        num_pad  = [pygame.K_KP1, pygame.K_KP2, pygame.K_KP3, pygame.K_KP4, pygame.K_KP5]

        if event.key in top_row:
            slot_index = top_row.index(event.key)
        elif event.key in num_pad:
            slot_index = num_pad.index(event.key)

        if slot_index is None:
            return None, None

        return player.use_skill(slot_index, monster)

    def draw(self, screen, player):
        """Draw endurance bar + skill slots. Call after floor/player draw."""
        self._draw_endurance_bar(screen, player)
        self._draw_slots(screen, player)

    # ------------------------------------------------------------------
    # DRAW — ENDURANCE BAR
    # ------------------------------------------------------------------

    def _draw_endurance_bar(self, screen, player):
        max_end = player.max_endurance()
        cur_end = player.current_end

        # Background
        bg_surf = pygame.Surface((BAR_W, END_BAR_H), pygame.SRCALPHA)
        bg_surf.fill(COLOR_END_BG)
        screen.blit(bg_surf, (END_BAR_X, END_BAR_Y))

        # Fill
        ratio   = max(0.0, min(1.0, cur_end / max(1, max_end)))
        fill_w  = int(BAR_W * ratio)
        if fill_w > 0:
            pygame.draw.rect(screen, COLOR_END_FILL,
                             (END_BAR_X, END_BAR_Y, fill_w, END_BAR_H),
                             border_radius=4)

        # Border
        pygame.draw.rect(screen, (100, 140, 200),
                         (END_BAR_X, END_BAR_Y, BAR_W, END_BAR_H),
                         width=1, border_radius=4)

        # Text label — "END  60 / 100" centered above the bar
        label = self.font_end.render(
            f"END  {int(cur_end)} / {int(max_end)}", True, COLOR_END_TEXT
        )
        screen.blit(label, label.get_rect(
            midbottom=(BAR_CENTER_X, END_BAR_Y - 3)
        ))

    # ------------------------------------------------------------------
    # DRAW — SLOTS
    # ------------------------------------------------------------------

    def _draw_slots(self, screen, player):
        for i, rect in enumerate(self.slot_rects):
            skill_id = player.skill_slots[i]
            skill    = self._get_skill(skill_id)

            # Determine slot state
            can_use   = False
            is_active = False
            if skill:
                can_use   = player.current_end >= skill["cost_end"]
                is_active = player.has_active_effect(skill_id)

            self._draw_slot_bg(screen, rect, skill, can_use, is_active)

            if skill:
                self._draw_slot_icon(screen, rect, skill_id)
                self._draw_slot_timer(screen, rect, skill_id, skill, player)
                self._draw_slot_cost(screen, rect, skill)

            self._draw_slot_key_label(screen, rect, i)

    def _draw_slot_bg(self, screen, rect, skill, can_use, is_active):
        """Draw slot background + border."""
        # Background
        bg = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        if skill is None:
            bg.fill(COLOR_SLOT_BG)
        elif not can_use:
            bg.fill(COLOR_SLOT_NO_END)
        else:
            bg.fill((20, 10, 10, 210))
        screen.blit(bg, rect.topleft)

        # Border — golden if effect is running, normal otherwise
        border_color = COLOR_SLOT_ACTIVE if is_active else COLOR_SLOT_BORDER
        border_width = 2 if is_active else 1
        pygame.draw.rect(screen, border_color, rect,
                         width=border_width, border_radius=6)

    def _draw_slot_icon(self, screen, rect, skill_id):
        """Blit the skill icon centered in the slot."""
        icon = self.icons.get(skill_id)
        if icon:
            icon_rect = icon.get_rect(center=rect.center)
            screen.blit(icon, icon_rect)

    def _draw_slot_timer(self, screen, rect, skill_id, skill, player):
        """
        For duration skills currently active, draw a draining bar
        at the bottom of the slot.

        Full bar = skill["duration"] seconds remaining
        Empty    = effect just expired
        """
        if skill["effect_type"] != "duration":
            return
        if not player.has_active_effect(skill_id):
            return

        remaining = player.active_effects.get(skill_id, 0)
        total     = skill["duration"]
        ratio     = max(0.0, min(1.0, remaining / max(0.01, total)))

        bar_h  = 5
        bar_y  = rect.bottom - bar_h - 2
        bar_x  = rect.x + 2
        bar_w  = rect.w - 4

        # Background
        pygame.draw.rect(screen, (40, 20, 20),
                         (bar_x, bar_y, bar_w, bar_h), border_radius=2)
        # Fill
        fill_w = int(bar_w * ratio)
        if fill_w > 0:
            pygame.draw.rect(screen, COLOR_TIMER_BAR,
                             (bar_x, bar_y, fill_w, bar_h), border_radius=2)

    def _draw_slot_cost(self, screen, rect, skill):
        """Draw endurance cost in the top-right corner of the slot."""
        cost_surf = self.font_cost.render(
            f"{skill['cost_end']} EN", True, (180, 180, 220)
        )
        screen.blit(cost_surf, (rect.right - cost_surf.get_width() - 3, rect.top + 3))

    def _draw_slot_key_label(self, screen, rect, slot_index):
        """Draw the key label (1-5) in the bottom-left corner."""
        label = self.font_key.render(KEY_LABELS[slot_index], True, COLOR_KEY_LABEL)
        screen.blit(label, (rect.left + 4, rect.bottom - label.get_height() - 3))

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    def _build_slot_rects(self):
        """Pre-compute the 5 slot rects, centered horizontally."""
        rects   = []
        start_x = BAR_CENTER_X - BAR_W // 2
        for i in range(SLOT_COUNT):
            x = start_x + i * (SLOT_SIZE + SLOT_GAP)
            rects.append(pygame.Rect(x, SLOT_Y, SLOT_SIZE, SLOT_SIZE))
        return rects

    def _get_skill(self, skill_id):
        if skill_id is None:
            return None
        return next((s for s in ACTIVE_SKILLS if s["id"] == skill_id), None)