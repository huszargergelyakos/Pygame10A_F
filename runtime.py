import random
import pygame
from settings import (
    FPS,
    LANE_POSITIONS,
    DISTANCE_PER_BIOME,
    SCREEN_HEIGHT,
    PG_K_A,
    PG_K_BACKSPACE,
    PG_K_C,
    PG_K_D,
    PG_KEYDOWN,
    PG_K_RETURN,
    PG_K_R,
    PG_K_S,
    PG_MOUSEBUTTONDOWN,
    PG_QUIT,
    PG_K_ESCAPE,
    PG_K_SPACE,
    PG_K_LEFT,
    PG_K_RIGHT,
    PG_ERROR,
    PG_QUIT_FN,
)
from objects import Obstacle, Coin, Fuel, Enemy


class GameRuntimeMixin:
    # Itt vannak a játék közben változó adatok.
    distance_meters = 0
    safe_lane_until_meter = 0
    safe_lane_span_m = 0
    cars_dodged = 0
    score = 0
    start_ticks = 0
    paused_total_ms = 0
    biome_counter = 0
    blocker_spawn_gap_timer = 0

    # Fő ciklus
    def run(self) -> None:
        # Ez a játék fő ismétlődő része.
        # Amíg fut a játék, ezt újra és újra végrehajtjuk.
        while self.running:
            self._check_events()
            if (
                self.screen_state == "playing"
                and not self.game_over
                and not self.paused
            ):
                self._handle_nitro()
                self._update()
            self._draw()
            self.clock.tick(FPS)

    # Bemenet és eseménykezelés
    def _check_events(self) -> None:
        # Itt kezeljük a kattintást, a billentyűket és a kilépést.
        for event in pygame.event.get():
            if event.type == PG_QUIT:
                self._quit_game()

            # Egér kattintásos részek.
            if event.type == PG_MOUSEBUTTONDOWN and event.button == 1:
                sound_rect = self._active_sound_button_rect()
                if sound_rect and sound_rect.collidepoint(event.pos):
                    self._toggle_sound()
                if (
                    self.screen_state == "playing"
                    and not self.game_over
                    and self.pause_menu_btn_rect.collidepoint(event.pos)
                ):
                    self._toggle_pause()
                if self.screen_state == "playing" and self.paused:
                    if self.pause_restart_rect.collidepoint(event.pos):
                        self.paused = False
                        self._reset_run()
                    elif self.pause_home_rect.collidepoint(event.pos):
                        self.paused = False
                        self._go_to_home()
                    elif self.pause_sound_rect.collidepoint(event.pos):
                        self._toggle_sound()
                    elif self.pause_resume_rect.collidepoint(event.pos):
                        self._toggle_pause()

            # Billentyűs részek.
            if event.type == PG_KEYDOWN:
                if self.screen_state == "home":
                    if event.key in (PG_K_RETURN, PG_K_SPACE):
                        self._start_game_from_home()
                    if event.key in (PG_K_C, PG_K_S):
                        self.screen_state = "select_car"
                    if event.key == PG_K_ESCAPE:
                        self._quit_game()
                elif self.screen_state == "select_car":
                    if event.key in (PG_K_RETURN, PG_K_SPACE):
                        self._start_game_from_home()
                    if event.key in (PG_K_ESCAPE, PG_K_BACKSPACE):
                        self.screen_state = "home"
                    if event.key in (PG_K_LEFT, PG_K_A):
                        self.selected_car_idx = (self.selected_car_idx - 1) % len(
                            self.car_options
                        )
                    if event.key in (PG_K_RIGHT, PG_K_D):
                        self.selected_car_idx = (self.selected_car_idx + 1) % len(
                            self.car_options
                        )
                elif self.game_over:
                    if event.key == PG_K_R:
                        self._reset_run()
                    if event.key == PG_K_ESCAPE:
                        self._quit_game()
                else:
                    if event.key == PG_K_ESCAPE:
                        self._toggle_pause()
                        continue
                    if self.paused:
                        continue
                    if event.key in (PG_K_LEFT, PG_K_A):
                        self.player.move_left()
                    if event.key in (PG_K_RIGHT, PG_K_D):
                        self.player.move_right()

    # Frame szintű szimuláció
    def _handle_nitro(self) -> None:
        # Szóköznél gyorsítunk, és közben fogy a nitro.
        # Ha elfogy, visszaáll a normál sebesség.
        keys = pygame.key.get_pressed()
        can_continue = self.is_nitro_active and self.nitro_gas > 0
        can_start = self.nitro_gas >= self.nitro_min_activation

        if keys[PG_K_SPACE] and (can_continue or can_start):
            self.speed = self.base_speed * 2
            self.nitro_gas = max(0.0, self.nitro_gas - self.nitro_drain_rate)
            self.is_nitro_active = True
            self.nitro_regen_delay_timer = self.nitro_regen_delay_frames
            if self.nitro_gas <= 0:
                self.speed = self.base_speed
                self.is_nitro_active = False
        else:
            self.speed = self.base_speed
            self.is_nitro_active = False

    def _update(self) -> None:
        # Egy körben minden mozgó adatot frissítünk.
        # Itt megy a mozgás, új tárgyak létrehozása, ütközés, háttér és pontok.
        # Várakozási idők kezelése.
        if self.nitro_regen_delay_timer > 0:
            self.nitro_regen_delay_timer -= 1
        if self.blocker_spawn_gap_timer > 0:
            self.blocker_spawn_gap_timer -= 1

        if not self.is_nitro_active and self.nitro_regen_delay_timer == 0:
            self.nitro_gas = min(100.0, self.nitro_gas + self.nitro_passive_rate)

        self.road.update(self.speed)
        self.player.update(self.is_nitro_active)
        self._handle_spawning()
        self._update_groups()
        self._check_collisions()
        self._scroll_background()
        self._update_stats()

    # Új tárgyak megjelenése
    def _handle_spawning(self) -> None:
        # Végigmegyünk a sávokon.
        # Ha letelt az idő, jöhet új tárgy.
        self._refresh_safe_lane_if_needed()
        for i in range(4):
            self.lane_cooldowns[i] -= self.speed
            if self.lane_cooldowns[i] <= 0:
                self._spawn_in_lane(i)

    def _spawn_in_lane(self, lane_idx: int) -> None:
        # Eldöntjük, mi jelenjen meg ebben a sávban.
        # Ebben benne van a véletlen is.
        if lane_idx == self.safe_lane_idx:
            # A biztonságos sávban inkább segítő tárgyak jönnek.
            safe_roll = random.random()
            if safe_roll < 0.30:
                self.coins.add(Coin(lane_idx))
                self.lane_cooldowns[lane_idx] = random.randint(100, 200)
            elif safe_roll < 0.38:
                self.fuels.add(Fuel(lane_idx))
                self.lane_cooldowns[lane_idx] = random.randint(260, 420)
            else:
                self.lane_cooldowns[lane_idx] = random.randint(70, 170)
            return

        difficulty = self._distance_difficulty()
        # Ahogy megyünk előre, nehezebb lesz a játék.
        enemy_threshold = 0.09 + (0.16 * difficulty)
        obstacle_threshold = enemy_threshold + (0.09 + (0.20 * difficulty))

        r = random.random()
        can_spawn_blocker_now = self.blocker_spawn_gap_timer == 0

        # Döntés, hogy mi jöjjön: ellenfél, akadály vagy segítő tárgy.
        if r < enemy_threshold:
            if self._can_spawn_blocker_in_lane(lane_idx) and can_spawn_blocker_now:
                self.enemies.add(Enemy(lane_idx))
                self.lane_cooldowns[lane_idx] = self._scaled_cooldown(
                    420, 620, difficulty
                )
                self.blocker_spawn_gap_timer = self.blocker_spawn_gap_frames
            else:
                self.coins.add(Coin(lane_idx))
                self.lane_cooldowns[lane_idx] = self._scaled_cooldown(
                    120, 230, difficulty
                )
        elif r < obstacle_threshold:
            can_add_obstacle = (
                self._obstacle_count_in_window() < self.max_obstacles_in_window
            )
            if (
                self._can_spawn_blocker_in_lane(lane_idx)
                and can_add_obstacle
                and can_spawn_blocker_now
            ):
                self.obstacles.add(
                    Obstacle(random.choice(["roadblock", "barrel"]), lane_idx)
                )
                self.lane_cooldowns[lane_idx] = self._scaled_cooldown(
                    260, 420, difficulty
                )
                self.blocker_spawn_gap_timer = self.blocker_spawn_gap_frames
            else:
                self.fuels.add(Fuel(lane_idx))
                self.lane_cooldowns[lane_idx] = self._scaled_cooldown(
                    220, 360, difficulty
                )
        elif r < obstacle_threshold + 0.12:
            self.coins.add(Coin(lane_idx))
            self.lane_cooldowns[lane_idx] = self._scaled_cooldown(100, 210, difficulty)
        elif r < obstacle_threshold + 0.17:
            self.fuels.add(Fuel(lane_idx))
            self.lane_cooldowns[lane_idx] = self._scaled_cooldown(400, 720, difficulty)
        else:
            self.lane_cooldowns[lane_idx] = self._scaled_cooldown(60, 170, difficulty)

    def _distance_difficulty(self) -> float:
        # A megtett útból számolunk egy nehézség értéket.
        return min(1.0, self.distance_meters / 4000.0)

    def _scaled_cooldown(self, min_cd: int, max_cd: int, difficulty: float) -> int:
        # Nehezebb játéknál rövidebb várakozási időt ad.
        scale = 1.0 - (0.35 * difficulty)
        scaled_min = max(35, int(min_cd * scale))
        scaled_max = max(scaled_min + 10, int(max_cd * scale))
        return random.randint(scaled_min, scaled_max)

    def _lane_from_x(self, x_pos: int) -> int:
        # Megmondja, melyik sáv van legközelebb az adott x ponthoz.
        return min(
            range(len(LANE_POSITIONS)), key=lambda idx: abs(LANE_POSITIONS[idx] - x_pos)
        )

    def _refresh_safe_lane_if_needed(self) -> None:
        # Néha új biztonságos sávot választunk.
        # Így marad esély kikerülni az akadályokat.
        if self.distance_meters < self.safe_lane_until_meter:
            return

        prev_safe_lane_idx = self.safe_lane_idx
        candidate_lanes = [
            idx for idx in range(len(LANE_POSITIONS)) if idx != prev_safe_lane_idx
        ]

        clear_candidates = [
            idx for idx in candidate_lanes if self._lane_blocker_count_ahead(idx) == 0
        ]
        adjacent_candidates = [
            idx for idx in clear_candidates if abs(idx - self.player.lane_idx) <= 1
        ]

        if self.player.lane_idx in clear_candidates:
            self.safe_lane_idx = self.player.lane_idx
        elif adjacent_candidates:
            self.safe_lane_idx = random.choice(adjacent_candidates)
        elif clear_candidates:
            self.safe_lane_idx = random.choice(clear_candidates)
        else:
            self.safe_lane_idx = min(
                candidate_lanes, key=self._lane_blocker_count_ahead
            )

        self.safe_lane_until_meter = self.distance_meters + self.safe_lane_span_m

    def _lane_blocker_count_ahead(self, lane_idx: int) -> int:
        # Megszámolja, mennyi veszélyes dolog van egy sávban előttünk.
        top_limit = self.player.rect.top - self.safe_lane_clear_px
        bottom_limit = self.player.rect.bottom + 80
        count = 0

        for sprite in list(self.obstacles) + list(self.enemies):
            sprite_lane = self._lane_from_x(sprite.rect.centerx)
            if sprite_lane != lane_idx:
                continue
            if top_limit <= sprite.rect.centery <= bottom_limit:
                count += 1

        return count

    def _obstacle_count_in_window(self) -> int:
        # Megszámolja a közeli akadályokat.
        # Ezzel elkerüljük, hogy túl sok legyen egyszerre.
        top_limit = self.player.rect.top - self.obstacle_window_px
        bottom_limit = self.player.rect.top
        count = 0
        for obstacle in self.obstacles:
            if top_limit <= obstacle.rect.centery <= bottom_limit:
                count += 1
        return count

    def _can_spawn_blocker_in_lane(self, lane_idx: int) -> bool:
        # Ellenőrzi, hogy marad-e még járható sáv.
        blocked_lanes = self._blocked_lanes_in_critical_window()
        blocked_after_spawn = blocked_lanes | {lane_idx}

        if len(blocked_after_spawn) > 2:
            return False

        reachable_lanes = {
            idx
            for idx in range(len(LANE_POSITIONS))
            if abs(idx - self.player.lane_idx) <= 1
        }
        free_reachable = reachable_lanes - blocked_after_spawn
        return len(free_reachable) > 0

    def _blocked_lanes_in_critical_window(self) -> set[int]:
        # Összegyűjti, melyik sávok vannak tele veszéllyel.
        blocked_lanes: set[int] = set()
        danger_top = self.player.rect.top - self.critical_window_px
        danger_bottom = self.player.rect.bottom + 120

        for sprite in list(self.obstacles) + list(self.enemies):
            if danger_top <= sprite.rect.centery <= danger_bottom:
                blocked_lanes.add(self._lane_from_x(sprite.rect.centerx))

        return blocked_lanes

    # Objektum frissítés és ütközések
    def _update_groups(self) -> None:
        # Frissítjük az összes csoportot.
        # Számoljuk, hány ellenség ment ki a képről.
        self.obstacles.update(self.speed)
        self.coins.update(self.speed)
        self.fuels.update(self.speed)
        prev_enemies = set(self.enemies.sprites())
        self.enemies.update(self.speed + 2)

        gone_enemies = [enemy for enemy in prev_enemies if enemy not in self.enemies]
        self.cars_dodged += len(gone_enemies)

    def _check_collisions(self) -> None:
        # Ütközések kezelése.
        # Ha akadályba megyünk: vége a körnek.
        # Ha pénzt veszünk fel: nő a pont.
        # Ha benzint veszünk fel: nő a nitro.
        if pygame.sprite.spritecollide(
            self.player, self.obstacles, False, self._hitbox_collide
        ) or pygame.sprite.spritecollide(
            self.player, self.enemies, False, self._hitbox_collide
        ):
            self.game_over = True
            self.speed = 0

        if pygame.sprite.spritecollide(self.player, self.coins, True):
            self.score += 1
            self._play_sfx(self.coin_sound)

        if pygame.sprite.spritecollide(self.player, self.fuels, True):
            self.nitro_gas = min(100.0, self.nitro_gas + 25.0)
            self._play_sfx(self.fuel_sound)

    def _hitbox_collide(
        self, player_sprite: pygame.sprite.Sprite, obj_sprite: pygame.sprite.Sprite
    ) -> bool:
        # Ütközést nézünk a kisebb találati dobozokkal.
        player_hitbox = getattr(player_sprite, "hitbox", player_sprite.rect)
        obj_hitbox = getattr(obj_sprite, "hitbox", obj_sprite.rect)
        return player_hitbox.colliderect(obj_hitbox)

    # Háttér görgetés és progresszió
    def _scroll_background(self) -> None:
        # A két háttérkép lefele mozog.
        # Ettől folyamatosnak látszik a haladás.
        self.bg1_y += self.speed
        self.bg2_y += self.speed
        if self.bg1_y >= SCREEN_HEIGHT:
            self.bg1_y = self.bg2_y - SCREEN_HEIGHT + 1
            self.bg1_surf = self.bg_surfaces[self.next_biome_idx]
        if self.bg2_y >= SCREEN_HEIGHT:
            self.bg2_y = self.bg1_y - SCREEN_HEIGHT + 1
            self.bg2_surf = self.bg_surfaces[self.next_biome_idx]

    def _update_stats(self) -> None:
        # Frissíti az adatokat: táv, idő, háttér számláló.
        self.distance_meters += self.speed // 2
        active_ms = pygame.time.get_ticks() - self.start_ticks - self.paused_total_ms
        self.elapsed_time = max(0, active_ms // 1000)
        computed_idx = (self.distance_meters // DISTANCE_PER_BIOME) % len(
            self.bg_surfaces
        )
        if computed_idx != self.current_biome_idx:
            self.current_biome_idx = computed_idx
            self.biome_counter += 1
        self.next_biome_idx = computed_idx

    # Játék állapot váltás
    def _toggle_pause(self) -> None:
        # Szünet be/ki.
        # Közben mérjük a szünet idejét.
        if self.screen_state != "playing" or self.game_over:
            return
        self.paused = not self.paused
        if self.paused:
            self.pause_started_ticks = pygame.time.get_ticks()
        elif self.pause_started_ticks is not None:
            self.paused_total_ms += pygame.time.get_ticks() - self.pause_started_ticks
            self.pause_started_ticks = None

    def _quit_game(self) -> None:
        # Kilépés a játékból.
        self.running = False
        try:
            pygame.mixer.music.stop()
        except PG_ERROR:
            pass
        PG_QUIT_FN()
