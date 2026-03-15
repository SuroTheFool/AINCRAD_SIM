import math
import pygame
import os
from .settings import (SCREEN_WIDTH, SCREEN_HEIGHT, ASSETS_DIR,
                        COLOR_ACCENT, COLOR_WHITE)
import random


class Player:
    """Player class — animated via sprite sheet, supports active skill slots."""

    def __init__(self, skin_data, floor_id=1):
        # ------------------------------------------------------------------
        # COMBAT STATS
        # ------------------------------------------------------------------
        self.click_damage    = 1
        self.crit_chance     = 0.02
        self.crit_multiplier = 2.0
        self.auto_dps        = 0
        self.gold_multiplier = 1.0

        # RPG STATS
        self.strength     = 0
        self.intelligence = 0
        self.endurance    = 1
        self.current_end  = 10.0

        # ------------------------------------------------------------------
        # SKILL SLOTS & ACTIVE EFFECTS
        # ------------------------------------------------------------------
        self.skill_slots    = [None, None, None, None, None]
        self.active_effects = {}

        # ------------------------------------------------------------------
        # SPRITE SHEET
        # ------------------------------------------------------------------
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

        # ------------------------------------------------------------------
        # POSITION
        # ------------------------------------------------------------------
        self._apply_position(floor_id)

        # ------------------------------------------------------------------
        # FONTS & FLOATING TEXTS
        # ------------------------------------------------------------------
        self.font_dmg       = pygame.font.SysFont("Arial", 28, bold=True)
        self.floating_texts = []

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------

    def update(self, dt=0):
        # --- Animation ---
        self.frame_index = (self.frame_index + self.frame_speed) % len(self.frames)
        self.image       = self.frames[int(self.frame_index)]
        midbottom        = self.rect.midbottom
        self.rect        = self.image.get_rect(midbottom=midbottom)

        # --- Endurance regen : +3 pts/sec ---
        max_end          = self.endurance * 10
        regen            = (dt * 3.0) if dt > 0 else 0.05
        self.current_end = min(max_end, self.current_end + regen)

        # --- Active effect countdown ---
        if dt > 0:
            expired = [sid for sid, t in self.active_effects.items() if t - dt <= 0]
            for sid in expired:
                del self.active_effects[sid]
            for sid in self.active_effects:
                self.active_effects[sid] -= dt

    # ------------------------------------------------------------------
    # ANIMATION
    # ------------------------------------------------------------------

    def set_animation(self, name):
        if name == self.current_anim or name not in self.animations:
            return
        self.current_anim = name
        self.frames       = self.animations[name]
        self.frame_index  = 0.0

    # ------------------------------------------------------------------
    # POSITION
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # COMBAT
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # SKILL SYSTEM
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # FLOATING TEXTS
    # ------------------------------------------------------------------

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
    """
    Clickable enemy.

    Supporte deux modes selon les données dans monsters_data.py :

    MODE STATIQUE (monstres existants — rien à changer) :
        {"name": "Goblin", "hp": 100, "image_file": "goblin.png", ...}

    MODE ANIMÉ (nouveaux monstres avec sprite sheet) :
        {
            "name"       : "Skeleton",
            "hp"         : 150,
            "image_file" : "skeleton.png",   ← la sprite sheet complète
            "frame_w"    : 64,               ← largeur d'une frame en px
            "frame_h"    : 64,               ← hauteur d'une frame en px
            "frame_speed": 0.15,             ← vitesse d'animation
            "animations" : {
                "idle" : {"row": 0, "frame_count": 4},
                "hurt" : {"row": 1, "frame_count": 2},  ← optionnel
                "death": {"row": 2, "frame_count": 5},  ← optionnel
            },
            "display_size": (192, 192),      ← taille affichée (multiple de frame_w)
            ...
        }

    Si "frame_w" est absent → mode statique automatiquement.
    """

    def __init__(self, name, hp, image_file, display_size=(220, 220),
                 pos=(0.72, 0.72), bonus=0, apply_random_offset=True,
                 frame_w=None, frame_h=None, frame_speed=0.12,
                 animations=None):

        self.name         = name
        self.max_hp       = hp
        self.current_hp   = hp
        self.display_size = display_size
        self.bonus        = bonus

        random_offset = random.uniform(-0.03, 0.03) if apply_random_offset else 0
        self._pos_x   = SCREEN_WIDTH  * (pos[0] + random_offset)
        self._pos_y   = SCREEN_HEIGHT * pos[1]

        # ------------------------------------------------------------------
        # CHARGEMENT — statique ou animé
        # ------------------------------------------------------------------
        self._animated   = (frame_w is not None and animations is not None)
        self.frame_speed = frame_speed
        self.frame_index = 0.0



        raw_sheet = pygame.image.load(
            os.path.join(ASSETS_DIR, image_file)
        ).convert_alpha()

        if self._animated:
            # Découpe la sprite sheet en animations
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
                    scaled = pygame.transform.scale(raw, display_size)
                    frames.append(scaled)
                self.animations[anim_name] = frames

            self.frames = self.animations["idle"]
            self.image  = self.frames[0]

        else:
            # Mode statique — comportement original
            self.animations   = {}
            self.current_anim = "idle"
            self.frames       = [pygame.transform.scale(raw_sheet, display_size)]
            self.image        = self.frames[0]

        # ------------------------------------------------------------------
        # RECT & MASK
        # ------------------------------------------------------------------
        self.rect = self.image.get_rect(midbottom=(self._pos_x, self._pos_y))
        self.font = pygame.font.SysFont("Arial", 22, bold=True)
        self.mask = pygame.mask.from_surface(self.image)

    # ------------------------------------------------------------------
    # ANIMATION
    # ------------------------------------------------------------------

    def _set_animation(self, name):
        """Change l'animation courante si elle existe."""
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


    # ------------------------------------------------------------------
    # COMBAT
    # ------------------------------------------------------------------

    def is_alive(self):
        return self.current_hp > 0

    def take_damage(self, damage):
        self.current_hp = max(0, self.current_hp - damage)

    # ------------------------------------------------------------------
    # CLICK
    # ------------------------------------------------------------------

    def is_clicked(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            rel_x = mouse_pos[0] - self.rect.x
            rel_y = mouse_pos[1] - self.rect.y
            try:
                return self.mask.get_at((rel_x, rel_y))
            except IndexError:
                return True
        return False

    # ------------------------------------------------------------------
    # DRAW
    # ------------------------------------------------------------------

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