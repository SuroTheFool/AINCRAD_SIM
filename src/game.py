import pygame
import random
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, ASSETS_DIR
from .entities  import Player, Monster
from .monsters_data import MONSTER_LIST
from .shop import Shop
from .floor import Floor
from .floor_data import FLOORS
from .player_data import PLAYER_SKINS
from .save_manager import save_game, save_exists, load_game
from .menu import Menu
from .boss_room import BossRoom
from .boss_data import BOSS_RAIDS
from .floor_button import FloorButton
from .skill_bar import SkillBar
from .audio_manager import AudioManager
from .hit_marker import HitMarkerManager



class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # --- Floor system ---
        self.current_floor_index = 0
        self.floor = self._load_floor(self.current_floor_index)

        # Initialize my entities
        self.current_skin = PLAYER_SKINS[0]
        self.player       = Player(self.current_skin, floor_id=1)
        self.monster = self._spawn_monster()
        self.audio = AudioManager()
        self.audio.play_music("floor_1")
        self.shop = Shop()
        self.floor_btn = FloorButton(self.shop.shop_btn_rect)
        self.gold = 0
        self.menu = Menu()
        self.skill_bar = SkillBar()
        self.hit_markers = HitMarkerManager()
        self.mode = "normal"
        self.boss_room = None
        self.highest_floor_unlocked = 0

        if save_exists():
            load_game(self)

        self.AUTO_DPS_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.AUTO_DPS_EVENT, 1000)

    # -----------------------------------------------------------

    def _load_floor(self, index):
        """Instantiate a floor from my import and data"""
        return Floor(FLOORS[index])

    def _spawn_monster(self):
        pool = self.floor.monster_pool
        names   = [entry["name"]   for entry in pool]
        weights = [entry["weight"] for entry in pool]
        chosen_name = random.choices(names, weights=weights, k=1)[0]
        data = next(m for m in MONSTER_LIST if m["name"] == chosen_name)
        return Monster(**data)

    def go_to_floor(self, index):
        """Transition to a new floor."""
        if 0 <= index < len(FLOORS):
            self.current_floor_index = index
            self.floor   = self._load_floor(index)
            self.monster = self._spawn_monster()
            floor_id     = FLOORS[index]["id"]
            self.player.change_floor(floor_id)
            self.audio.play_music(f"floor_{floor_id}")

    def start_boss_raid(self, floor_id):
        """Find the raid matching my floor_id"""
        raid = next((r for r in BOSS_RAIDS if r["floor_id"] == floor_id), None)
        if raid is None:
            print(f"No boss raid found for floor {floor_id}")
            return
        self.mode      = "boss_raid"
        self.boss_room = BossRoom(raid)
        self.audio.play_music("boss_raid")

    def _handle_boss_victory(self):
        """Unlocks next floor after victory"""
        unlocks = self.boss_room.raid_data["unlocks"]
        if unlocks > self.highest_floor_unlocked:
            self.highest_floor_unlocked = unlocks
            print("New floor unlocked")
        self.mode      = "normal"
        self.boss_room = None
        self.go_to_floor(self.current_floor_index)

    def _handle_boss_defeat(self):
        """Timer ran out — return to last unlocked floor."""
        print("Defeat ! Returning to last unlocked floor...")
        self.mode      = "normal"
        self.boss_room = None
        self.go_to_floor(self.highest_floor_unlocked)

    def _gold_for_kill(self, monster):
        base_reward = max(1, monster.max_hp // 10)
        return int((base_reward * self.player.gold_multiplier) + monster.bonus)

    # -------------------------------------------------------
    # Main loop
    # -------------------------------------------------------

    def run(self):
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)
        self._quit()

    # -------------------------------------------------------
    # Events
    # -------------------------------------------------------

    def _handle_events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                save_game(self)
                self.running = False

            # ---- KEYDOWN ----
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.shop.is_open:
                        self.shop.is_open = False
                    else:
                        self.menu.toggle()

                if event.key == pygame.K_RIGHT:
                    self.go_to_floor(self.current_floor_index + 1)
                if event.key == pygame.K_LEFT:
                    self.go_to_floor(self.current_floor_index - 1)
                if event.key == pygame.K_b:
                    self.start_boss_raid(floor_id=1)

                if not self.shop.is_open and not self.menu.is_open:
                    damage, skill_id = self.skill_bar.handle_keydown(
                        event, self.player,
                        monster=self.monster if self.mode == "normal" else None
                    )
                    if damage is not None and skill_id is not None:
                        target = self.monster if self.mode == "normal" else None
                        if target and target.is_alive():
                            target.take_damage(damage)
                            self.player.spawn_floating_text(damage, False, target.rect.center)
                            if not target.is_alive():
                                self.gold += self._gold_for_kill(target)
                                self.monster = self._spawn_monster()

            # ---- AUTO DPS ----
            if event.type == self.AUTO_DPS_EVENT:
                if self.mode == "normal" and self.player.auto_dps > 0 and self.monster.is_alive():
                    self.monster.take_damage(self.player.auto_dps)
                    self.player.spawn_floating_text(
                        self.player.auto_dps, False, self.monster.rect.center
                    )
                    if not self.monster.is_alive():
                        self.gold += self._gold_for_kill(self.monster)
                        self.monster = self._spawn_monster()

            # ---- MOUSE ----
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                action = self.menu.handle_click(event.pos, self)
                if action == "logout":
                    self.running = False
                    return

                if self.menu.is_open:
                    return

                # Boss raid mode
                if self.mode == "boss_raid":
                    result = self.boss_room.handle_click(event.pos, self.player)
                    if result is not None:
                        damage, is_crit, monster = result
                        self.hit_markers.spawn(
                            event.pos,
                            "crit" if is_crit else "normal"
                        )
                        self.audio.play_sfx( "crit" if is_crit else "hit")
                        self.player.spawn_floating_text(
                            damage, is_crit, monster.rect.center
                        )

                    return

                # Shop open button
                self.gold = self.shop.handle_click(
                    event.pos, is_open_click=True,
                    gold=self.gold, player=self.player,
                    highest_floor=self.highest_floor_unlocked
                )

                # Floor button
                self.floor_btn.handle_click(event.pos, self)
                if self.floor_btn.is_open:
                    return

                if self.shop.is_open:
                    old_gold = self.gold
                    self.gold = self.shop.handle_click(
                        event.pos, is_open_click=False,
                        gold=self.gold, player=self.player
                    )
                    if self.gold < old_gold:
                        self.audio.play_sfx("buy")
                elif self.monster.is_clicked(event.pos):
                    damage, is_crit = self.player.calculate_damage()
                    self.monster.take_damage(damage)
                    self.audio.play_sfx("crit" if is_crit else "hit")
                    self.hit_markers.spawn(event.pos, "crit" if is_crit else "normal")
                    self.player.spawn_floating_text(damage, is_crit, self.monster.rect.center)
                    if not self.monster.is_alive():
                        self.audio.play_sfx("death")
                        self.gold += self._gold_for_kill(self.monster)
                        self.monster = self._spawn_monster()

    # -------------------------------------------------------
    # Update
    # -------------------------------------------------------

    def _update(self):
        dt = self.clock.get_time() / 1000.0
        self.floor.update()
        self.player.update(dt)
        self.monster.update(dt)
        self.player.update_floating_texts()
        self.menu.update()

        if self.mode == "boss_raid":
            result = self.boss_room.update(dt)
            if result == "victory":
                self._handle_boss_victory()
            elif result == "defeat":
                self._handle_boss_defeat()

        self.hit_markers.update(dt)

    # -------------------------------------------------------
    # Draw
    # -------------------------------------------------------

    def _draw(self):
        if self.mode == "boss_raid":
            self.boss_room.draw(self.screen, self.player)
            self.player.draw_floating_texts(self.screen)
            self.menu.draw_menu_button(self.screen)
            self.skill_bar.draw(self.screen, self.player)
            self.hit_markers.draw(self.screen)
            self.menu.draw_overlay(self.screen)
            pygame.display.flip()
            return

        self.floor.draw(self.screen)
        self.player.draw(self.screen)
        self.monster.draw(self.screen)
        self.player.draw_floating_texts(self.screen)
        self.hit_markers.draw(self.screen)
        self.shop.draw_shop_button(self.screen, self.gold)
        self.floor_btn.draw_floor_button(self.screen)
        self.skill_bar.draw(self.screen, self.player)
        self.menu.draw_menu_button(self.screen)
        self.shop.draw_overlay(
            self.screen, self.gold, self.player,
            highest_floor=self.highest_floor_unlocked
        )
        self.floor_btn.draw_overlay(self.screen, self)
        self.menu.draw_overlay(self.screen)
        pygame.display.flip()

    @staticmethod
    def _quit():
        pygame.quit()