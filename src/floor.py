import pygame
import os
import random
from .settings import ASSETS_DIR, SCREEN_WIDTH, SCREEN_HEIGHT
from .entities import Monster
from .monsters_data import MONSTER_LIST


class Decoration:
    """A single decorative element. Passive — just loads and draws."""

    def __init__(self, file, pos, size):
        path = os.path.join(ASSETS_DIR, file)
        raw  = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(raw, size)
        self.rect  = self.image.get_rect(topleft=pos)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Layer:
    """
    A single background layer (sky, ground, fog...).
    scroll_speed > 0 activates horizontal scrolling (parallax).
    """

    def __init__(self, file, pos, size, scroll_speed=0):
        path = os.path.join(ASSETS_DIR, file)
        raw  = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(raw, size)
        self.rect  = self.image.get_rect(topleft=pos)

        self.scroll_speed = scroll_speed
        self.scroll_x     = 0.0

    def update(self):
        if self.scroll_speed == 0:
            return
        self.scroll_x += self.scroll_speed
        tile_width = self.image.get_width() // 2
        if self.scroll_x >= tile_width:
            self.scroll_x = 0.0

    def draw(self, screen):
        if self.scroll_speed == 0:
            screen.blit(self.image, self.rect)
            return
        tile_width = self.image.get_width() // 2
        x = int(self.scroll_x)
        y = self.rect.y
        screen.blit(self.image, (x, y))
        screen.blit(self.image, (x - tile_width, y))


class Floor:
    """
    Owns the background layers, decorations, and the current Monster.

    Game no longer holds self.monster — everything goes through Floor.

    Usage in Game :
        # Click handling
        result = self.floor.handle_click(event.pos, self.player)
        if result:
            self.gold += result["gold"]
            self.audio.play_sfx("death" if result["killed"] else "hit")
            self.hit_markers.spawn(event.pos, "crit" if result["is_crit"] else "normal")

        # Update
        self.floor.update(dt)

        # Draw background only (before player/HUD)
        self.floor.draw(screen)

        # Draw monster (after player, before HUD)
        self.floor.draw_monster(screen)
    """

    def __init__(self, floor_data):
        self.id   = floor_data["id"]
        self.name = floor_data["name"]

        self.layers = [
            Layer(l["file"], l["pos"], l["size"], l.get("scroll_speed", 0))
            for l in floor_data["layers"]
        ]
        self.decorations = [
            Decoration(d["file"], d["pos"], d["size"])
            for d in floor_data["decorations"]
        ]

        # Monster pool — list of {"name": ..., "weight": ...}
        self.monster_pool = floor_data["monsters"]

        # Spawn the first monster immediately
        self.monster = self._spawn_monster()

    # ------------------------------------------------------------------
    # MONSTER MANAGEMENT
    # ------------------------------------------------------------------

    def _spawn_monster(self):
        """Pick a random monster from the pool and instantiate it."""
        names   = [entry["name"]   for entry in self.monster_pool]
        weights = [entry["weight"] for entry in self.monster_pool]
        chosen  = random.choices(names, weights=weights, k=1)[0]
        data    = next(m for m in MONSTER_LIST if m["name"] == chosen)
        return Monster(**data)

    def handle_click(self, pos, player):
        """
        Handle a mouse click on the floor area.
        If the monster is hit, apply damage and respawn if killed.

        Returns a dict if the monster was hit :
            {
                "damage"  : int,
                "is_crit" : bool,
                "gold"    : int,     # 0 if not killed
                "killed"  : bool,
            }
        Returns None if the click missed.
        """
        if not self.monster.is_alive():
            return None

        if not self.monster.is_clicked(pos):
            return None

        damage, is_crit = player.calculate_damage()
        self.monster.take_damage(damage)

        killed = not self.monster.is_alive()
        gold   = self._gold_for_kill() if killed else 0

        if killed:
            self.monster = self._spawn_monster()

        return {
            "damage" : damage,
            "is_crit": is_crit,
            "gold"   : gold,
            "killed" : killed,
        }

    def _gold_for_kill(self):
        """Gold reward for the current monster. Called just before respawn."""
        base = max(1, self.monster.max_hp // 10)
        return int(base * 1.0 + self.monster.bonus)
        # Note: gold_multiplier from player is applied in Game after receiving result

    # ------------------------------------------------------------------
    # UPDATE & DRAW
    # ------------------------------------------------------------------

    def update(self, dt):
        """Update scrolling layers and monster animation."""
        for layer in self.layers:
            layer.update()
        self.monster.update(dt)

    def draw(self, screen):
        """Draw background layers and decorations only."""
        for layer in self.layers:
            layer.draw(screen)
        for deco in self.decorations:
            deco.draw(screen)

    def draw_monster(self, screen):
        """Draw the current monster. Call this after player, before HUD."""
        self.monster.draw(screen)