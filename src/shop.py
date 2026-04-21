import math
import os
import traceback
import pygame

from .settings import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, ASSETS_DIR
from .shop_data import UPGRADES, STATS_UPGRADES
from .skill_data import PASSIVE_SKILLS, ACTIVE_SKILLS

# --- Overlay dimensions ---
OVERLAY_W = 700
OVERLAY_H = 620
OVERLAY_X = SCREEN_WIDTH  // 2 - OVERLAY_W // 2
OVERLAY_Y = SCREEN_HEIGHT // 2 - OVERLAY_H // 2

# --- Items per page ---
ITEMS_PER_PAGE         = 4
PASSIVE_ITEMS_PER_PAGE = 5
ACTIVE_ITEMS_PER_PAGE  = 3

# --- Tab names ---
TABS       = ["UPGRADES", "SKILLS", "STATS"]
SKILL_TABS = ["PASSIF", "ACTIVE"]

# --- Stat bar max ---
STAT_BAR_MAX = 100

# --- Colors ---
COLOR_BUTTON_BUY   = (220, 220, 220)
COLOR_BUTTON_TEXT  = (20,  20,  20)
COLOR_BUTTON_CANT  = (100, 40,  40)
COLOR_GOLD         = (255, 230, 100)
COLOR_WHITE_SOFT   = (0, 0, 0)
COLOR_TAB_ACTIVE   = (220, 80,  80)
COLOR_TAB_IDLE     = (80,  20,  20)
COLOR_END_BAR      = (80,  180, 255)
COLOR_END_BG       = (30,  30,  80)
COLOR_LOCKED       = (60,  60,  60)
COLOR_LOCK_TEXT    = (160, 100, 100)
COLOR_PASSIVE_TAG  = (80,  140, 220)
COLOR_ACTIVE_TAG   = (220, 140, 40)
COLOR_EQUIPPED     = (60,  180, 80)
COLOR_INT_SCALE    = (120, 180, 255)
COLOR_OWNED        = (60,  180, 80)
FONT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "fonts", "PixelPurl.ttf"
)
# Error log path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(BASE_DIR, "error.log")


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _load_image(filename, size):
    """Load image with magenta fallback + error.log on failure."""
    path = os.path.join(ASSETS_DIR, filename)
    try:
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (int(size[0]), int(size[1])))
        raise FileNotFoundError(f"Asset not found: {path}")
    except Exception:
        try:
            with open(LOG_PATH, "a", encoding="utf-8") as f:
                f.write(f"\n[_load_image] {filename}\n")
                f.write(traceback.format_exc())
        except Exception:
            pass
        surf = pygame.Surface((int(size[0]), int(size[1])), pygame.SRCALPHA)
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
    pygame.draw.rect(mask, (255, 255, 255, 150), mask.get_rect(), width=2, border_radius=radius)
    return mask


def _draw_bar(screen, x, y, w, h, value, max_value, color_fill, color_bg, radius=6):
    pygame.draw.rect(screen, color_bg, (x, y, w, h), border_radius=radius)
    fill_w = int(w * max(0, min(1, value / max(1, max_value))))
    if fill_w > 0:
        pygame.draw.rect(screen, color_fill, (x, y, fill_w, h), border_radius=radius)
    pygame.draw.rect(screen, (255, 255, 255, 80), (x, y, w, h), width=1, border_radius=radius)


def _pill_tag(screen, font, text, color, x, y):
    surf   = font.render(text, True, COLOR_WHITE)
    px, py = 6, 3
    w      = surf.get_width()  + px * 2
    h      = surf.get_height() + py * 2
    bg     = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(bg, (*color, 200), bg.get_rect(), border_radius=4)
    bg.blit(surf, (px, py))
    screen.blit(bg, (x, y))
    return w


def _active_skill_damage_preview(skill, player):
    int_mult = math.sqrt(max(1, player.intelligence))
    base     = player.strength

    if skill["effect_type"] == "instant":
        final = int(base * int_mult * skill.get("dmg_multiplier", 1))
        return (
            f"Damage : {final}  "
            f"= ({player.strength}) × {int_mult:.2f} (√INT {int(player.intelligence)}) "
        )
    elif skill["effect_type"] == "duration":
        if "dmg_bonus_pct" in skill:
            bonus_hit = int(base * int_mult * skill["dmg_bonus_pct"])
            return (
                f"+{int(skill['dmg_bonus_pct']*100)}% dmg  "
                f"(+{bonus_hit}/hit at current INT)  |  {skill['duration']}s"
            )
        elif "crit_multiplier" in skill:
            new_crit = min(100, int(player.crit_chance * skill["crit_multiplier"] * 100))
            return (
                f"Crit : {int(player.crit_chance*100)}%  →  {new_crit}%  |  "
                f"{skill['duration']}s  |  INT scales base dmg"
            )
    return ""


# ===========================================================================
# SHOP CLASS
# ===========================================================================

