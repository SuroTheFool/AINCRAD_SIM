import pygame
import os
from .settings   import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, ASSETS_DIR
from .floor_data import FLOORS
from .boss_data  import BOSS_RAIDS
from .quest_data import get_available_quests, get_quests_for_floor


# --- Overlay dimensions ---
OVERLAY_W = 650
OVERLAY_H = 600
OVERLAY_X = SCREEN_WIDTH  // 2 - OVERLAY_W // 2
OVERLAY_Y = SCREEN_HEIGHT // 2 - OVERLAY_H // 2

# --- Colors ---
COLOR_TAB_ACTIVE    = (60,  60,  100)
COLOR_TAB_INACTIVE  = (30,  30,  50)
COLOR_ROW_BG        = (35,  35,  60)
COLOR_BTN_GO        = (40,  100, 40)
COLOR_BTN_BOSS      = (140, 30,  30)
COLOR_BTN_LOCKED    = (60,  60,  60)
COLOR_BTN_QUEST     = (80,  60,  140)    # purple for quests
COLOR_BTN_DONE      = (50,  50,  50)     # grey for completed quests
COLOR_UNLOCKED      = (100, 220, 100)
COLOR_LOCKED        = (180, 60,  60)
COLOR_QUEST_AVAIL   = (160, 130, 255)    # purple for available quest status
COLOR_QUEST_DONE    = (120, 120, 120)    # grey for completed
COLOR_QUEST_PREREQ  = (200, 160, 60)     # orange — prereq not met


