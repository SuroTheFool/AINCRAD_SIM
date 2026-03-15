import pygame
import os
from .settings import ASSETS_DIR


class Decoration:
    """
    A single decorative element (tree, building, lamp...).
    Completely passive — just loads and draws itself.
    """

    def __init__(self, file, pos, size):
        path = os.path.join(ASSETS_DIR, file)
        raw  = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(raw, size)

        self.rect = self.image.get_rect(topleft=pos)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Layer:
    """
    A single background layer (sky, ground, fog..)
    scroll_speed > 0 activates horizontal scrolling (parallax effect).
    """

    def __init__(self, file, pos, size, scroll_speed=0):
        path = os.path.join(ASSETS_DIR, file)
        raw  = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(raw, size)
        self.rect  = self.image.get_rect(topleft=pos)

        self.scroll_speed = scroll_speed
        self.scroll_x     = 0.0   # current horizontal offset (float for smooth movement)
        # float instead of int → avoids choppy movement at slow speeds like 0.3px/frame

    def update(self):
        """Advance the scroll offset. Only does something if scroll_speed > 0."""
        if self.scroll_speed == 0:
            return

        self.scroll_x += self.scroll_speed

        # Reset when we've scrolled one full image width
        # This creates a seamless loop — image must be tileable left-to-right
        tile_width = self.image.get_width() // 2

        if self.scroll_x >= tile_width:
            self.scroll_x = 0.0


    def draw(self, screen):
        if self.scroll_speed == 0:
            # Static layer — normal draw, nothing changes
            screen.blit(self.image, self.rect)
            return

        tile_width = self.image.get_width() // 2
        x     = int(self.scroll_x)
        y     = self.rect.y

        screen.blit(self.image, (x, y))
        screen.blit(self.image, (x - tile_width, y))

class Floor:
    def __init__(self, floor_data):
        self.id = floor_data["id"]
        self.name = floor_data["name"]

        # build layers

        self.layers = [
            Layer(l["file"], l["pos"], l["size"], l.get("scroll_speed", 0))
            for l in floor_data["layers"]
        ]

        # Build decorations in order
        self.decorations = [
            Decoration(d["file"], d["pos"], d["size"])
            for d in floor_data["decorations"]
        ]

        # Monster pool for this floor (list of names, used by Game to filter)
        self.monster_pool = floor_data["monsters"]


    def draw(self, screen):
        """Draw all layers then all decorations."""
        for layer in self.layers:
            layer.draw(screen)
        for deco in self.decorations:
            deco.draw(screen)

    def update(self):
        """Update scrolling layers."""
        for layer in self.layers:
            layer.update()