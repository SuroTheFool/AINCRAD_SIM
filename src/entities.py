import math
import pygame
import os
from .settings import (SCREEN_WIDTH, SCREEN_HEIGHT, ASSETS_DIR,
                        COLOR_ACCENT, COLOR_WHITE)
import random


# ===========================================================================
# PLAYER
# ===========================================================================

class Player:
    """Player class — animated via sprite sheet, supports active skill slots."""

    def __init__(self, skin_data, floor_id=1):
        self.click_damage    = 1
        self.crit_chance     = 0.02
        self.crit_multiplier = 2.0
        self.auto_dps        = 0
        self.gold_multiplier = 1.0

        self.strength     = 0
        self.intelligence = 0
        self.endurance    = 1
        self.current_end  = 10.0

        self.skill_slots    = [None, None, None, None, None]
        self.active_effects = {}

        self.skin_data = skin_data
        sheet_path     = os.path.join(ASSETS_DIR, skin_data["image_file"])
        self.sheet     = pygame.image.load(sheet_path).convert_alpha()

        fw           = skin_data["frame_w"]
        fh           = skin_data["frame_h"]
        display_size = skin_data["display_size"]

        self.animations = {}
        for anim_name, anim_data in skin_data["animations"].items():
            frames = []
            for i in range(anim_data["frame_count"]):
                raw    = self.sheet.subsurface((i * fw, anim_data["row"] * fh, fw, fh))
                scaled = pygame.transform.scale(raw, display_size)
                frames.append(scaled)
            self.animations[anim_name] = frames

        self.current_anim = "idle"
        self.frames       = self.animations["idle"]
        self.frame_index  = 0.0
        self.frame_speed  = skin_data["frame_speed"]
        self.image        = self.frames[0]

        self._apply_position(floor_id)

        self.font_dmg       = pygame.font.SysFont("Arial", 28, bold=True)
        self.floating_texts = []

    def update(self, dt=0):
        self.frame_index = (self.frame_index + self.frame_speed) % len(self.frames)
        self.image       = self.frames[int(self.frame_index)]
        midbottom        = self.rect.midbottom
        self.rect        = self.image.get_rect(midbottom=midbottom)

        max_end          = self.endurance * 10
        regen            = (dt * 3.0) if dt > 0 else 0.05
        self.current_end = min(max_end, self.current_end + regen)

        if dt > 0:
            expired = [sid for sid, t in self.active_effects.items() if t - dt <= 0]
            for sid in expired:
                del self.active_effects[sid]
            for sid in self.active_effects:
                self.active_effects[sid] -= dt

    def set_animation(self, name):
        if name == self.current_anim or name not in self.animations:
            return
        self.current_anim = name
        self.frames       = self.animations[name]
        self.frame_index  = 0.0

    def _apply_position(self, floor_id):
        self.current_floor_id = floor_id
        positions = self.skin_data["positions"]
        pos       = positions.get(floor_id, positions["default"])
        self.rect = self.image.get_rect(
            midbottom=(SCREEN_WIDTH * pos[0], SCREEN_HEIGHT * pos[1])
        )

    def change_floor(self, floor_id):
        self._apply_position(floor_id)

    def change_skin(self, skin_data):
        self.__init__(skin_data, self.current_floor_id)

    def calculate_damage(self):
        from .skill_data import ACTIVE_SKILLS

        eff_crit = self.crit_chance
        if "shadow_step" in self.active_effects:
            skill    = next((s for s in ACTIVE_SKILLS if s["id"] == "shadow_step"), None)
            eff_crit = min(1.0, self.crit_chance * skill["crit_multiplier"]) if skill else eff_crit

        is_crit = random.random() < eff_crit
        base    = self.click_damage + self.strength
        damage  = base * (self.crit_multiplier if is_crit else 1.0)

        if "battle_aura" in self.active_effects:
            skill   = next((s for s in ACTIVE_SKILLS if s["id"] == "battle_aura"), None)
            damage *= (1.0 + skill["dmg_bonus_pct"]) if skill else 1.0

        return int(damage), is_crit
    
    def equip_skill(self, slot_index, skill_id):
        if 0 <= slot_index < 5:
            self.skill_slots[slot_index] = skill_id

    def use_skill(self, slot_index, monster=None):
        from .skill_data import ACTIVE_SKILLS

        if not (0 <= slot_index < 5):
            return None, None

        skill_id = self.skill_slots[slot_index]
        if skill_id is None:
            return None, None

        skill = next((s for s in ACTIVE_SKILLS if s["id"] == skill_id), None)
        if skill is None:
            return None, None

        if self.current_end < skill["cost_end"]:
            return None, None

        self.current_end -= skill["cost_end"]

        if skill["effect_type"] == "instant":
            damage = int(
                (self.click_damage + self.strength)
                * math.sqrt(max(1, self.intelligence))
                * skill.get("dmg_multiplier", 1)
            )
            return damage, skill_id

        if skill["effect_type"] == "duration":
            self.active_effects[skill_id] = skill["duration"]
            return None, skill_id

        return None, None

    def has_active_effect(self, skill_id):
        return skill_id in self.active_effects

    def max_endurance(self):
        return self.endurance * 10

    def use_endurance(self, cost):
        if self.current_end >= cost:
            self.current_end -= cost
            return True
        return False

    def spawn_floating_text(self, damage, is_crit, position):
        color = (255, 215, 0) if is_crit else (255, 80, 80)
        label = f"CRIT! -{int(damage)}" if is_crit else f"-{int(damage)}"
        surf  = self.font_dmg.render(label, True, color)
        self.floating_texts.append([surf, position[0], position[1], 45])

    def update_floating_texts(self):
        for entry in self.floating_texts:
            entry[2] -= 1.5
            entry[3] -= 1
        self.floating_texts = [e for e in self.floating_texts if e[3] > 0]

    def draw_floating_texts(self, screen):
        for entry in self.floating_texts:
            surf, x, y, _ = entry
            screen.blit(surf, surf.get_rect(center=(x, y)))

    def draw(self, screen):
        screen.blit(self.image, self.rect)