def _load_image(filename, size):
    path = os.path.join(ASSETS_DIR, filename)
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
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
    Three tabs : TRAVEL | BOSS | QUEST

    QUEST tab rules :
      - Only shows quests belonging to the current floor
      - Quests locked by prerequisite show as LOCKED (orange)
      - Completed quests show as DONE (grey, not clickable)
      - Floor 2+ quests are hidden if floor not yet unlocked
    """

    TABS = ["travel", "boss", "quest"]

    def __init__(self, shop_btn_rect):
        self.is_open    = False
        self.active_tab = "travel"

        # --- Fonts ---
        self.font_title = pygame.font.SysFont("Verdana", 24, bold=True)
        self.font_tab   = pygame.font.SysFont("Verdana", 14, bold=True)
        self.font_item  = pygame.font.SysFont("Verdana", 15, bold=True)
        self.font_desc  = pygame.font.SysFont("Verdana", 12)
        self.font_btn   = pygame.font.SysFont("Verdana", 13, bold=True)
        self.font_small = pygame.font.SysFont("Verdana", 11)

        # --- Floor button image ---
        self.floor_btn_img  = _load_image("floor_widget.png", (180, 89))
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

        # --- Tab rects — 3 tabs evenly spaced ---
        tab_y = OVERLAY_Y + 55
        tab_h = 34
        total_tab_w = OVERLAY_W - 40
        tab_w       = total_tab_w // 3 - 6

        self.tab_rects = {
            "travel": pygame.Rect(OVERLAY_X + 10,                    tab_y, tab_w, tab_h),
            "boss"  : pygame.Rect(OVERLAY_X + 10 + tab_w + 8,        tab_y, tab_w, tab_h),
            "quest" : pygame.Rect(OVERLAY_X + 10 + (tab_w + 8) * 2,  tab_y, tab_w, tab_h),
        }

        # --- Close button ---
        self.close_btn_rect = pygame.Rect(
            OVERLAY_X + OVERLAY_W - 40, OVERLAY_Y + 10, 30, 30
        )

        # --- Action button rects (populated during _update_btn_rects) ---
        self.go_btn_rects    = {}   # { floor_index : Rect }
        self.boss_btn_rects  = {}   # { floor_id    : Rect }
        self.quest_btn_rects = {}   # { quest_id    : Rect }
        self._update_btn_rects()

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def handle_click(self, mouse_pos, game):
        # Toggle open/close
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
        for tab_name, rect in self.tab_rects.items():
            if rect.collidepoint(mouse_pos):
                self.active_tab = tab_name
                return None

        # ── TRAVEL ──────────────────────────────────────────────────────
        if self.active_tab == "travel":
            for floor_index, rect in self.go_btn_rects.items():
                if rect.collidepoint(mouse_pos):
                    if floor_index <= game.highest_floor_unlocked:
                        game.go_to_floor(floor_index)
                        self.is_open = False
                    return None

        # ── BOSS ────────────────────────────────────────────────────────
        elif self.active_tab == "boss":
            for floor_id, rect in self.boss_btn_rects.items():
                if rect.collidepoint(mouse_pos):
                    floor_index = next(
                        (i for i, f in enumerate(FLOORS) if f["id"] == floor_id), None
                    )
                    if floor_index is not None and floor_index <= game.highest_floor_unlocked:
                        game.start_boss_raid(floor_id)
                        self.is_open = False
                    return None

        # ── QUEST ───────────────────────────────────────────────────────
        elif self.active_tab == "quest":
            current_floor_id = FLOORS[game.current_floor_index]["id"]
            available_ids    = {
                q["id"] for q in get_available_quests(
                    current_floor_id, game.completed_quests
                )
            }
            for quest_id, rect in self.quest_btn_rects.items():
                if rect.collidepoint(mouse_pos):
                    # Must be available (not done, prereq met)
                    if quest_id in available_ids:
                        game.start_quest(quest_id)
                        self.is_open = False
                    return None

        return None

    # ------------------------------------------------------------------
    # DRAW
    # ------------------------------------------------------------------

    def draw_floor_button(self, screen):
        screen.blit(self.floor_btn_img, self.floor_btn_rect)

    def draw_overlay(self, screen, game):
        if not self.is_open:
            return

        screen.blit(self.overlay_bg, (OVERLAY_X, OVERLAY_Y))

        # Title
        title        = self.font_title.render("FLOOR NAVIGATOR", True, COLOR_WHITE)
        title_shadow = self.font_title.render("FLOOR NAVIGATOR", True, (0, 0, 0))
        title_rect   = title.get_rect(midtop=(OVERLAY_X + OVERLAY_W // 2, OVERLAY_Y + 12))
        screen.blit(title_shadow, (title_rect.x + 2, title_rect.y + 2))
        screen.blit(title, title_rect)

        # Close button X
        pygame.draw.line(screen, COLOR_WHITE,
                         (self.close_btn_rect.left + 5,  self.close_btn_rect.top + 5),
                         (self.close_btn_rect.right - 5, self.close_btn_rect.bottom - 5), 3)
        pygame.draw.line(screen, COLOR_WHITE,
                         (self.close_btn_rect.left + 5,  self.close_btn_rect.bottom - 5),
                         (self.close_btn_rect.right - 5, self.close_btn_rect.top + 5), 3)

        # Tabs
        labels = {"travel": "TRAVEL", "boss": "BOSS", "quest": "QUEST"}
        for tab_name, rect in self.tab_rects.items():
            self._draw_tab(screen, rect, labels[tab_name], self.active_tab == tab_name)

        # Content
        if self.active_tab == "travel":
            self._draw_travel_tab(screen, game)
        elif self.active_tab == "boss":
            self._draw_boss_tab(screen, game)
        elif self.active_tab == "quest":
            self._draw_quest_tab(screen, game)

    # ------------------------------------------------------------------
    # PRIVATE — Tab drawers
    # ------------------------------------------------------------------

    def _draw_tab(self, screen, rect, label, is_active):
        color = COLOR_TAB_ACTIVE if is_active else COLOR_TAB_INACTIVE
        pygame.draw.rect(screen, color, rect, border_radius=8)
        if is_active:
            pygame.draw.rect(screen, COLOR_WHITE, rect, 1, border_radius=8)
        surf = self.font_tab.render(label, True, COLOR_WHITE)
        screen.blit(surf, surf.get_rect(center=rect.center))

    def _draw_travel_tab(self, screen, game):
        row_y = OVERLAY_Y + 104
        for i, floor in enumerate(FLOORS):
            unlocked = i <= game.highest_floor_unlocked
            row_rect = pygame.Rect(OVERLAY_X + 20, row_y, OVERLAY_W - 40, 72)
            pygame.draw.rect(screen, COLOR_ROW_BG, row_rect, border_radius=6)

            status_color = COLOR_UNLOCKED if unlocked else COLOR_LOCKED
            status_text  = "UNLOCKED" if unlocked else "LOCKED"
            screen.blit(
                self.font_desc.render(status_text, True, status_color),
                (OVERLAY_X + 30, row_y + 10)
            )
            screen.blit(
                self.font_item.render(floor["name"], True, COLOR_WHITE),
                (OVERLAY_X + 30, row_y + 32)
            )

            btn_rect  = self.go_btn_rects[i]
            btn_color = COLOR_BTN_GO if unlocked else COLOR_BTN_LOCKED
            pygame.draw.rect(screen, btn_color, btn_rect, border_radius=6)
            lbl = self.font_btn.render("GO" if unlocked else "🔒", True, COLOR_WHITE)
            screen.blit(lbl, lbl.get_rect(center=btn_rect.center))

            row_y += 82

    def _draw_boss_tab(self, screen, game):
        row_y = OVERLAY_Y + 104
        for raid in BOSS_RAIDS:
            floor_index = next(
                (i for i, f in enumerate(FLOORS) if f["id"] == raid["floor_id"]), None
            )
            unlocked = floor_index is not None and floor_index <= game.highest_floor_unlocked
            row_rect = pygame.Rect(OVERLAY_X + 20, row_y, OVERLAY_W - 40, 90)
            pygame.draw.rect(screen, COLOR_ROW_BG, row_rect, border_radius=6)

            screen.blit(
                self.font_item.render(raid["name"], True, COLOR_WHITE),
                (OVERLAY_X + 30, row_y + 10)
            )
            minutes = raid["time_limit"] // 60
            secs    = raid["time_limit"] % 60
            screen.blit(
                self.font_desc.render(
                    f"Time limit : {minutes}:{secs:02d}  —  {len(raid['waves'])} wave(s)",
                    True, (180, 180, 220)
                ),
                (OVERLAY_X + 30, row_y + 36)
            )
            status_color = COLOR_UNLOCKED if unlocked else COLOR_LOCKED
            screen.blit(
                self.font_desc.render("AVAILABLE" if unlocked else "LOCKED", True, status_color),
                (OVERLAY_X + 30, row_y + 60)
            )

            btn_rect  = self.boss_btn_rects[raid["floor_id"]]
            btn_color = COLOR_BTN_BOSS if unlocked else COLOR_BTN_LOCKED
            pygame.draw.rect(screen, btn_color, btn_rect, border_radius=6)
            lbl = self.font_btn.render(
                "CHALLENGE" if unlocked else "LOCKED", True, COLOR_WHITE
            )
            screen.blit(lbl, lbl.get_rect(center=btn_rect.center))

            row_y += 102

    def _draw_quest_tab(self, screen, game):
        """
        Shows all quests for the current floor.

        States per quest :
          DONE      — grey, not clickable
          LOCKED    — orange, prereq not completed
          AVAILABLE — purple, clickable
        """
        current_floor_id = FLOORS[game.current_floor_index]["id"]
        all_quests       = get_quests_for_floor(current_floor_id)
        completed        = game.completed_quests
        available_ids    = {q["id"] for q in get_available_quests(current_floor_id, completed)}

        self.quest_btn_rects = {}   # rebuild each draw

        if not all_quests:
            msg = self.font_desc.render(
                "No quests available on this floor.", True, (160, 160, 180)
            )
            screen.blit(msg, msg.get_rect(
                center=(OVERLAY_X + OVERLAY_W // 2, OVERLAY_Y + OVERLAY_H // 2)
            ))
            return

        row_y   = OVERLAY_Y + 104
        row_h   = 100
        row_gap = 8

        for quest in all_quests:
            qid       = quest["id"]
            is_done   = qid in completed
            is_avail  = qid in available_ids
            # A quest is prereq-locked when it's not done, not available,
            # meaning its unlocked_by quest hasn't been completed yet
            is_prereq = not is_done and not is_avail

            row_rect = pygame.Rect(OVERLAY_X + 20, row_y, OVERLAY_W - 40, row_h)

            # Row background — slightly different shade when done
            bg_color = (25, 25, 40) if is_done else COLOR_ROW_BG
            pygame.draw.rect(screen, bg_color, row_rect, border_radius=8)

            # Left border accent color
            accent = (80, 80, 80) if is_done else \
                     (200, 160, 60) if is_prereq else \
                     (120, 80, 200)
            pygame.draw.rect(screen, accent,
                             pygame.Rect(OVERLAY_X + 20, row_y, 4, row_h),
                             border_radius=3)

            # Quest label
            label_col = (120, 120, 120) if is_done else COLOR_WHITE
            screen.blit(
                self.font_item.render(quest["label"], True, label_col),
                (OVERLAY_X + 34, row_y + 10)
            )

            # Description
            screen.blit(
                self.font_desc.render(quest["description"], True, (160, 160, 200)),
                (OVERLAY_X + 34, row_y + 32)
            )

            # Reward summary
            reward_str = self._reward_summary(quest["reward"])
            screen.blit(
                self.font_small.render(f"Reward : {reward_str}", True, (140, 200, 140)),
                (OVERLAY_X + 34, row_y + 52)
            )

            # Time info
            minutes = quest["time_limit"] // 60
            secs    = quest["time_limit"] % 60
            screen.blit(
                self.font_small.render(
                    f"{len(quest['waves'])} wave(s)  —  {minutes}:{secs:02d}",
                    True, (140, 140, 180)
                ),
                (OVERLAY_X + 34, row_y + 70)
            )

            # Status + button (right side)
            btn_x = OVERLAY_X + OVERLAY_W - 140
            btn_y = row_y + row_h // 2 - 18

            if is_done:
                # No button — just DONE label
                done_surf = self.font_btn.render("✓ DONE", True, COLOR_QUEST_DONE)
                screen.blit(done_surf, done_surf.get_rect(
                    midright=(OVERLAY_X + OVERLAY_W - 24, row_y + row_h // 2)
                ))

            elif is_prereq:
                # Show which quest unlocks this one
                prereq_id   = quest.get("unlocked_by", "")
                prereq_surf = self.font_small.render(
                    f"Complete : {prereq_id}", True, COLOR_QUEST_PREREQ
                )
                screen.blit(prereq_surf, prereq_surf.get_rect(
                    midright=(OVERLAY_X + OVERLAY_W - 24, row_y + row_h // 2)
                ))

            else:
                # START button
                btn_rect = pygame.Rect(btn_x, btn_y, 110, 36)
                self.quest_btn_rects[qid] = btn_rect
                pygame.draw.rect(screen, COLOR_BTN_QUEST, btn_rect, border_radius=6)
                pygame.draw.rect(screen, (160, 130, 255), btn_rect, width=1, border_radius=6)
                lbl = self.font_btn.render("START", True, COLOR_WHITE)
                screen.blit(lbl, lbl.get_rect(center=btn_rect.center))

            row_y += row_h + row_gap

    # ------------------------------------------------------------------
    # PRIVATE — Helpers
    # ------------------------------------------------------------------

    def _reward_summary(self, rewards: list) -> str:
        """Build a short one-line summary of quest rewards."""
        parts = []
        for r in rewards:
            t = r["type"]
            if t == "gold":
                parts.append(f"{r['amount']} stones")
            elif t == "stat":
                parts.append(f"+{r['amount']} {r['stat'][:3].upper()}")
            elif t == "hidden_skill":
                parts.append(f"Hidden skill")
            elif t == "hidden_upgrade":
                parts.append(f"Skill upgrade")
        return "  |  ".join(parts) if parts else "None"

    def _draw_tab(self, screen, rect, label, is_active):
        color = COLOR_TAB_ACTIVE if is_active else COLOR_TAB_INACTIVE
        pygame.draw.rect(screen, color, rect, border_radius=8)
        if is_active:
            pygame.draw.rect(screen, COLOR_WHITE, rect, 1, border_radius=8)
        surf = self.font_tab.render(label, True, COLOR_WHITE)
        screen.blit(surf, surf.get_rect(center=rect.center))

    def _update_btn_rects(self):
        """Pre-compute travel and boss button rects."""
        row_y = OVERLAY_Y + 104
        for i in range(len(FLOORS)):
            self.go_btn_rects[i] = pygame.Rect(
                OVERLAY_X + OVERLAY_W - 130, row_y + 18, 100, 36
            )
            row_y += 82

        row_y = OVERLAY_Y + 104
        for raid in BOSS_RAIDS:
            self.boss_btn_rects[raid["floor_id"]] = pygame.Rect(
                OVERLAY_X + OVERLAY_W - 150, row_y + 22, 120, 40
            )
            row_y += 102
        # Quest btn rects are built dynamically in _draw_quest_tab
        # because the list depends on game state (floor, completed_quests)