class Shop:
    def __init__(self):
        self.is_open          = False
        self.active_tab       = "UPGRADES"
        self.active_skill_tab = "PASSIF"
        self.current_page     = 0
        self._total_pages     = math.ceil(len(UPGRADES) / ITEMS_PER_PAGE)

        self.passive_skill_page   = 0
        self._total_passive_pages = math.ceil(len(PASSIVE_SKILLS) / PASSIVE_ITEMS_PER_PAGE)

        self.active_skill_page   = 0
        self._total_active_pages = math.ceil(len(ACTIVE_SKILLS) / ACTIVE_ITEMS_PER_PAGE)

        self.selected_slot = None

        self.levels = {u["id"]: 0 for u in UPGRADES}
        self.levels.update({u["id"]: 0 for u in STATS_UPGRADES})

        self.skill_owned = {s["id"]: 0 for s in ACTIVE_SKILLS}

        # --- Fonts ---
        self.font_title  = pygame.font.SysFont("Verdana", 26, bold=True)
        self.font_tab    = pygame.font.SysFont("Verdana", 15, bold=True)
        self.font_item   = pygame.font.SysFont("Verdana", 17, bold=True)
        self.font_desc   = pygame.font.SysFont("Verdana", 13)
        self.font_btn    = pygame.font.SysFont("Verdana", 13, bold=True)
        self.font_gold   = pygame.font.Font(FONT_PATH, 30)
        self.font_stat   = pygame.font.SysFont("Verdana", 16, bold=True)
        self.font_small  = pygame.font.SysFont("Verdana", 12)
        self.font_tag    = pygame.font.SysFont("Verdana", 10, bold=True)

        self.shop_btn_img  = _load_image("shop_widget.png", (180, 89))
        self.shop_btn_rect = self.shop_btn_img.get_rect(
            bottomright=(SCREEN_WIDTH - 15, SCREEN_HEIGHT - 15)
        )

        self.overlay_bg = _create_gradient_surface(
            OVERLAY_W, OVERLAY_H,
            (210, 80, 80, 240), (140, 20, 20, 250), radius=20
        )

        self.icon_stone    = _load_image("magic_stone.png", (40, 40))
        self.upgrade_icons = {u["id"]: _load_image(u["icon"], (56, 56)) for u in UPGRADES}
        self.stat_icons    = {u["id"]: _load_image(u["icon"], (48, 48)) for u in STATS_UPGRADES}
        self.passive_icons = {s["id"]: _load_image(s["icon"], (44, 44)) for s in PASSIVE_SKILLS}
        self.active_icons  = {s["id"]: _load_image(s["icon"], (56, 56)) for s in ACTIVE_SKILLS}

        self.close_btn_rect = pygame.Rect(
            OVERLAY_X + OVERLAY_W - 40, OVERLAY_Y + 10, 30, 30
        )

        self.buy_btn_rects      = {}
        self.stat_plus_rects    = {}
        self.tab_rects          = {}
        self.skill_tab_rects    = {}
        self.equip_btn_rects    = {}
        self.slot_select_rects  = {}
        self.skill_buy_rects    = {}
        self.passive_prev_rect  = None
        self.passive_next_rect  = None
        self.prev_btn_rect      = None
        self.next_btn_rect      = None
        self.active_prev_rect   = None
        self.active_next_rect   = None

        self._update_tab_rects()
        self._update_btn_rects()

    # -----------------------------------------------------------------------
    # PUBLIC API
    # -----------------------------------------------------------------------

    def get_current_cost(self, upgrade_id):
        u     = self._get_upgrade_any(upgrade_id)
        level = self.levels[upgrade_id]
        return int(u["base_cost"] * (u["cost_growth"] ** level))

    def get_active_skill_cost(self, skill_id):
        skill = self._get_active_skill(skill_id)
        if skill is None:
            return 0
        return skill["base_cost"]

    def handle_click(self, mouse_pos, is_open_click, gold, player, highest_floor=0):
        if is_open_click:
            if self.shop_btn_rect.collidepoint(mouse_pos):
                self.is_open = not self.is_open
                if not self.is_open:
                    self.selected_slot = None
            return gold

        if not self.is_open:
            return gold

        if self.close_btn_rect.collidepoint(mouse_pos):
            self.is_open       = False
            self.selected_slot = None
            return gold

        for tab_name, rect in self.tab_rects.items():
            if rect.collidepoint(mouse_pos):
                if self.active_tab != tab_name:
                    self.active_tab    = tab_name
                    self.current_page  = 0
                    self.selected_slot = None
                    self._update_btn_rects()
                return gold

        # ── UPGRADES ────────────────────────────────────────────────────────
        if self.active_tab == "UPGRADES":
            if self.prev_btn_rect and self.prev_btn_rect.collidepoint(mouse_pos):
                if self.current_page > 0:
                    self.current_page -= 1
                    self._update_btn_rects()
                return gold
            if self.next_btn_rect and self.next_btn_rect.collidepoint(mouse_pos):
                if self.current_page < self._total_pages - 1:
                    self.current_page += 1
                    self._update_btn_rects()
                return gold
            for upgrade_id, rect in self.buy_btn_rects.items():
                if rect.collidepoint(mouse_pos):
                    upgrade = self._get_upgrade_from_list(upgrade_id, UPGRADES)
                    # Bug fix 1 : +1 aligns 0-based index with 1-based min_floor
                    if upgrade is None or (highest_floor + 1) < upgrade.get("min_floor", 0):
                        break
                    cost = self.get_current_cost(upgrade_id)
                    if gold >= cost:
                        gold -= cost
                        self.levels[upgrade_id] += 1
                        self._apply_upgrade(upgrade_id, player, UPGRADES)
                    break

        # ── SKILLS ──────────────────────────────────────────────────────────
        elif self.active_tab == "SKILLS":
            for st_name, rect in self.skill_tab_rects.items():
                if rect.collidepoint(mouse_pos):
                    if self.active_skill_tab != st_name:
                        self.active_skill_tab = st_name
                        self.selected_slot    = None
                    return gold

            if self.active_skill_tab == "PASSIF":
                if self.passive_prev_rect and self.passive_prev_rect.collidepoint(mouse_pos):
                    if self.passive_skill_page > 0:
                        self.passive_skill_page -= 1
                    return gold
                if self.passive_next_rect and self.passive_next_rect.collidepoint(mouse_pos):
                    if self.passive_skill_page < self._total_passive_pages - 1:
                        self.passive_skill_page += 1
                    return gold

            elif self.active_skill_tab == "ACTIVE":
                if self.active_prev_rect and self.active_prev_rect.collidepoint(mouse_pos):
                    if self.active_skill_page > 0:
                        self.active_skill_page -= 1
                    return gold
                if self.active_next_rect and self.active_next_rect.collidepoint(mouse_pos):
                    if self.active_skill_page < self._total_active_pages - 1:
                        self.active_skill_page += 1
                    return gold

                for slot_idx, rect in self.slot_select_rects.items():
                    if rect.collidepoint(mouse_pos):
                        self.selected_slot = slot_idx if self.selected_slot != slot_idx else None
                        return gold

                for skill_id, rect in self.skill_buy_rects.items():
                    if rect.collidepoint(mouse_pos):
                        if self.skill_owned.get(skill_id, 0) == 0:
                            skill = self._get_active_skill(skill_id)
                            if skill is None:
                                break
                            # Bug fix 1 : +1 aligns 0-based index with 1-based min_floor
                            if (highest_floor + 1) < skill.get("min_floor", 0):
                                break
                            cost = self.get_active_skill_cost(skill_id)
                            if gold >= cost:
                                gold -= cost
                                self.skill_owned[skill_id] = 1
                        return gold

                for skill_id, slot_rects in self.equip_btn_rects.items():
                    for si, rect in enumerate(slot_rects):
                        if rect.collidepoint(mouse_pos):
                            if self.skill_owned.get(skill_id, 0) == 0:
                                return gold
                            target = self.selected_slot if self.selected_slot is not None else si
                            player.equip_skill(target, skill_id)
                            self.selected_slot = None
                            return gold

        # ── STATS ───────────────────────────────────────────────────────────
        elif self.active_tab == "STATS":
            for stat_id, rect in self.stat_plus_rects.items():
                if rect.collidepoint(mouse_pos):
                    upgrade = self._get_upgrade_from_list(stat_id, STATS_UPGRADES)
                    # Bug fix 1 : +1 aligns 0-based index with 1-based min_floor
                    if upgrade is None or (highest_floor + 1) < upgrade.get("min_floor", 0):
                        break
                    cost = self.get_current_cost(stat_id)
                    if gold >= cost:
                        gold -= cost
                        self.levels[stat_id] += 1
                        self._apply_upgrade(stat_id, player, STATS_UPGRADES)
                    break

        return gold

    # -----------------------------------------------------------------------
    # DRAW — PUBLIC
    # -----------------------------------------------------------------------

    def draw_shop_button(self, screen, gold):
        icon_x = SCREEN_WIDTH - 270
        icon_y = 7
        screen.blit(self.icon_stone, (icon_x, icon_y))
        gold_surf = self.font_gold.render(f"{int(gold)} Magic Stones", True, COLOR_WHITE_SOFT)
        screen.blit(gold_surf, (icon_x + 50, icon_y + 8))
        screen.blit(self.shop_btn_img, self.shop_btn_rect)

    def draw_overlay(self, screen, gold, player=None, highest_floor=0):
        if not self.is_open:
            return

        screen.blit(self.overlay_bg, (OVERLAY_X, OVERLAY_Y))

        title    = self.font_title.render("AINCRAD SHOP", True, COLOR_WHITE)
        title_sh = self.font_title.render("AINCRAD SHOP", True, (50, 0, 0))
        t_rect   = title.get_rect(midtop=(OVERLAY_X + OVERLAY_W // 2, OVERLAY_Y + 12))
        screen.blit(title_sh, (t_rect.x + 2, t_rect.y + 2))
        screen.blit(title, t_rect)

        pygame.draw.line(screen, COLOR_WHITE,
                         (self.close_btn_rect.left + 5,  self.close_btn_rect.top + 5),
                         (self.close_btn_rect.right - 5, self.close_btn_rect.bottom - 5), 3)
        pygame.draw.line(screen, COLOR_WHITE,
                         (self.close_btn_rect.left + 5,  self.close_btn_rect.bottom - 5),
                         (self.close_btn_rect.right - 5, self.close_btn_rect.top + 5), 3)

        self._draw_main_tabs(screen)

        if self.active_tab == "UPGRADES":
            self._draw_upgrades(screen, gold, highest_floor)
        elif self.active_tab == "SKILLS":
            self._draw_skills(screen, gold, player, highest_floor)
        elif self.active_tab == "STATS":
            self._draw_stats(screen, gold, player, highest_floor)

    # -----------------------------------------------------------------------
    # DRAW — MAIN TABS
    # -----------------------------------------------------------------------

    def _draw_main_tabs(self, screen):
        for tab_name, rect in self.tab_rects.items():
            is_active = (tab_name == self.active_tab)
            color     = COLOR_TAB_ACTIVE if is_active else COLOR_TAB_IDLE
            pygame.draw.rect(screen, color, rect, border_radius=6)
            if is_active:
                pygame.draw.rect(screen, COLOR_WHITE, rect, width=2, border_radius=6)
            label = self.font_tab.render(tab_name, True, COLOR_WHITE)
            screen.blit(label, label.get_rect(center=rect.center))

    def _draw_skill_subtabs(self, screen):
        for st_name, rect in self.skill_tab_rects.items():
            is_active = (st_name == self.active_skill_tab)
            color     = (180, 60, 60) if is_active else (60, 15, 15)
            pygame.draw.rect(screen, color, rect, border_radius=5)
            if is_active:
                pygame.draw.rect(screen, COLOR_WHITE, rect, width=1, border_radius=5)
            label = self.font_tab.render(st_name, True, COLOR_WHITE)
            screen.blit(label, label.get_rect(center=rect.center))

    # -----------------------------------------------------------------------
    # DRAW — UPGRADES TAB
    # -----------------------------------------------------------------------

    def _draw_upgrades(self, screen, gold, highest_floor=0):
        content_y     = OVERLAY_Y + 105
        page_upgrades = self._get_page_upgrades()

        for i, upgrade in enumerate(page_upgrades):
            uid        = upgrade["id"]
            lvl        = self.levels[uid]
            min_floor  = upgrade.get("min_floor", 0)
            # Bug fix 1 : display lock based on same +1 logic
            is_locked  = (highest_floor + 1) < min_floor
            cost       = self.get_current_cost(uid)
            can_afford = gold >= cost and not is_locked

            row_y    = content_y + i * 105
            row_rect = pygame.Rect(OVERLAY_X + 20, row_y, OVERLAY_W - 40, 95)

            bg_alpha = 40 if is_locked else 80
            row_surf = pygame.Surface((row_rect.width, row_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(row_surf, (0, 0, 0, bg_alpha), row_surf.get_rect(), border_radius=8)
            screen.blit(row_surf, row_rect.topleft)

            icon      = self.upgrade_icons[uid]
            icon_rect = icon.get_rect(midleft=(OVERLAY_X + 32, row_y + 48))
            if is_locked:
                dark = pygame.Surface(icon.get_size(), pygame.SRCALPHA)
                dark.fill((0, 0, 0, 160))
                screen.blit(icon, icon_rect)
                screen.blit(dark, icon_rect)
            else:
                screen.blit(icon, icon_rect)

            text_x     = icon_rect.right + 16
            name_color = (140, 100, 100) if is_locked else COLOR_WHITE
            name_surf  = self.font_item.render(f"{upgrade['label']}  (Lv. {lvl})", True, name_color)
            screen.blit(name_surf, (text_x, row_y + 10))

            if is_locked:
                lock_surf = self.font_desc.render(
                    f"Unlocks at Floor {min_floor}", True, COLOR_LOCK_TEXT
                )
                screen.blit(lock_surf, (text_x, row_y + 36))
            else:
                desc_surf = self.font_desc.render(upgrade["description"], True, (200, 200, 200))
                screen.blit(desc_surf, (text_x, row_y + 36))
                screen.blit(pygame.transform.scale(self.icon_stone, (16, 16)), (text_x, row_y + 62))
                cost_surf = self.font_desc.render(f"  {cost}", True, COLOR_GOLD)
                screen.blit(cost_surf, (text_x + 18, row_y + 61))

            btn_rect = self.buy_btn_rects.get(uid)
            if btn_rect:
                if is_locked:
                    pygame.draw.rect(screen, COLOR_LOCKED, btn_rect, border_radius=5)
                    lbl = self.font_btn.render("LOCKED", True, COLOR_LOCK_TEXT)
                else:
                    bg_color  = COLOR_BUTTON_BUY if can_afford else COLOR_BUTTON_CANT
                    txt_color = COLOR_BUTTON_TEXT if can_afford else (150, 100, 100)
                    pygame.draw.rect(screen, bg_color, btn_rect, border_radius=5)
                    lbl = self.font_btn.render("BUY", True, txt_color)
                screen.blit(lbl, lbl.get_rect(center=btn_rect.center))

        self._draw_pagination(screen)

    def _draw_pagination(self, screen):
        btn_y        = OVERLAY_Y + OVERLAY_H - 55
        btn_w, btn_h = 90, 32

        prev_rect          = pygame.Rect(OVERLAY_X + 20, btn_y, btn_w, btn_h)
        self.prev_btn_rect = prev_rect
        can_prev           = self.current_page > 0
        pygame.draw.rect(screen, (180, 50, 50) if can_prev else (60, 20, 20), prev_rect, border_radius=6)
        prev_lbl = self.font_btn.render("<- PREV", True, COLOR_WHITE if can_prev else (100, 60, 60))
        screen.blit(prev_lbl, prev_lbl.get_rect(center=prev_rect.center))

        page_surf = self.font_desc.render(
            f"Page {self.current_page + 1} / {self._total_pages}", True, COLOR_WHITE
        )
        screen.blit(page_surf, page_surf.get_rect(
            center=(OVERLAY_X + OVERLAY_W // 2, btn_y + btn_h // 2)
        ))

        next_rect          = pygame.Rect(OVERLAY_X + OVERLAY_W - 20 - btn_w, btn_y, btn_w, btn_h)
        self.next_btn_rect = next_rect
        can_next           = self.current_page < self._total_pages - 1
        pygame.draw.rect(screen, (180, 50, 50) if can_next else (60, 20, 20), next_rect, border_radius=6)
        next_lbl = self.font_btn.render("NEXT ->", True, COLOR_WHITE if can_next else (100, 60, 60))
        screen.blit(next_lbl, next_lbl.get_rect(center=next_rect.center))

    # -----------------------------------------------------------------------
    # DRAW — SKILLS TAB
    # -----------------------------------------------------------------------

    def _draw_skills(self, screen, gold, player, highest_floor=0):
        self._update_skill_tab_rects()
        self._draw_skill_subtabs(screen)
        content_y = OVERLAY_Y + 140

        if self.active_skill_tab == "PASSIF":
            self._draw_passif(screen, content_y, player)
        else:
            self._draw_actif(screen, content_y, gold, player, highest_floor)

    # ── PASSIF ──────────────────────────────────────────────────────────────

    def _draw_passif(self, screen, content_y, player):
        row_h   = 66
        padding = 5

        for i, skill in enumerate(self._get_passive_page_skills()):
            sid   = skill["id"]
            row_y = content_y + i * (row_h + padding)

            row_rect = pygame.Rect(OVERLAY_X + 15, row_y, OVERLAY_W - 30, row_h)
            row_surf = pygame.Surface((row_rect.width, row_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(row_surf, (0, 0, 0, 70), row_surf.get_rect(), border_radius=8)
            screen.blit(row_surf, row_rect.topleft)

            icon = self.passive_icons.get(sid)
            if icon:
                icon_rect = icon.get_rect(midleft=(OVERLAY_X + 22, row_y + row_h // 2))
                screen.blit(icon, icon_rect)
                text_x = icon_rect.right + 12
            else:
                text_x = OVERLAY_X + 22

            lvl       = self.levels.get(sid, 0)
            name_surf = self.font_item.render(f"{skill['label']}  Lv. {lvl}", True, COLOR_WHITE)
            screen.blit(name_surf, (text_x, row_y + 6))

            _pill_tag(screen, self.font_tag, "PASSIVE", COLOR_PASSIVE_TAG, text_x, row_y + 28)

            desc_surf = self.font_small.render(skill["description"], True, (180, 180, 180))
            screen.blit(desc_surf, (text_x, row_y + 46))

            if player:
                stat_val = getattr(player, sid, None)
                if stat_val is not None:
                    fmt = (
                        f"{stat_val:.2f}"
                        if isinstance(stat_val, float) and stat_val != int(stat_val)
                        else str(int(stat_val))
                    )
                    val_surf = self.font_stat.render(fmt, True, COLOR_GOLD)
                    screen.blit(val_surf, val_surf.get_rect(
                        midright=(OVERLAY_X + OVERLAY_W - 18, row_y + row_h // 2)
                    ))

        self._draw_passive_pagination(screen)

    def _draw_passive_pagination(self, screen):
        if self._total_passive_pages <= 1:
            return
        btn_y        = OVERLAY_Y + OVERLAY_H - 50
        btn_w, btn_h = 80, 28

        prev_rect              = pygame.Rect(OVERLAY_X + 20, btn_y, btn_w, btn_h)
        self.passive_prev_rect = prev_rect
        can_prev               = self.passive_skill_page > 0
        pygame.draw.rect(screen, (180, 50, 50) if can_prev else (60, 20, 20), prev_rect, border_radius=5)
        lbl = self.font_btn.render("◄ PREV", True, COLOR_WHITE if can_prev else (100, 60, 60))
        screen.blit(lbl, lbl.get_rect(center=prev_rect.center))

        page_surf = self.font_small.render(
            f"{self.passive_skill_page + 1} / {self._total_passive_pages}", True, COLOR_WHITE
        )
        screen.blit(page_surf, page_surf.get_rect(
            center=(OVERLAY_X + OVERLAY_W // 2, btn_y + btn_h // 2)
        ))

        next_rect              = pygame.Rect(OVERLAY_X + OVERLAY_W - 20 - btn_w, btn_y, btn_w, btn_h)
        self.passive_next_rect = next_rect
        can_next               = self.passive_skill_page < self._total_passive_pages - 1
        pygame.draw.rect(screen, (180, 50, 50) if can_next else (60, 20, 20), next_rect, border_radius=5)
        lbl = self.font_btn.render("NEXT ►", True, COLOR_WHITE if can_next else (100, 60, 60))
        screen.blit(lbl, lbl.get_rect(center=next_rect.center))

    # ── ACTIF ───────────────────────────────────────────────────────────────

    def _draw_actif(self, screen, content_y, gold, player, highest_floor=0):
        if player is None:
            return

        self.equip_btn_rects   = {}
        self.slot_select_rects = {}
        self.skill_buy_rects   = {}

        self._draw_endurance_bar_actif(screen, content_y, player)
        y = content_y + 46
        y = self._draw_slot_selector(screen, y, player)

        pygame.draw.line(screen, (200, 80, 80),
                         (OVERLAY_X + 20, y), (OVERLAY_X + OVERLAY_W - 20, y), 1)
        y += 8

        row_h = 118
        for skill in self._get_active_page_skills():
            sid       = skill["id"]
            owned     = self.skill_owned.get(sid, 0) == 1
            min_floor = skill.get("min_floor", 0)
            # Bug fix 1 : +1 aligns 0-based index with 1-based min_floor
            is_locked = (highest_floor + 1) < min_floor
            cost      = self.get_active_skill_cost(sid)
            can_buy   = not owned and not is_locked and gold >= cost

            row_rect = pygame.Rect(OVERLAY_X + 15, y, OVERLAY_W - 30, row_h)
            row_surf = pygame.Surface((row_rect.width, row_rect.height), pygame.SRCALPHA)
            bg_alpha = 90 if owned else 50
            pygame.draw.rect(row_surf, (0, 0, 0, bg_alpha), row_surf.get_rect(), border_radius=10)
            screen.blit(row_surf, row_rect.topleft)

            if owned:
                pygame.draw.rect(screen, (50, 150, 70), row_rect, width=1, border_radius=10)

            icon = self.active_icons.get(sid)
            if icon:
                icon_rect = icon.get_rect(midleft=(OVERLAY_X + 22, y + row_h // 2))
                if not owned:
                    dark = pygame.Surface(icon.get_size(), pygame.SRCALPHA)
                    dark.fill((0, 0, 0, 130))
                    screen.blit(icon, icon_rect)
                    screen.blit(dark, icon_rect)
                else:
                    screen.blit(icon, icon_rect)
                text_x = icon_rect.right + 14
            else:
                text_x = OVERLAY_X + 22

            name_col  = COLOR_WHITE if owned else (150, 120, 120)
            name_surf = self.font_item.render(skill["label"], True, name_col)
            screen.blit(name_surf, (text_x, y + 6))

            tag_x = text_x + name_surf.get_width() + 8
            _pill_tag(screen, self.font_tag, "ACTIVE", COLOR_ACTIVE_TAG, tag_x, y + 9)
            if owned:
                tag_x += 52
                _pill_tag(screen, self.font_tag, "OWNED", COLOR_OWNED, tag_x, y + 9)

            screen.blit(
                self.font_small.render(skill["description"], True,
                                       (200, 200, 200) if owned else (140, 120, 120)),
                (text_x, y + 28)
            )
            screen.blit(
                self.font_small.render(f"Cost : {skill['cost_end']} EN", True, COLOR_END_BAR),
                (text_x, y + 44)
            )

            if owned:
                scale_txt = _active_skill_damage_preview(skill, player)
                screen.blit(
                    self.font_small.render(scale_txt, True, COLOR_INT_SCALE),
                    (text_x, y + 60)
                )

            right_x = OVERLAY_X + OVERLAY_W - 120

            if not owned:
                btn_rect = pygame.Rect(right_x, y + 38, 100, 38)
                self.skill_buy_rects[sid] = btn_rect

                if is_locked:
                    pygame.draw.rect(screen, COLOR_LOCKED, btn_rect, border_radius=6)
                    lbl = self.font_btn.render("LOCKED", True, COLOR_LOCK_TEXT)
                    screen.blit(lbl, lbl.get_rect(center=btn_rect.center))
                    # Show which floor unlocks it
                    unlock_surf = self.font_small.render(
                        f"Floor {min_floor}", True, COLOR_LOCK_TEXT
                    )
                    screen.blit(unlock_surf, unlock_surf.get_rect(
                        center=(btn_rect.centerx, btn_rect.bottom + 10)
                    ))
                elif can_buy:
                    pygame.draw.rect(screen, COLOR_BUTTON_BUY, btn_rect, border_radius=6)
                    lbl = self.font_btn.render("BUY", True, COLOR_BUTTON_TEXT)
                    screen.blit(lbl, lbl.get_rect(center=btn_rect.center))
                else:
                    pygame.draw.rect(screen, COLOR_BUTTON_CANT, btn_rect, border_radius=6)
                    lbl = self.font_btn.render("BUY", True, (150, 100, 100))
                    screen.blit(lbl, lbl.get_rect(center=btn_rect.center))

                screen.blit(pygame.transform.scale(self.icon_stone, (14, 14)),
                            (right_x, y + 82))
                cost_surf = self.font_small.render(f"  {cost}", True, COLOR_GOLD)
                screen.blit(cost_surf, (right_x + 16, y + 82))
            else:
                self._draw_equip_buttons(screen, sid, y + row_h - 26, player)

            y += row_h + 6

        self._draw_active_pagination(screen)

    def _draw_endurance_bar_actif(self, screen, content_y, player):
        max_end = player.endurance * 10
        cur_end = player.current_end
        bar_x   = OVERLAY_X + 40
        bar_y   = content_y + 16
        bar_w   = OVERLAY_W - 80
        bar_h   = 16
        lbl     = self.font_small.render(
            f"ENDURANCE  {int(cur_end)} / {int(max_end)}", True, COLOR_WHITE
        )
        screen.blit(lbl, (bar_x, bar_y - 14))
        _draw_bar(screen, bar_x, bar_y, bar_w, bar_h,
                  cur_end, max_end, COLOR_END_BAR, COLOR_END_BG, radius=6)

    def _draw_slot_selector(self, screen, y, player):
        hint = self.font_small.render(
            "Select a slot, then click a number below to equip  ↓", True, (180, 180, 180)
        )
        screen.blit(hint, (OVERLAY_X + 20, y))
        y += 16

        slot_w  = 90
        slot_h  = 26
        gap     = 5
        total_w = 5 * slot_w + 4 * gap
        start_x = OVERLAY_X + OVERLAY_W // 2 - total_w // 2

        self.slot_select_rects = {}
        for si in range(5):
            sx        = start_x + si * (slot_w + gap)
            slot_rect = pygame.Rect(sx, y, slot_w, slot_h)
            self.slot_select_rects[si] = slot_rect

            selected = (self.selected_slot == si)
            skill_id = player.skill_slots[si]
            bg_col   = (180, 140,  0) if selected else \
                       ( 40, 120, 60) if skill_id else (40, 20, 20)
            brd_col  = (255, 210,  0) if selected else \
                       ( 80, 180,100) if skill_id else (100, 50, 50)

            pygame.draw.rect(screen, bg_col,  slot_rect, border_radius=5)
            pygame.draw.rect(screen, brd_col, slot_rect, width=1, border_radius=5)

            if skill_id:
                sk    = next((s for s in ACTIVE_SKILLS if s["id"] == skill_id), None)
                label = (sk["label"][:7] + "…") if sk and len(sk["label"]) > 7 else \
                        (sk["label"] if sk else "?")
            else:
                label = "empty"

            lbl_surf = self.font_small.render(f"{si+1}: {label}", True, COLOR_WHITE)
            screen.blit(lbl_surf, lbl_surf.get_rect(center=slot_rect.center))

        return y + slot_h + 8

    def _draw_equip_buttons(self, screen, skill_id, y, player):
        btn_w   = 32
        btn_h   = 20
        btn_gap = 4
        total_w = 5 * btn_w + 4 * btn_gap
        start_x = OVERLAY_X + OVERLAY_W - total_w - 18

        slot_btns = []
        for si in range(5):
            bx       = start_x + si * (btn_w + btn_gap)
            btn_rect = pygame.Rect(bx, y, btn_w, btn_h)
            slot_btns.append(btn_rect)

            equipped = (player.skill_slots[si] == skill_id)
            selected = (self.selected_slot == si)
            bg_col   = ( 40, 160, 70) if equipped else \
                       (180, 140,  0) if selected else (60, 20, 20)
            brd_col  = ( 80, 220,100) if equipped else \
                       (255, 210,  0) if selected else (100, 60, 60)

            pygame.draw.rect(screen, bg_col,  btn_rect, border_radius=3)
            pygame.draw.rect(screen, brd_col, btn_rect, width=1, border_radius=3)

            lbl = self.font_small.render(str(si + 1), True, COLOR_WHITE)
            screen.blit(lbl, lbl.get_rect(center=btn_rect.center))

        self.equip_btn_rects[skill_id] = slot_btns

    def _draw_active_pagination(self, screen):
        if self._total_active_pages <= 1:
            return
        btn_y        = OVERLAY_Y + OVERLAY_H - 48
        btn_w, btn_h = 80, 26

        prev_rect             = pygame.Rect(OVERLAY_X + 20, btn_y, btn_w, btn_h)
        self.active_prev_rect = prev_rect
        can_prev              = self.active_skill_page > 0
        pygame.draw.rect(screen, (180, 50, 50) if can_prev else (60, 20, 20),
                         prev_rect, border_radius=5)
        lbl = self.font_btn.render("◄ PREV", True, COLOR_WHITE if can_prev else (100, 60, 60))
        screen.blit(lbl, lbl.get_rect(center=prev_rect.center))

        page_surf = self.font_small.render(
            f"{self.active_skill_page + 1} / {self._total_active_pages}", True, COLOR_WHITE
        )
        screen.blit(page_surf, page_surf.get_rect(
            center=(OVERLAY_X + OVERLAY_W // 2, btn_y + btn_h // 2)
        ))

        next_rect             = pygame.Rect(OVERLAY_X + OVERLAY_W - 20 - btn_w, btn_y, btn_w, btn_h)
        self.active_next_rect = next_rect
        can_next              = self.active_skill_page < self._total_active_pages - 1
        pygame.draw.rect(screen, (180, 50, 50) if can_next else (60, 20, 20),
                         next_rect, border_radius=5)
        lbl = self.font_btn.render("NEXT ►", True, COLOR_WHITE if can_next else (100, 60, 60))
        screen.blit(lbl, lbl.get_rect(center=next_rect.center))

    # -----------------------------------------------------------------------
    # DRAW — STATS TAB
    # -----------------------------------------------------------------------

    def _draw_stats(self, screen, gold, player, highest_floor=0):
        if player is None:
            return

        self.stat_plus_rects = {}
        content_y = OVERLAY_Y + 105
        spacing   = 110
        bar_x     = OVERLAY_X + 110
        bar_w     = OVERLAY_W - 250

        stat_defs = [
            ("strength",     player.strength,     (220, 80,  80)),
            ("intelligence", player.intelligence, (80,  120, 220)),
            ("endurance",    player.endurance,    (80,  200, 120)),
        ]

        for i, (stat_id, value, bar_color) in enumerate(stat_defs):
            upgrade = self._get_upgrade_from_list(stat_id, STATS_UPGRADES)
            if upgrade is None:
                continue

            min_floor  = upgrade.get("min_floor", 0)
            # Bug fix 1 : consistent +1
            is_locked  = (highest_floor + 1) < min_floor
            cost       = self.get_current_cost(stat_id)
            can_afford = gold >= cost and not is_locked

            row_y    = content_y + i * spacing
            row_rect = pygame.Rect(OVERLAY_X + 15, row_y, OVERLAY_W - 30, 100)
            row_surf = pygame.Surface((row_rect.width, row_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(row_surf, (0, 0, 0, 70), row_surf.get_rect(), border_radius=10)
            screen.blit(row_surf, row_rect.topleft)

            icon      = self.stat_icons[stat_id]
            icon_rect = icon.get_rect(midleft=(OVERLAY_X + 28, row_y + 50))
            screen.blit(icon, icon_rect)

            label_surf = self.font_item.render(
                f"{upgrade['label']}   Lv. {int(value)}", True, COLOR_WHITE
            )
            screen.blit(label_surf, (bar_x, row_y + 8))

            desc_surf = self.font_small.render(upgrade["description"], True, (180, 180, 180))
            screen.blit(desc_surf, (bar_x, row_y + 32))

            bar_h = 14
            bar_y = row_y + 54
            _draw_bar(screen, bar_x, bar_y, bar_w, bar_h,
                      value, STAT_BAR_MAX, bar_color, (25, 25, 25), radius=5)

            pct   = int(value / STAT_BAR_MAX * 100)
            pct_s = self.font_small.render(f"{pct}%", True, (200, 200, 200))
            screen.blit(pct_s, (bar_x + bar_w + 6, bar_y))

            if not is_locked:
                screen.blit(pygame.transform.scale(self.icon_stone, (14, 14)),
                            (bar_x, row_y + 76))
                cost_surf = self.font_small.render(f"  {cost}", True, COLOR_GOLD)
                screen.blit(cost_surf, (bar_x + 16, row_y + 76))

            plus_x    = OVERLAY_X + OVERLAY_W - 75
            plus_rect = pygame.Rect(plus_x, row_y + 30, 48, 40)
            self.stat_plus_rects[stat_id] = plus_rect

            if is_locked:
                pygame.draw.rect(screen, COLOR_LOCKED, plus_rect, border_radius=8)
                lbl = self.font_btn.render("LOCK", True, COLOR_LOCK_TEXT)
            elif can_afford:
                pygame.draw.rect(screen, COLOR_EQUIPPED, plus_rect, border_radius=8)
                pygame.draw.rect(screen, COLOR_WHITE, plus_rect, width=2, border_radius=8)
                lbl = self.font_title.render("+", True, COLOR_WHITE)
            else:
                pygame.draw.rect(screen, COLOR_BUTTON_CANT, plus_rect, border_radius=8)
                lbl = self.font_title.render("+", True, (150, 80, 80))

            screen.blit(lbl, lbl.get_rect(center=plus_rect.center))

        sep_y = content_y + len(stat_defs) * spacing + 10
        pygame.draw.line(screen, (255, 255, 255, 60),
                         (OVERLAY_X + 30, sep_y), (OVERLAY_X + OVERLAY_W - 30, sep_y), 1)

        derived = [
            ("Click Damage",    f"{int(player.click_damage + player.strength)} base"),
            ("DMG Multiplier",  f"x{math.sqrt(max(1, player.intelligence)):.2f}  (√INT)"),
            ("Endurance Max",   f"{int(player.endurance * 10)} pts"),
            ("Crit Chance",     f"{int(player.crit_chance * 100)} %"),
            ("Crit Multiplier", f"x{player.crit_multiplier:.1f}"),
            ("Auto DPS",        f"{player.auto_dps} dmg/s"),
            ("Gold Multiplier", f"x{player.gold_multiplier:.1f}"),
        ]

        col_x = [OVERLAY_X + 40, OVERLAY_X + OVERLAY_W // 2]
        row_y = sep_y + 10
        for j, (d_label, d_val) in enumerate(derived):
            x   = col_x[j % 2]
            y   = row_y + (j // 2) * 34
            lbl = self.font_small.render(d_label, True, (150, 150, 150))
            val = self.font_stat.render(d_val,    True, COLOR_GOLD)
            screen.blit(lbl, (x, y))
            screen.blit(val, (x, y + 15))

    # -----------------------------------------------------------------------
    # PRIVATE HELPERS
    # -----------------------------------------------------------------------

    def _get_page_upgrades(self):
        start = self.current_page * ITEMS_PER_PAGE
        return UPGRADES[start: start + ITEMS_PER_PAGE]

    def _get_passive_page_skills(self):
        start = self.passive_skill_page * PASSIVE_ITEMS_PER_PAGE
        return PASSIVE_SKILLS[start: start + PASSIVE_ITEMS_PER_PAGE]

    def _get_active_page_skills(self):
        start = self.active_skill_page * ACTIVE_ITEMS_PER_PAGE
        return ACTIVE_SKILLS[start: start + ACTIVE_ITEMS_PER_PAGE]

    def _get_upgrade_from_list(self, upgrade_id, upgrade_list):
        return next((u for u in upgrade_list if u["id"] == upgrade_id), None)

    def _get_upgrade_any(self, upgrade_id):
        result = self._get_upgrade_from_list(upgrade_id, UPGRADES)
        if result is None:
            result = self._get_upgrade_from_list(upgrade_id, STATS_UPGRADES)
        return result

    def _get_active_skill(self, skill_id):
        return next((s for s in ACTIVE_SKILLS if s["id"] == skill_id), None)

    def _apply_upgrade(self, upgrade_id, player, upgrade_list):
        u = self._get_upgrade_from_list(upgrade_id, upgrade_list)
        if u is None:
            return
        current = getattr(player, u["effect"])
        setattr(player, u["effect"], current + u["effect_value"])

    def _update_tab_rects(self):
        tab_w   = 140
        tab_h   = 34
        tab_y   = OVERLAY_Y + 55
        total_w = len(TABS) * tab_w + (len(TABS) - 1) * 8
        start_x = OVERLAY_X + OVERLAY_W // 2 - total_w // 2
        self.tab_rects = {}
        for i, name in enumerate(TABS):
            x = start_x + i * (tab_w + 8)
            self.tab_rects[name] = pygame.Rect(x, tab_y, tab_w, tab_h)

    def _update_skill_tab_rects(self):
        stab_w  = 110
        stab_h  = 28
        stab_y  = OVERLAY_Y + 103
        total_w = len(SKILL_TABS) * stab_w + (len(SKILL_TABS) - 1) * 6
        start_x = OVERLAY_X + OVERLAY_W // 2 - total_w // 2
        self.skill_tab_rects = {}
        for i, name in enumerate(SKILL_TABS):
            x = start_x + i * (stab_w + 6)
            self.skill_tab_rects[name] = pygame.Rect(x, stab_y, stab_w, stab_h)

    def _update_btn_rects(self):
        self.buy_btn_rects = {}
        content_y     = OVERLAY_Y + 105
        page_upgrades = self._get_page_upgrades()
        for i, upgrade in enumerate(page_upgrades):
            row_y = content_y + i * 105
            rect  = pygame.Rect(OVERLAY_X + OVERLAY_W - 125, row_y + 28, 88, 38)
            self.buy_btn_rects[upgrade["id"]] = rect