# ===========================================================================
# MONSTER
# ===========================================================================

class Monster:
    """Clickable enemy — static or animated sprite sheet."""

    def __init__(self, name, hp, image_file, display_size=(220, 220),
                 pos=(0.72, 0.72), bonus=0, apply_random_offset=True,
                 frame_w=None, frame_h=None, frame_speed=0.12,
                 animations=None):

        self.name         = name
        self.max_hp       = hp
        self.current_hp   = hp
        self.display_size = (int(display_size[0]), int(display_size[1]))
        self.bonus        = bonus

        random_offset = random.uniform(-0.03, 0.03) if apply_random_offset else 0
        self._pos_x   = SCREEN_WIDTH  * (pos[0] + random_offset)
        self._pos_y   = SCREEN_HEIGHT * pos[1]

        self._animated   = (frame_w is not None and animations is not None)
        self.frame_speed = frame_speed
        self.frame_index = 0.0

        raw_sheet = pygame.image.load(
            os.path.join(ASSETS_DIR, image_file)
        ).convert_alpha()

        if self._animated:
            self.animations   = {}
            self.current_anim = "idle"
            for anim_name, anim_data in animations.items():
                frames = []
                row    = anim_data["row"]
                count  = anim_data["frame_count"]
                for i in range(count):
                    raw    = raw_sheet.subsurface(
                        (i * frame_w, row * frame_h, frame_w, frame_h)
                    )
                    scaled = pygame.transform.scale(raw, self.display_size)
                    frames.append(scaled)
                self.animations[anim_name] = frames
            self.frames = self.animations["idle"]
            self.image  = self.frames[0]
        else:
            self.animations   = {}
            self.current_anim = "idle"
            self.frames       = [pygame.transform.scale(raw_sheet, self.display_size)]
            self.image        = self.frames[0]

        self.rect = self.image.get_rect(midbottom=(self._pos_x, self._pos_y))
        self.font = pygame.font.SysFont("Arial", 22, bold=True)
        self.mask = pygame.mask.from_surface(self.image)

    def _set_animation(self, name):
        if name == self.current_anim or name not in self.animations:
            return
        self.current_anim = name
        self.frames       = self.animations[name]
        self.frame_index  = 0.0

    def update(self, dt):
        if not self._animated:
            return
        self.frame_index = (self.frame_index + self.frame_speed) % len(self.frames)
        self.image = self.frames[min(int(self.frame_index), len(self.frames) - 1)]

    def is_alive(self):
        return self.current_hp > 0

    def take_damage(self, damage):
        self.current_hp = max(0, self.current_hp - damage)

    def is_clicked(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            rel_x = mouse_pos[0] - self.rect.x
            rel_y = mouse_pos[1] - self.rect.y
            try:
                return self.mask.get_at((rel_x, rel_y))
            except IndexError:
                return True
        return False

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        self._draw_hp_bar(screen)

    def _draw_hp_bar(self, screen):
        bar_width  = 220
        bar_height = 18
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top - 40

        pygame.draw.rect(screen, (100, 0, 0),
                         (bar_x, bar_y, bar_width, bar_height), border_radius=4)
        fill_width = int(bar_width * self.current_hp / self.max_hp)
        if fill_width > 0:
            pygame.draw.rect(screen, COLOR_ACCENT,
                             (bar_x, bar_y, fill_width, bar_height), border_radius=4)

        name_surf = self.font.render(
            f"{self.name}  {self.current_hp}/{self.max_hp} HP", True, COLOR_WHITE
        )
        screen.blit(name_surf, name_surf.get_rect(midbottom=(self.rect.centerx, bar_y - 4)))


# ===========================================================================
# MOB  (Monster + dialog)
# ===========================================================================

class Mob(Monster):
    """
    Monster with dialog bubbles triggered at HP thresholds.

    dialog format in data :
        {
            0.75: "I'm still here",
            0.50: "You're going to regret",
            0.25: None,          # None = Don't talk
        }
    Keys are HP ratio floats (0.0 → 1.0), checked after each hit.
    Each threshold fires at most once per fight.
    """

    # Bubble style
    BUBBLE_DURATION  = 4.0        # seconds the bubble stays visible
    BUBBLE_PADDING   = (12, 8)    # horizontal, vertical
    BUBBLE_COLOR     = (245, 245, 240)
    BUBBLE_BORDER    = (60, 60, 60)
    BUBBLE_TEXT_COL  = (15, 15, 15)
    BUBBLE_RADIUS    = 8

    def __init__(self, name, hp, image_file, display_size=(220, 220),
                 pos=(0.72, 0.72), bonus=0, apply_random_offset=True,
                 frame_w=None, frame_h=None, frame_speed=0.12,
                 animations=None,
                 dialog=None):
        # Monster handles ALL loading — no duplication
        super().__init__(
            name, hp, image_file, display_size, pos, bonus,
            apply_random_offset, frame_w, frame_h, frame_speed, animations
        )

        # dialog = {hp_ratio: text_or_None, ...}
        self.dialog          = dialog or {}
        self._said_at        = set()     # ratios already triggered
        self._current_dialog = None      # text currently shown (None = hidden)
        self._dialog_timer   = 0.0      # seconds remaining

        self._font_bubble = pygame.font.SysFont("Arial", 14)

    # ------------------------------------------------------------------
    # COMBAT — override to check dialog thresholds
    # ------------------------------------------------------------------

    def take_damage(self, damage):
        super().take_damage(damage)
        self._check_dialog_thresholds()

    def _check_dialog_thresholds(self):
        """Fire dialog for the lowest unpassed threshold that was just crossed."""
        if not self.dialog or self.max_hp == 0:
            return
        ratio = self.current_hp / self.max_hp
        # Check all thresholds — trigger the highest one not yet said
        for threshold in sorted(self.dialog.keys(), reverse=True):
            if threshold not in self._said_at and ratio <= threshold:
                self._said_at.add(threshold)
                text = self.dialog[threshold]
                if text is not None:
                    self._current_dialog = text
                    self._dialog_timer   = self.BUBBLE_DURATION
                break  # only one trigger per hit

    # ------------------------------------------------------------------
    # UPDATE — advance dialog timer
    # ------------------------------------------------------------------

    def update(self, dt):
        super().update(dt)   # handles animation
        if self._dialog_timer > 0:
            self._dialog_timer -= dt
            if self._dialog_timer <= 0:
                self._current_dialog = None
                self._dialog_timer   = 0.0

    # ------------------------------------------------------------------
    # DRAW — bubble above HP bar
    # ------------------------------------------------------------------

    def draw(self, screen):
        super().draw(screen)   # draws sprite + HP bar
        if self._current_dialog:
            self._draw_bubble(screen, self._current_dialog)

    def _draw_bubble(self, screen, text):
        """Draw a simple speech bubble above the HP bar."""
        px, py = self.BUBBLE_PADDING
        text_surf = self._font_bubble.render(text, True, self.BUBBLE_TEXT_COL)
        tw, th    = text_surf.get_size()

        bw = tw + px * 2
        bh = th + py * 2

        # Position : centered above HP bar (which is ~58px above sprite top)
        bx = self.rect.centerx - bw // 2
        by = self.rect.top - 40 - 8 - bh   # 40 = hp bar offset, 8 = gap

        # Clamp so bubble stays on screen
        bx = max(4, min(SCREEN_WIDTH  - bw - 4, bx))
        by = max(4, by)

        # Background rect
        bubble_rect = pygame.Rect(bx, by, bw, bh)
        pygame.draw.rect(screen, self.BUBBLE_COLOR,  bubble_rect, border_radius=self.BUBBLE_RADIUS)
        pygame.draw.rect(screen, self.BUBBLE_BORDER, bubble_rect, width=1,
                         border_radius=self.BUBBLE_RADIUS)

        # Small tail triangle pointing down toward the monster
        tail_x = self.rect.centerx
        tail_y = by + bh
        pts    = [(tail_x - 6, tail_y), (tail_x + 6, tail_y), (tail_x, tail_y + 8)]
        pygame.draw.polygon(screen, self.BUBBLE_COLOR,  pts)
        pygame.draw.polygon(screen, self.BUBBLE_BORDER, pts, 1)

        # Text
        screen.blit(text_surf, (bx + px, by + py))

        # Fade indicator — small alpha overlay as timer runs out
        if self._dialog_timer < 0.8:
            fade_a = int(255 * (1.0 - self._dialog_timer / 0.8))
            fade   = pygame.Surface((bw, bh), pygame.SRCALPHA)
            fade.fill((255, 255, 255, fade_a))
            screen.blit(fade, (bx, by))


# ===========================================================================
# ALLY
# ===========================================================================

class Ally:
    """
    Friendly entity that appears during quests.

    Properties defined in quest_data :
        name         : str
        image_file   : str  (sprite sheet)
        frame_w/h    : int
        frame_speed  : float
        animations   : dict  (same format as Monster)
        display_size : tuple
        pos          : (x_ratio, y_ratio)  — left side of screen
        auto_dps     : int   — damage dealt per tick
        dps_interval : float — seconds between each DPS tick
        dialog       : list  — one string per wave, shown at wave start
                               e.g. ["Allons-y !", "Tiens bon !", "Presque !"]

    Usage :
        ally = Ally(**ally_data)
        ally.set_wave_dialog(wave_index)   # called by QuestRoom on wave change
        ally.update(dt, targets)           # targets = list of living Mob
        ally.draw(screen)
    """

    BUBBLE_DURATION  = 6
    BUBBLE_PADDING   = (12, 8)
    BUBBLE_COLOR     = (220, 240, 255)   # light blue for ally
    BUBBLE_BORDER    = (80, 120, 180)
    BUBBLE_TEXT_COL  = (20, 40, 80)
    BUBBLE_RADIUS    = 8

    def __init__(self, name, image_file, display_size=(200, 200),
                 pos=(0.25, 0.75), frame_w=None, frame_h=None,
                 frame_speed=0.12, animations=None,
                 auto_dps=5, dps_interval=1.0,
                 dialog=None):

        self.name         = name
        self.display_size = (int(display_size[0]), int(display_size[1]))
        self.auto_dps     = auto_dps
        self.dps_interval = dps_interval
        self._dps_timer   = 0.0

        # Dialog — list of strings, one per wave
        self.dialog          = dialog or []
        self._current_dialog = None
        self._dialog_timer   = 0.0

        # ------------------------------------------------------------------
        # Sprite sheet loading
        # ------------------------------------------------------------------
        self._animated   = (frame_w is not None and animations is not None)
        self.frame_speed = frame_speed
        self.frame_index = 0.0

        raw_sheet = pygame.image.load(
            os.path.join(ASSETS_DIR, image_file)
        ).convert_alpha()

        if self._animated:
            self.animations   = {}
            self.current_anim = "idle"
            for anim_name, anim_data in animations.items():
                frames = []
                row    = anim_data["row"]
                count  = anim_data["frame_count"]
                for i in range(count):
                    raw    = raw_sheet.subsurface(
                        (i * frame_w, row * frame_h, frame_w, frame_h)
                    )
                    scaled = pygame.transform.scale(raw, self.display_size)
                    frames.append(scaled)
                self.animations[anim_name] = frames
            self.frames = self.animations["idle"]
            self.image  = self.frames[0]
        else:
            self.animations   = {}
            self.frames       = [pygame.transform.scale(raw_sheet, self.display_size)]
            self.image        = self.frames[0]

        # Position — allies stand on the left side
        self.rect = self.image.get_rect(
            midbottom=(SCREEN_WIDTH * pos[0], SCREEN_HEIGHT * pos[1])
        )

        self._font_name   = pygame.font.SysFont("Arial", 16, bold=True)
        self._font_bubble = pygame.font.SysFont("Arial", 14)

    # ------------------------------------------------------------------
    # WAVE DIALOG
    # ------------------------------------------------------------------

    def set_wave_dialog(self, wave_index: int):
        """Call this at the start of each wave to show the ally's line."""
        if wave_index < len(self.dialog):
            text = self.dialog[wave_index]
            if text:
                self._current_dialog = text
                self._dialog_timer   = self.BUBBLE_DURATION

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------

    def update(self, dt: float, targets: list):
        """
        dt      : delta time in seconds
        targets : list of living Mob/Monster to attack
        """
        # Animation
        if self._animated and self.frames:
            self.frame_index = (self.frame_index + self.frame_speed) % len(self.frames)
            self.image = self.frames[min(int(self.frame_index), len(self.frames) - 1)]

        # DPS tick
        if self.auto_dps > 0 and targets:
            self._dps_timer += dt
            if self._dps_timer >= self.dps_interval:
                self._dps_timer -= self.dps_interval
                target = targets[0]   # attack the first living target
                target.take_damage(self.auto_dps)

        # Dialog timer
        if self._dialog_timer > 0:
            self._dialog_timer -= dt
            if self._dialog_timer <= 0:
                self._current_dialog = None
                self._dialog_timer   = 0.0

    # ------------------------------------------------------------------
    # DRAW
    # ------------------------------------------------------------------

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        self._draw_name(screen)
        if self._current_dialog:
            self._draw_bubble(screen, self._current_dialog)

    def _draw_name(self, screen):
        """Small name label below the ally sprite."""
        surf = self._font_name.render(self.name, True, (200, 220, 255))
        screen.blit(surf, surf.get_rect(midtop=(self.rect.centerx, self.rect.bottom + 4)))

    def _draw_bubble(self, screen, text):
        """Speech bubble above the ally, pointing down."""
        px, py    = self.BUBBLE_PADDING
        text_surf = self._font_bubble.render(text, True, self.BUBBLE_TEXT_COL)
        tw, th    = text_surf.get_size()

        bw = tw + px * 2
        bh = th + py * 2

        bx = self.rect.centerx - bw // 2
        by = self.rect.top - 16 - bh

        bx = max(4, min(SCREEN_WIDTH - bw - 4, bx))
        by = max(4, by)

        bubble_rect = pygame.Rect(bx, by, bw, bh)
        pygame.draw.rect(screen, self.BUBBLE_COLOR,  bubble_rect, border_radius=self.BUBBLE_RADIUS)
        pygame.draw.rect(screen, self.BUBBLE_BORDER, bubble_rect, width=1,
                         border_radius=self.BUBBLE_RADIUS)

        # Tail
        tail_x = self.rect.centerx
        tail_y = by + bh
        pts    = [(tail_x - 6, tail_y), (tail_x + 6, tail_y), (tail_x, tail_y + 8)]
        pygame.draw.polygon(screen, self.BUBBLE_COLOR,  pts)
        pygame.draw.polygon(screen, self.BUBBLE_BORDER, pts, 1)

        screen.blit(text_surf, (bx + px, by + py))

        # Fade out
        if self._dialog_timer < 0.8:
            fade_a = int(255 * (1.0 - self._dialog_timer / 0.8))
            fade   = pygame.Surface((bw, bh), pygame.SRCALPHA)
            fade.fill((255, 255, 255, fade_a))
            screen.blit(fade, (bx, by))