import pygame
from .settings    import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, ASSETS_DIR
from .entities    import Player
from .shop        import Shop
from .floor       import Floor
from .floor_data  import FLOORS
from .player_data import PLAYER_SKINS
from .save_manager import save_game, save_exists, load_game
from .menu        import Menu
from .boss_room   import BossRoom
from .boss_data   import BOSS_RAIDS
from .floor_button import FloorButton
from .skill_bar   import SkillBar
from .audio_manager import AudioManager
from .hit_marker  import HitMarkerManager


class Game:
    def __init__(self, screen):
        self.screen  = screen
        self.clock   = pygame.time.Clock()
        self.running = True

        # --- Floor ---
        self.current_floor_index = 0
        self.floor = self._load_floor(self.current_floor_index)

        # --- Entities & systems ---
        self.current_skin = PLAYER_SKINS[0]
        self.player       = Player(self.current_skin, floor_id=1)
        self.audio        = AudioManager()
        self.audio.play_music("floor_1")
        self.shop         = Shop()
        self.floor_btn    = FloorButton(self.shop.shop_btn_rect)
        self.gold         = 0
        self.menu         = Menu()
        self.skill_bar    = SkillBar()
        self.hit_markers  = HitMarkerManager()
        self.mode         = "normal"
        self.boss_room    = None
        self.quest_room   = None
        self.highest_floor_unlocked = 0
        self.completed_quests       = set()

        if save_exists():
            load_game(self)

        self.AUTO_DPS_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.AUTO_DPS_EVENT, 1000)

    # ------------------------------------------------------------------
    # Floor
    # ------------------------------------------------------------------

    def _load_floor(self, index):
        return Floor(FLOORS[index])

    def go_to_floor(self, index):
        if 0 <= index < len(FLOORS):
            self.current_floor_index = index
            self.floor   = self._load_floor(index)
            floor_id     = FLOORS[index]["id"]
            self.player.change_floor(floor_id)
            self.audio.play_music(f"floor_{floor_id}")

    # ------------------------------------------------------------------
    # Boss raid
    # ------------------------------------------------------------------

    def start_boss_raid(self, floor_id):
        raid = next((r for r in BOSS_RAIDS if r["floor_id"] == floor_id), None)
        if raid is None:
            return
        self.mode      = "boss_raid"
        self.boss_room = BossRoom(raid)
        self.audio.play_music("boss_raid")

    def _handle_boss_victory(self):
        unlocks = self.boss_room.raid_data["unlocks"]
        if unlocks > self.highest_floor_unlocked:
            self.highest_floor_unlocked = unlocks
        self.mode      = "normal"
        self.boss_room = None
        self.go_to_floor(self.current_floor_index)

    def _handle_boss_defeat(self):
        self.mode      = "normal"
        self.boss_room = None
        self.go_to_floor(self.highest_floor_unlocked)

    # ------------------------------------------------------------------
    # Quest
    # ------------------------------------------------------------------

    def start_quest(self, quest_id):
        from .quest_data import get_quest_by_id
        from .quest_room import QuestRoom
        quest = get_quest_by_id(quest_id)
        if quest is None:
            return
        self.mode       = "quest"
        self.quest_room = QuestRoom(quest, self.player)
        self.audio.play_music("boss_raid")

    def _handle_quest_victory(self):
        rewards = self.quest_room.collect_rewards()
        self._apply_quest_rewards(rewards)
        self.completed_quests.add(self.quest_room.quest_data["id"])
        self.mode       = "normal"
        self.quest_room = None
        self.go_to_floor(self.current_floor_index)

    def _handle_quest_defeat(self):
        self.mode       = "normal"
        self.quest_room = None
        self.go_to_floor(self.current_floor_index)

    def _apply_quest_rewards(self, rewards: list):
        """Apply each reward dict returned by QuestRoom.collect_rewards()."""
        for r in rewards:
            t = r["type"]

            if t == "gold":
                self.gold += r["amount"]

            elif t == "stat":
                stat    = r["stat"]
                current = getattr(self.player, stat, 0)
                setattr(self.player, stat, current + r["amount"])

            elif t == "hidden_skill":
                skill_id = r["skill_id"]
                # Mark as owned in shop so it can be equipped + upgraded
                if not hasattr(self.shop, "hidden_skill_owned"):
                    self.shop.hidden_skill_owned = {}
                if not hasattr(self.shop, "hidden_skill_levels"):
                    self.shop.hidden_skill_levels = {}
                self.shop.hidden_skill_owned[skill_id]  = 1
                self.shop.hidden_skill_levels.setdefault(skill_id, 0)

            elif t == "hidden_upgrade":
                skill_id = r["skill_id"]
                if not hasattr(self.shop, "hidden_skill_levels"):
                    self.shop.hidden_skill_levels = {}
                lvl = self.shop.hidden_skill_levels.get(skill_id, 0)
                self.shop.hidden_skill_levels[skill_id] = lvl + 1

    # ------------------------------------------------------------------
    # Gold helper
    # ------------------------------------------------------------------

    def _gold_for_kill(self, monster):
        base = max(1, monster.max_hp // 10)
        return int((base * self.player.gold_multiplier) + monster.bonus)

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self):
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)
        self._quit()

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

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

                # Skill keys
                if not self.shop.is_open and not self.menu.is_open:
                    if self.mode == "normal":
                        monster = self.floor.monster
                    elif self.mode == "boss_raid" and self.boss_room:
                        living  = self.boss_room.get_living_monsters()
                        monster = living[0] if living else None
                    elif self.mode == "quest" and self.quest_room:
                        living  = self.quest_room.get_living_monsters()
                        monster = living[0] if living else None
                    else:
                        monster = None

                    damage, skill_id = self.skill_bar.handle_keydown(
                        event, self.player, monster=monster
                    )
                    if damage is not None and skill_id is not None:
                        if monster and monster.is_alive():
                            monster.take_damage(damage)
                            self.hit_markers.spawn(monster.rect.center, "crit")
                            self.player.spawn_floating_text(damage, False, monster.rect.center)
                            if self.mode == "normal" and not monster.is_alive():
                                self.gold += self._gold_for_kill(monster)
                                self.floor.monster = self.floor._spawn_monster()

            # ---- AUTO DPS ----
            if event.type == self.AUTO_DPS_EVENT:
                if self.mode == "normal" and self.player.auto_dps > 0:
                    monster = self.floor.monster
                    if monster.is_alive():
                        monster.take_damage(self.player.auto_dps)
                        self.player.spawn_floating_text(
                            self.player.auto_dps, False, monster.rect.center
                        )
                        if not monster.is_alive():
                            self.gold += self._gold_for_kill(monster)
                            self.floor.monster = self.floor._spawn_monster()

            # ---- MOUSE ----
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                action = self.menu.handle_click(event.pos, self)
                if action == "logout":
                    self.running = False
                    return

                if self.menu.is_open:
                    return

                # ── Boss raid ────────────────────────────────────────────
                if self.mode == "boss_raid":
                    result = self.boss_room.handle_click(event.pos, self.player)
                    if result is not None:
                        damage, is_crit, monster = result
                        self.hit_markers.spawn(
                            monster.rect.center,
                            "crit" if is_crit else "normal"
                        )
                        self.audio.play_sfx("crit" if is_crit else "hit")
                        self.player.spawn_floating_text(
                            damage, is_crit, monster.rect.center
                        )
                    return

                # ── Quest ────────────────────────────────────────────────
                if self.mode == "quest":
                    result = self.quest_room.handle_click(event.pos, self.player)
                    if result is not None:
                        damage, is_crit, mob = result
                        self.hit_markers.spawn(
                            mob.rect.center,
                            "crit" if is_crit else "normal"
                        )
                        self.audio.play_sfx("crit" if is_crit else "hit")
                        self.player.spawn_floating_text(
                            damage, is_crit, mob.rect.center
                        )
                    return

                # ── Normal mode ──────────────────────────────────────────
                self.gold = self.shop.handle_click(
                    event.pos, is_open_click=True,
                    gold=self.gold, player=self.player,
                    highest_floor=self.highest_floor_unlocked
                )

                self.floor_btn.handle_click(event.pos, self)
                if self.floor_btn.is_open:
                    return

                if self.shop.is_open:
                    old_gold  = self.gold
                    self.gold = self.shop.handle_click(
                        event.pos, is_open_click=False,
                        gold=self.gold, player=self.player
                    )
                    if self.gold < old_gold:
                        self.audio.play_sfx("buy")
                else:
                    result = self.floor.handle_click(event.pos, self.player)
                    if result:
                        self.audio.play_sfx("crit" if result["is_crit"] else "hit")
                        self.hit_markers.spawn(
                            event.pos,
                            "crit" if result["is_crit"] else "normal"
                        )
                        self.player.spawn_floating_text(
                            result["damage"], result["is_crit"],
                            self.floor.monster.rect.center
                        )
                        if result["killed"]:
                            self.audio.play_sfx("death")
                            self.gold += int(result["gold"] * self.player.gold_multiplier)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def _update(self):
        dt = self.clock.get_time() / 1000.0
        self.floor.update(dt)
        self.player.update(dt)
        self.player.update_floating_texts()
        self.menu.update()
        self.hit_markers.update(dt)

        if self.mode == "boss_raid":
            result = self.boss_room.update(dt)
            if result == "victory":
                self._handle_boss_victory()
            elif result == "defeat":
                self._handle_boss_defeat()

        elif self.mode == "quest":
            result = self.quest_room.update(dt)
            if result == "victory":
                self._handle_quest_victory()
            elif result == "defeat":
                self._handle_quest_defeat()

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def _draw(self):
        # ── Boss raid ────────────────────────────────────────────────────
        if self.mode == "boss_raid":
            self.boss_room.draw(self.screen, self.player)
            self.player.draw_floating_texts(self.screen)
            self.menu.draw_menu_button(self.screen)
            self.skill_bar.draw(self.screen, self.player)
            self.hit_markers.draw(self.screen)
            self.menu.draw_overlay(self.screen)
            pygame.display.flip()
            return

        # ── Quest ────────────────────────────────────────────────────────
        if self.mode == "quest":
            self.quest_room.draw(self.screen, self.player)
            self.player.draw_floating_texts(self.screen)
            self.menu.draw_menu_button(self.screen)
            self.skill_bar.draw(self.screen, self.player)
            self.hit_markers.draw(self.screen)
            self.menu.draw_overlay(self.screen)
            pygame.display.flip()
            return

        # ── Normal ───────────────────────────────────────────────────────
        self.floor.draw(self.screen)
        self.player.draw(self.screen)
        self.floor.draw_monster(self.screen)
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