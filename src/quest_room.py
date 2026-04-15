"""
quest_room.py
=============
QuestRoom inherits BossRoom. Differences :
  - Waves are dicts {mobs, allies_present} instead of plain lists
  - Mob entities (dialog bubbles)
  - Ally entities filtered per wave via allies_present
  - Reward system on victory
"""

import random
import pygame
from .boss_room import BossRoom
from .entities  import Mob, Ally
from .settings  import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE

STATE_FIGHTING = "fighting"
STATE_VICTORY  = "victory"
STATE_DEFEAT   = "defeat"

REWARD_DISPLAY_DURATION = 4.0


class QuestRoom(BossRoom):

    def __init__(self, quest_data: dict, player):
        # Assign before super().__init__() — _load_wave() needs these
        self.quest_data    = quest_data
        self._player       = player
        self.allies        = []          # populated by _load_allies()
        self.active_allies = []          # subset visible this wave

        super().__init__(quest_data)     # calls _load_wave(0)

        self._load_allies()
        self._update_active_allies(0)    # filter allies for wave 0

        self._rewards_collected  = False
        self._pending_rewards    = []
        self._show_reward_panel  = False
        self._reward_panel_timer = 0.0
        self._reward_lines       = []

        self.font_reward_title = pygame.font.SysFont("Verdana", 20, bold=True)
        self.font_reward_item  = pygame.font.SysFont("Verdana", 15)

    # ------------------------------------------------------------------
    # WAVE LOADING
    # ------------------------------------------------------------------

    def _load_wave(self, wave_index: int):
        """Override — wave is a dict {mobs, allies_present}."""
        self.monsters = []
        wave          = self.quest_data["waves"][wave_index]
        mob_list      = wave["mobs"]

        for mob_data in mob_list:
            x_base, x_range, y = mob_data["pos"]
            offset  = random.uniform(-x_range, x_range)
            final_x = x_base + offset

            m = Mob(
                name                = mob_data["name"],
                hp                  = mob_data["hp"],
                image_file          = mob_data["image_file"],
                display_size        = mob_data["display_size"],
                pos                 = (final_x, y),
                bonus               = mob_data.get("bonus", 0),
                apply_random_offset = False,
                frame_w             = mob_data.get("frame_w"),
                frame_h             = mob_data.get("frame_h"),
                frame_speed         = mob_data.get("frame_speed", 0.12),
                animations          = mob_data.get("animations"),
                dialog              = mob_data.get("dialog"),
            )
            self.monsters.append(m)

        # Notify active allies of new wave dialog
        for ally in self.active_allies:
            ally.set_wave_dialog(wave_index)

    # ------------------------------------------------------------------
    # ALLY MANAGEMENT
    # ------------------------------------------------------------------

    def _load_allies(self):
        """Instantiate ALL allies defined in quest_data."""
        for ally_data in self.quest_data.get("allies", []):
            ally = Ally(
                name         = ally_data["name"],
                image_file   = ally_data["image_file"],
                display_size = ally_data["display_size"],
                pos          = ally_data["pos"],
                frame_w      = ally_data.get("frame_w"),
                frame_h      = ally_data.get("frame_h"),
                frame_speed  = ally_data.get("frame_speed", 0.12),
                animations   = ally_data.get("animations"),
                auto_dps     = ally_data.get("auto_dps", 0),
                dps_interval = ally_data.get("dps_interval", 1.0),
                dialog       = ally_data.get("dialog", []),
            )
            self.allies.append(ally)

    def _update_active_allies(self, wave_index: int):
        """
        Filter self.allies to only those listed in allies_present
        for the given wave. Sets self.active_allies.
        """
        wave            = self.quest_data["waves"][wave_index]
        present_names   = wave.get("allies_present", [])
        self.active_allies = [
            a for a in self.allies if a.name in present_names
        ]

        # Notify newly active allies of wave dialog
        for ally in self.active_allies:
            ally.set_wave_dialog(wave_index)

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------

    def update(self, dt: float) -> str:
        if self.state != STATE_FIGHTING:
            return self.state

        self.time_remaining -= dt
        if self.time_remaining <= 0:
            self.time_remaining = 0
            self.state = STATE_DEFEAT
            return self.state

        # Update mobs
        for mob in self.monsters:
            mob.update(dt)

        # Update active allies only
        living_mobs = self.get_living_monsters()
        for ally in self.active_allies:
            ally.update(dt, living_mobs)

        # Reward panel countdown
        if self._show_reward_panel:
            self._reward_panel_timer -= dt
            if self._reward_panel_timer <= 0:
                self._show_reward_panel = False

        # Wave clear
        if self._is_wave_clear():
            next_wave = self.current_wave + 1
            if next_wave < len(self.quest_data["waves"]):
                self.current_wave = next_wave
                self._load_wave(self.current_wave)
                self._update_active_allies(self.current_wave)  # ← update allies
            else:
                self.state = STATE_VICTORY
                self._prepare_rewards()

        return self.state

    # ------------------------------------------------------------------
    # REWARDS
    # ------------------------------------------------------------------

    def _prepare_rewards(self):
        if self._rewards_collected:
            return
        self._pending_rewards    = self.quest_data.get("reward", [])
        self._reward_lines       = self._build_reward_lines()
        self._show_reward_panel  = True
        self._reward_panel_timer = REWARD_DISPLAY_DURATION

    def _build_reward_lines(self) -> list:
        lines = []
        for r in self._pending_rewards:
            t = r["type"]
            if t == "gold":
                lines.append(f"+ {r['amount']} Magic Stones")
            elif t == "stat":
                lines.append(f"+ {r['amount']} {r['stat'].capitalize()}")
            elif t == "hidden_skill":
                lines.append(f"New skill unlocked : {r['skill_id']}")
            elif t == "hidden_upgrade":
                lines.append(f"Skill upgraded : {r['skill_id']}")
        return lines

    def collect_rewards(self) -> list:
        self._rewards_collected = True
        return list(self._pending_rewards)

    # ------------------------------------------------------------------
    # DRAW
    # ------------------------------------------------------------------

    def draw(self, screen: pygame.Surface, player):
        for layer in self.layers:
            layer.draw(screen)
        for deco in self.decorations:
            deco.draw(screen)

        for mob in self.monsters:
            if mob.is_alive():
                mob.draw(screen)
        # Active allies only
        for ally in self.active_allies:
            ally.draw(screen)

        player.draw(screen)



        self._draw_timer(screen)
        self._draw_wave_info(screen)
        self._draw_raid_title(screen)

        if self._show_reward_panel:
            self._draw_reward_panel(screen)

    def _draw_raid_title(self, screen):
        surf = self.font_title.render(
            self.quest_data.get("label", "Quest"), True, COLOR_WHITE
        )
        screen.blit(surf, (20, 15))

    def _draw_reward_panel(self, screen):
        if not self._reward_lines:
            return

        pad     = 20
        line_h  = 28
        panel_w = 380
        panel_h = pad * 2 + 30 + len(self._reward_lines) * line_h

        px = SCREEN_WIDTH  // 2 - panel_w // 2
        py = SCREEN_HEIGHT // 2 - panel_h // 2

        t     = self._reward_panel_timer / REWARD_DISPLAY_DURATION
        alpha = 220 if t > 0.5 else int(220 * (t / 0.5))

        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (10, 30, 10, alpha),
                         panel.get_rect(), border_radius=14)
        pygame.draw.rect(panel, (60, 180, 80, alpha),
                         panel.get_rect(), width=2, border_radius=14)

        title = self.font_reward_title.render("Quest Complete !", True, (100, 255, 120))
        panel.blit(title, title.get_rect(midtop=(panel_w // 2, pad)))

        for i, line in enumerate(self._reward_lines):
            surf = self.font_reward_item.render(f"  {line}", True, (200, 255, 210))
            panel.blit(surf, (pad, pad + 30 + i * line_h))

        screen.blit(panel, (px, py))