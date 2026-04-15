import pygame
import random
from .entities  import Monster
from .settings  import SCREEN_WIDTH, SCREEN_HEIGHT, ASSETS_DIR, COLOR_WHITE
import os

STATE_FIGHTING = "fighting"
STATE_VICTORY = "victory"
STATE_DEFEAT = "defeat"

COLOR_TIMER_OK   = (100, 220, 100)    # green — plenty of time
COLOR_TIMER_WARN = (220, 180, 50)     # yellow — under 30s
COLOR_TIMER_CRIT = (220, 60,  60)     # red — under 10s


class BossRoom:
    """Manages a full boss raid"""
    def __init__(self, raid_data):
        self.raid_data      = raid_data
        self.state          = STATE_FIGHTING
        self.time_remaining = float(raid_data["time_limit"])
        self.current_wave   = 0

        from .floor import Layer,Decoration
        bg_folder = raid_data["background"]
        self.layers = [
            Layer(
                os.path.join(bg_folder, "room.png"),
                pos=(0, 0),
                size=(SCREEN_WIDTH, SCREEN_HEIGHT)
            )
        ]
        self.decorations = [
        #     Decoration(
        #         os.path.join(bg_folder, "pillar_left.png"),
        #         pos=(50, SCREEN_HEIGHT - 400),
        #         size=(180, 350)
        #     ),
        #     Decoration(
        #         os.path.join(bg_folder, "pillar_right.png"),
        #         pos=(SCREEN_WIDTH - 230, SCREEN_HEIGHT - 400),
        #         size=(180, 350)
        #     ),
        ]

        # Texts fonts
        self.font_timer = pygame.font.SysFont("Verdana", 36, bold=True)
        self.font_wave = pygame.font.SysFont("Verdana", 18, bold=True)
        self.font_title = pygame.font.SysFont("Verdana", 22, bold=True)

        # --- Load first wave ---
        self.monsters = []
        self._load_wave(self.current_wave)

    def update(self, dt):
        if self.state != STATE_FIGHTING:
            return self.state

        self.time_remaining -= dt
        if self.time_remaining <=0:
            self.time_remaining = 0
            self.state = STATE_DEFEAT
            return self.state

        for monster in self.monsters:
            monster.update(dt)

        if self._is_wave_clear():
            next_wave_index = self.current_wave + 1
            if next_wave_index < len(self.raid_data["waves"]):
                self.current_wave = next_wave_index
                self._load_wave(self.current_wave)
            else:
                self.state = STATE_VICTORY

        return self.state

    def handle_click(self,mouse_pos,player):
        for monster in self.monsters:
            if monster.is_alive() and monster.is_clicked(mouse_pos):
                damage, is_crit = player.calculate_damage()
                monster.take_damage(damage)
                return damage, is_crit, monster
        return None

    def get_living_monsters(self):
        return [m for m in self.monsters if m.is_alive()]
    # Drawing methods
    def draw(self,screen,player):

        for layer in self.layers:
            layer.draw(screen)
        for deco in self.decorations:
            deco.draw(screen)

        player.draw(screen)
        for monster in self.monsters:
            if monster.is_alive():
                monster.draw(screen)
        self._draw_timer(screen)
        self._draw_wave_info(screen)
        self._draw_raid_title(screen)

    def _draw_timer(self, screen):
        """
        Countdown timer displayed at the top-center of the screen.
        Changes color as time runs out.
        """
        seconds = int(self.time_remaining)

        if seconds > 30:
            color = COLOR_TIMER_OK
        elif seconds > 10:
            color = COLOR_TIMER_WARN
        else:
            color = COLOR_TIMER_CRIT

        # Format : MM:SS
        minutes = seconds // 60
        secs = seconds % 60
        time_str = f"{minutes:01d}:{secs:02d}"

        # Shadow for readability
        shadow = self.font_timer.render(time_str, True, (0, 0, 0))
        surf = self.font_timer.render(time_str, True, color)
        rect = surf.get_rect(midtop=(SCREEN_WIDTH // 2, 15))

        screen.blit(shadow, (rect.x + 2, rect.y + 2))
        screen.blit(surf, rect)

    def _draw_wave_info(self, screen):
        """
        Wave progress shown below the timer.
        Example : "Wave 1 / 2"
        """
        total = len(self.raid_data["waves"])
        wave_str = f"Wave {self.current_wave + 1} / {total}"
        surf = self.font_wave.render(wave_str, True, COLOR_WHITE)
        screen.blit(surf, surf.get_rect(midtop=(SCREEN_WIDTH // 2, 58)))

    def _draw_raid_title(self, screen):
        """Boss raid name shown at the top-left."""
        surf = self.font_title.render(self.raid_data["name"], True, COLOR_WHITE)
        screen.blit(surf, (20, 15))

    def _is_wave_clear(self):
        """Returns True if all monsters in the current wave are dead."""
        return all(not m.is_alive() for m in self.monsters)

    def _load_wave(self, wave_index):
        """Instantiate all monsters for the given wave index."""
        self.monsters = []
        wave_data = self.raid_data["waves"][wave_index]

        for monster_data in wave_data:
            # pos in boss_data has 3 values : (x_base, x_range, y)
            # We convert it to the 2-value tuple Monster expects
            # by applying the random offset here
            x_base, x_range, y = monster_data["pos"]
            offset = random.uniform(-x_range, x_range)
            final_x = x_base + offset

            # Build a clean dict for Monster(**data)
            m_data = {
                "name": monster_data["name"],
                "hp": monster_data["hp"],
                "image_file": monster_data["image_file"],
                "display_size": monster_data["display_size"],
                "pos": (final_x, y),  # already resolved, no range
                "bonus": monster_data.get("bonus", 0),
                "apply_random_offset": False,"frame_w"            : monster_data.get("frame_w"),
                "frame_h"            : monster_data.get("frame_h"),
                "frame_speed"        : monster_data.get("frame_speed", 0.12),
                "animations"         : monster_data.get("animations"),
        }
            self.monsters.append(Monster(**m_data))

