"""
hit_marker.py
=============
Effets visuels de coup style slash anime.

Normal : 2 traits blancs/jaunes qui traversent l'écran en diagonale
Crit   : slash rouge vif + ombre noire décalée, plus large et plus long,
         avec un éclat central blanc au point d'impact
"""

import math
import random
import pygame


# ---------------------------------------------------------------------------
# COULEURS
# ---------------------------------------------------------------------------
COLOR_NORMAL_1   = (255, 255, 180)   # blanc chaud
COLOR_NORMAL_2   = (255, 200,  60)   # jaune doré

COLOR_CRIT_RED   = (220,  20,  20)   # rouge vif
COLOR_CRIT_DARK  = ( 40,   0,   0)   # noir rouge (ombre)
COLOR_CRIT_CORE  = (255, 255, 255)   # éclat central blanc


# ---------------------------------------------------------------------------
# UTILITAIRES
# ---------------------------------------------------------------------------

def _lerp(a, b, t):
    return a + (b - a) * t


def _lerp_color(c1, c2, t):
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


def _slash_polygon(cx, cy, angle, length, width):
    """
    draw a slash
    """
    dx = math.cos(angle)
    dy = math.sin(angle)
    px = -dy
    py =  dx

    half_len = length / 2
    half_w   = width  / 2

    p1 = (cx - dx * half_len - px * half_w,
          cy - dy * half_len - py * half_w)
    p2 = (cx - dx * half_len + px * half_w,
          cy - dy * half_len + py * half_w)
    p3 = (cx + dx * half_len + px * half_w * 0.1,
          cy + dy * half_len + py * half_w * 0.1)
    p4 = (cx + dx * half_len - px * half_w * 0.1,
          cy + dy * half_len - py * half_w * 0.1)

    return [p1, p2, p3, p4]




class HitMarker:
    DURATION_NORMAL = 0.55
    DURATION_CRIT   = 1.0

    def __init__(self, pos, kind="normal"):
        self.x        = pos[0]
        self.y        = pos[1]
        self.kind     = kind
        self.elapsed  = 0.0
        self.duration = self.DURATION_CRIT if kind == "crit" else self.DURATION_NORMAL
        self.alive    = True

        base_angle       = random.uniform(math.radians(0), math.radians(10))
        self.angle_main  = base_angle
        self.angle_shadow = base_angle + math.radians(random.uniform(8, 16))

        self.travel = random.choice([-1, 1])   # SLIDE DURING ANIMATION

    # -----------------------------------------------------------------------

    def update(self, dt):
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.alive = False

    def draw(self, screen):
        t     = self.elapsed / self.duration
        alpha = int(255 * (1.0 - t) ** 1.4)

        if self.kind == "normal":
            self._draw_normal(screen, t, alpha)
        else:
            self._draw_crit(screen, t, alpha)


    def _draw_normal(self, screen, t, alpha):

        expand = math.sqrt(t)   # ease-out
        length = _lerp(150, 200, expand)
        width  = _lerp(12,  4,  t)

        # Léger glissement perpendiculaire
        offset = self.travel * _lerp(0, 12, t)
        px     = -math.sin(self.angle_main) * offset
        py     =  math.cos(self.angle_main) * offset

        size = 300
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx = cy = size // 2

        color1 = (*COLOR_NORMAL_1, alpha)
        pts1   = _slash_polygon(cx + px, cy + py,
                                self.angle_main, length, width)
        pygame.draw.polygon(surf, color1, pts1)

        color2 = (*COLOR_NORMAL_2, int(alpha * 0.55))
        pts2   = _slash_polygon(cx + px * 1.4 + 4, cy + py * 1.4 + 4,
                                self.angle_main + math.radians(12),
                                length * 0.65, width * 0.6)
        pygame.draw.polygon(surf, color2, pts2)

        screen.blit(surf, (self.x - cx, self.y - cy))

    # -----------------------------------------------------------------------
    # CRIT — slash rouge vif + ombre noire décalée + éclat central
    # -----------------------------------------------------------------------

    def _draw_crit(self, screen, t, alpha):
        # Phase 1 (0 → 0.3) : apparition explosive
        # Phase 2 (0.3 → 1) : dissolution lente
        if t < 0.3:
            expand = (t / 0.3) ** 0.5   # très rapide au début
        else:
            expand = 1.0

        length_main   = _lerp(400, 500, expand) * _lerp(1.0, 0.6, t)
        width_main    = _lerp(24, 10,  t)
        length_shadow = length_main * 0.85
        width_shadow  = width_main  * 1.3

        # Glissement du slash vers la direction de coupe
        offset = self.travel * _lerp(0, 18, t)
        px     = -math.sin(self.angle_main) * offset
        py     =  math.cos(self.angle_main) * offset

        size = 200
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx = cy = size // 2

        # --- Ombre noire (dessinée en premier, légèrement décalée) ---
        shadow_offset_x = math.cos(self.angle_shadow) * 6
        shadow_offset_y = math.sin(self.angle_shadow) * 6
        shadow_alpha    = int(alpha * 0.75)

        pts_shadow = _slash_polygon(
            cx + px + shadow_offset_x,
            cy + py + shadow_offset_y,
            self.angle_shadow,
            length_shadow, width_shadow
        )
        pygame.draw.polygon(surf, (*COLOR_CRIT_DARK, shadow_alpha), pts_shadow)

        # --- Slash rouge principal ---
        pts_main = _slash_polygon(cx + px, cy + py,
                                  self.angle_main, length_main, width_main)
        pygame.draw.polygon(surf, (*COLOR_CRIT_RED, alpha), pts_main)

        # --- Liseré blanc sur le bord du slash rouge (effet tranchant) ---
        if width_main > 3:
            edge_w  = max(1, int(width_main * 0.25))
            pts_edge = _slash_polygon(cx + px, cy + py,
                                      self.angle_main,
                                      length_main * 0.9, edge_w)
            pygame.draw.polygon(surf, (*COLOR_CRIT_CORE, int(alpha * 0.7)), pts_edge)

        # --- Éclat central au point d'impact (disparaît vite) ---
        if t < 0.35:
            core_t = t / 0.35
            core_r = int(_lerp(10, 2, core_t))
            core_a = int(255 * (1.0 - core_t) ** 2)
            if core_r > 0:
                pygame.draw.circle(surf, (*COLOR_CRIT_CORE, core_a),
                                   (cx, cy), core_r)
                # Petits rayons autour de l'éclat
                for i in range(4):
                    ray_angle = self.angle_main + i * (math.pi / 2)
                    r1 = core_r + 2
                    r2 = core_r + int(8 * (1.0 - core_t))
                    x1 = int(cx + math.cos(ray_angle) * r1)
                    y1 = int(cy + math.sin(ray_angle) * r1)
                    x2 = int(cx + math.cos(ray_angle) * r2)
                    y2 = int(cy + math.sin(ray_angle) * r2)
                    pygame.draw.line(surf, (*COLOR_CRIT_CORE, core_a),
                                     (x1, y1), (x2, y2), 2)

        screen.blit(surf, (self.x - cx, self.y - cy))




class HitMarkerManager:
    def __init__(self):
        self._markers: list[HitMarker] = []

    def spawn(self, pos, kind="normal"):
        self._markers.append(HitMarker(pos, kind))

    def update(self, dt):
        for m in self._markers:
            m.update(dt)
        self._markers = [m for m in self._markers if m.alive]

    def draw(self, screen):
        for m in self._markers:
            m.draw(screen)