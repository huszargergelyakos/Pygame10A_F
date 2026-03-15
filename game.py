import random
import math
import pygame
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    WHITE,
    DISTANCE_PER_BIOME,
    LANE_POSITIONS,
)
from road import Road
from player import Player
from objects import Obstacle, Coin, Fuel, Enemy  # Új import: Enemy
from ui import Button


class Game:
    def __init__(self) -> None:
        flags = pygame.DOUBLEBUF
        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT), flags, vsync=1
        )
        pygame.display.set_caption("Highway Dodge")
        self.clock = pygame.time.Clock()
        self._init_menu_state()
        self._init_variables()
        self._init_objects()

    def _init_menu_state(self) -> None:
        self.screen_state = "home"
        self.car_options = [f"Assets/cars/{i}.png" for i in range(1, 14)]
        self.selected_car_idx = 0

        self.home_bg = self._load_optional_image(
            "Assets/home.png", (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        self.home_title_font = pygame.font.SysFont("Arial", 64, bold=True)
        self.home_info_font = pygame.font.SysFont("Arial", 30, bold=True)

        self.play_button = Button(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 115,
            "Assets/buttons/play.png",
            0.72,
        )

        arrow_img = self._load_optional_image("Assets/buttons/arrow.png", (78, 78))
        self.arrow_right_img = arrow_img
        self.arrow_left_img = (
            pygame.transform.flip(arrow_img, True, False) if arrow_img else None
        )
        self.arrow_left_rect = pygame.Rect(130, SCREEN_HEIGHT // 2 - 10, 78, 78)
        self.arrow_right_rect = pygame.Rect(
            SCREEN_WIDTH - 208, SCREEN_HEIGHT // 2 - 10, 78, 78
        )
        self._mouse_prev_down = False

        self.car_preview_surfaces: list[pygame.Surface] = []
        for car_path in self.car_options:
            car_img = pygame.image.load(car_path).convert_alpha()
            self.car_preview_surfaces.append(
                pygame.transform.smoothscale(car_img, (170, 320))
            )

    def _init_variables(self) -> None:
        self.running, self.base_speed = True, 5
        self.speed = self.base_speed
        self.distance_meters, self.elapsed_time = 0, 0
        self.score, self.nitro_gas = 0, 0.0
        self.cars_dodged = 0
        self.nitro_passive_rate = 3.2 / FPS
        self.nitro_drain_rate = 0.60
        self.nitro_min_activation = 5.0
        self.nitro_regen_delay_timer = 0
        self.nitro_regen_delay_frames = int(0.25 * FPS)
        self.game_over = False
        self.lane_cooldowns = [0, 0, 0, 0]
        self.safe_lane_idx = random.randint(0, len(LANE_POSITIONS) - 1)
        self.safe_lane_span_m = 100
        self.safe_lane_until_meter = self.safe_lane_span_m
        self.safe_lane_clear_px = 260
        self.obstacle_window_px = 420
        self.max_obstacles_in_window = 3
        self.critical_window_px = 360
        self.start_ticks = pygame.time.get_ticks()
        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.game_over_title_font = pygame.font.SysFont("Arial", 64, bold=True)
        self.game_over_stat_font = pygame.font.SysFont("Arial", 46, bold=True)
        self.bg_surfaces = [self._load_bg(i) for i in [2, 5, 4, 3, 8, 1, 7, 6]]
        self.next_biome_idx = 0
        self.is_nitro_active = False
        self.nitro_icon = self._load_nitro_icon()
        self.game_over_main_bg = self._load_optional_image(
            "Assets/end.jpg", (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        self.game_over_logo = self._load_optional_image(
            "Assets/game_over.png", (560, 270)
        )
        self.coin_stat_icon = self._load_optional_image("Assets/coins/1.png", (54, 54))
        self.car_stat_icon = self._load_optional_image(
            "Assets/car_dodge.png", (108, 46)
        )
        self.replay_button = Button(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 96, "Assets/buttons/replay.png", 0.30
        )
        self.home_button = Button(
            SCREEN_WIDTH // 2 - 110,
            SCREEN_HEIGHT - 96,
            "Assets/buttons/home.png",
            0.28,
        )

    def _init_objects(self) -> None:
        self.road = Road("Assets/road.png")
        self.player = Player(
            SCREEN_HEIGHT - 150, self.car_options[self.selected_car_idx]
        )
        self.obstacles = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.fuels = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()  # Új csoport

        self.bg1_surf = self.bg_surfaces[0]
        self.bg2_surf = self.bg_surfaces[0]
        self.bg1_y, self.bg2_y = 0, -SCREEN_HEIGHT

    def _load_bg(self, index: int) -> pygame.Surface:
        return pygame.transform.scale(
            pygame.image.load(f"Assets/backgrounds/{index}.jpg").convert(),
            (SCREEN_WIDTH, SCREEN_HEIGHT),
        )

    def _load_optional_image(
        self, path: str, size: tuple[int, int] | None = None
    ) -> pygame.Surface | None:
        try:
            raw_img = pygame.image.load(path)
            if raw_img.get_alpha() is not None:
                img = raw_img.convert_alpha()
            else:
                img = raw_img.convert()
            if size is not None:
                return pygame.transform.smoothscale(img, size)
            return img
        except (pygame.error, FileNotFoundError):
            return None

    def _load_nitro_icon(self) -> pygame.Surface | None:
        for icon_path in [
            "Assets/nitro/nitro.png",
            "Assets/nitro/0.gif",
            "Assets/nitro/1.gif",
            "Assets/nitro/2.gif",
            "Assets/nitro.png",
            "nitro.png",
        ]:
            try:
                icon = pygame.image.load(icon_path).convert_alpha()
                return pygame.transform.smoothscale(icon, (54, 54))
            except (pygame.error, FileNotFoundError):
                continue
        return None

    def run(self) -> None:
        while self.running:
            self._check_events()
            if self.screen_state == "playing" and not self.game_over:
                self._handle_nitro()
                self._update()
            self._draw()
            self.clock.tick(FPS)

    def _handle_nitro(self) -> None:
        keys = pygame.key.get_pressed()

        can_continue = self.is_nitro_active and self.nitro_gas > 0
        can_start = self.nitro_gas >= self.nitro_min_activation

        if keys[pygame.K_SPACE] and (can_continue or can_start):
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
        if self.nitro_regen_delay_timer > 0:
            self.nitro_regen_delay_timer -= 1

        if not self.is_nitro_active and self.nitro_regen_delay_timer == 0:
            self.nitro_gas = min(100.0, self.nitro_gas + self.nitro_passive_rate)

        self.road.update(self.speed)
        self.player.update(self.is_nitro_active)
        self._handle_spawning()
        self._update_groups()
        self._check_collisions()
        self._scroll_background()
        self._update_stats()

    def _handle_spawning(self) -> None:
        self._refresh_safe_lane_if_needed()
        for i in range(4):
            self.lane_cooldowns[i] -= self.speed
            if self.lane_cooldowns[i] <= 0:
                self._spawn_in_lane(i)

    def _spawn_in_lane(self, lane_idx: int) -> None:
        if lane_idx == self.safe_lane_idx:
            # A safe lane-en nem spawnolhat blocker vagy enemy a következő 100m-en.
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
        enemy_threshold = 0.08 + (0.14 * difficulty)
        obstacle_threshold = enemy_threshold + (0.08 + (0.18 * difficulty))

        r = random.random()
        if r < enemy_threshold:
            if self._can_spawn_blocker_in_lane(lane_idx):
                self.enemies.add(Enemy(lane_idx))
                self.lane_cooldowns[lane_idx] = self._scaled_cooldown(
                    420, 620, difficulty
                )
            else:
                self.coins.add(Coin(lane_idx))
                self.lane_cooldowns[lane_idx] = self._scaled_cooldown(
                    120, 230, difficulty
                )
        elif r < obstacle_threshold:
            can_add_obstacle = (
                self._obstacle_count_in_window() < self.max_obstacles_in_window
            )
            if self._can_spawn_blocker_in_lane(lane_idx) and can_add_obstacle:
                self.obstacles.add(
                    Obstacle(random.choice(["roadblock", "barrel"]), lane_idx)
                )
                self.lane_cooldowns[lane_idx] = self._scaled_cooldown(
                    260, 420, difficulty
                )
            else:
                self.fuels.add(Fuel(lane_idx))
                self.lane_cooldowns[lane_idx] = self._scaled_cooldown(
                    220, 360, difficulty
                )
        elif r < obstacle_threshold + 0.14:
            self.coins.add(Coin(lane_idx))
            self.lane_cooldowns[lane_idx] = self._scaled_cooldown(100, 210, difficulty)
        elif r < obstacle_threshold + 0.19:
            self.fuels.add(Fuel(lane_idx))
            self.lane_cooldowns[lane_idx] = self._scaled_cooldown(400, 720, difficulty)
        else:
            self.lane_cooldowns[lane_idx] = self._scaled_cooldown(60, 170, difficulty)

    def _distance_difficulty(self) -> float:
        # 0.0 -> indulás, 1.0 -> kb 4000m után max nehézség.
        return min(1.0, self.distance_meters / 4000.0)

    def _scaled_cooldown(self, min_cd: int, max_cd: int, difficulty: float) -> int:
        # Ahogy nő a nehézség, rövidebb cooldown -> gyakoribb spawn.
        scale = 1.0 - (0.35 * difficulty)
        scaled_min = max(35, int(min_cd * scale))
        scaled_max = max(scaled_min + 10, int(max_cd * scale))
        return random.randint(scaled_min, scaled_max)

    def _lane_from_x(self, x_pos: int) -> int:
        return min(
            range(len(LANE_POSITIONS)), key=lambda idx: abs(LANE_POSITIONS[idx] - x_pos)
        )

    def _refresh_safe_lane_if_needed(self) -> None:
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

        # A safe lane soha ne maradjon ugyanaz, és lehetőleg ténylegesen tiszta legyen.
        if self.player.lane_idx in clear_candidates:
            self.safe_lane_idx = self.player.lane_idx
        elif adjacent_candidates:
            self.safe_lane_idx = random.choice(adjacent_candidates)
        elif clear_candidates:
            self.safe_lane_idx = random.choice(clear_candidates)
        else:
            # Ha minden lane-ben van blocker, akkor a legkevésbé telítettből választunk.
            self.safe_lane_idx = min(
                candidate_lanes, key=lambda idx: self._lane_blocker_count_ahead(idx)
            )

        self.safe_lane_until_meter = self.distance_meters + self.safe_lane_span_m

    def _lane_blocker_count_ahead(self, lane_idx: int) -> int:
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
        top_limit = self.player.rect.top - self.obstacle_window_px
        bottom_limit = self.player.rect.top
        count = 0
        for obstacle in self.obstacles:
            if top_limit <= obstacle.rect.centery <= bottom_limit:
                count += 1
        return count

    def _can_spawn_blocker_in_lane(self, lane_idx: int) -> bool:
        blocked_lanes = self._blocked_lanes_in_critical_window()
        blocked_after_spawn = blocked_lanes | {lane_idx}

        # Kritikus zónában legfeljebb 2 lane legyen blokkolt.
        if len(blocked_after_spawn) > 2:
            return False

        # Maradjon legalább egy a játékos számára gyorsan elérhető lane.
        reachable_lanes = {
            idx
            for idx in range(len(LANE_POSITIONS))
            if abs(idx - self.player.lane_idx) <= 1
        }
        free_reachable = reachable_lanes - blocked_after_spawn
        return len(free_reachable) > 0

    def _blocked_lanes_in_critical_window(self) -> set[int]:
        blocked_lanes: set[int] = set()
        danger_top = self.player.rect.top - self.critical_window_px
        danger_bottom = self.player.rect.bottom + 120

        for sprite in list(self.obstacles) + list(self.enemies):
            if danger_top <= sprite.rect.centery <= danger_bottom:
                blocked_lanes.add(self._lane_from_x(sprite.rect.centerx))

        return blocked_lanes

    def _update_groups(self) -> None:
        self.obstacles.update(self.speed)
        self.coins.update(self.speed)
        self.fuels.update(self.speed)
        prev_enemies = set(self.enemies.sprites())
        self.enemies.update(self.speed + 2)  # Az ellenfelek picit gyorsabbak
        gone_enemies = [enemy for enemy in prev_enemies if enemy not in self.enemies]
        self.cars_dodged += len(gone_enemies)

    def _check_collisions(self) -> None:
        # Ütközés ellenséggel vagy akadállyal
        if pygame.sprite.spritecollide(
            self.player, self.obstacles, False, self._hitbox_collide
        ) or pygame.sprite.spritecollide(
            self.player, self.enemies, False, self._hitbox_collide
        ):
            self.game_over = True
            self.speed = 0

        if pygame.sprite.spritecollide(self.player, self.coins, True):
            self.score += 1

        if pygame.sprite.spritecollide(self.player, self.fuels, True):
            self.nitro_gas = min(100.0, self.nitro_gas + 25.0)

    def _hitbox_collide(
        self, player_sprite: pygame.sprite.Sprite, obj_sprite: pygame.sprite.Sprite
    ) -> bool:
        player_hitbox = getattr(player_sprite, "hitbox", player_sprite.rect)
        obj_hitbox = getattr(obj_sprite, "hitbox", obj_sprite.rect)
        return player_hitbox.colliderect(obj_hitbox)

    def _scroll_background(self) -> None:
        self.bg1_y += self.speed
        self.bg2_y += self.speed
        if self.bg1_y >= SCREEN_HEIGHT:
            self.bg1_y = self.bg2_y - SCREEN_HEIGHT + 1
            self.bg1_surf = self.bg_surfaces[self.next_biome_idx]
        if self.bg2_y >= SCREEN_HEIGHT:
            self.bg2_y = self.bg1_y - SCREEN_HEIGHT + 1
            self.bg2_surf = self.bg_surfaces[self.next_biome_idx]

    def _update_stats(self) -> None:
        self.distance_meters += self.speed // 2
        self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) // 1000
        self.next_biome_idx = (self.distance_meters // DISTANCE_PER_BIOME) % len(
            self.bg_surfaces
        )

    def _draw(self) -> None:
        if self.screen_state == "home":
            self._draw_home()
            pygame.display.update()
            return

        self.screen.blit(self.bg1_surf, (0, self.bg1_y))
        self.screen.blit(self.bg2_surf, (0, self.bg2_y))
        self.road.draw(self.screen)
        self.player.draw(self.screen)
        self.obstacles.draw(self.screen)
        self.coins.draw(self.screen)
        self.fuels.draw(self.screen)
        self.enemies.draw(self.screen)
        self._draw_hud()
        if self.game_over:
            self._draw_game_over()
        pygame.display.update()

    def _draw_home(self) -> None:
        if self.home_bg:
            self.screen.blit(self.home_bg, (0, 0))
        else:
            self.screen.fill((22, 20, 40))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 70))
        self.screen.blit(overlay, (0, 0))

        title = self.home_title_font.render("HIGHWAY DODGE", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 100)))

        preview = self.car_preview_surfaces[self.selected_car_idx]
        preview_rect = preview.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 5)
        )
        panel = pygame.Rect(0, 0, 270, 390)
        panel.center = preview_rect.center
        panel_surf = pygame.Surface(panel.size, pygame.SRCALPHA)
        panel_surf.fill((8, 8, 18, 145))
        self.screen.blit(panel_surf, panel.topleft)
        self.screen.blit(preview, preview_rect)

        mouse_pressed = pygame.mouse.get_pressed()[0] == 1
        click_started = mouse_pressed and not self._mouse_prev_down
        mouse_pos = pygame.mouse.get_pos()

        if self.arrow_left_img:
            self.screen.blit(self.arrow_left_img, self.arrow_left_rect)
            if click_started and self.arrow_left_rect.collidepoint(mouse_pos):
                self.selected_car_idx = (self.selected_car_idx - 1) % len(
                    self.car_options
                )

        if self.arrow_right_img:
            self.screen.blit(self.arrow_right_img, self.arrow_right_rect)
            if click_started and self.arrow_right_rect.collidepoint(mouse_pos):
                self.selected_car_idx = (self.selected_car_idx + 1) % len(
                    self.car_options
                )

        self._mouse_prev_down = mouse_pressed

        car_label = self.home_info_font.render(
            f"Selected Car: {self.selected_car_idx + 1}/13", True, WHITE
        )
        self.screen.blit(
            car_label,
            car_label.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 205)),
        )

        if self.play_button.draw(self.screen):
            self._start_game_from_home()

    def _draw_game_over(self) -> None:
        if self.game_over_main_bg:
            self.screen.blit(self.game_over_main_bg, (0, 0))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 95))
        self.screen.blit(overlay, (0, 0))

        if self.game_over_logo:
            logo_rect = self.game_over_logo.get_rect(center=(SCREEN_WIDTH // 2, 150))
            self.screen.blit(self.game_over_logo, logo_rect)
        else:
            title = self.game_over_title_font.render("GAME OVER", True, (255, 80, 80))
            self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 150)))

        coin_y = 320
        car_y = 415
        time_y = 510
        dist_y = 600

        if self.coin_stat_icon:
            self.screen.blit(
                self.coin_stat_icon, (SCREEN_WIDTH // 2 - 155, coin_y - 22)
            )
        if self.car_stat_icon:
            self.screen.blit(self.car_stat_icon, (SCREEN_WIDTH // 2 - 175, car_y - 12))

        coins_txt = self.game_over_stat_font.render(str(self.score), True, WHITE)
        cars_txt = self.game_over_stat_font.render(str(self.cars_dodged), True, WHITE)
        time_txt = self.game_over_stat_font.render(
            f"Time : {self.elapsed_time}s", True, WHITE
        )
        dist_km = self.distance_meters / 1000.0
        dist_txt = self.game_over_stat_font.render(
            f"Distance : {dist_km:.2f} km", True, WHITE
        )

        self.screen.blit(coins_txt, (SCREEN_WIDTH // 2 + 30, coin_y - 13))
        self.screen.blit(cars_txt, (SCREEN_WIDTH // 2 + 30, car_y - 13))
        self.screen.blit(
            time_txt, time_txt.get_rect(center=(SCREEN_WIDTH // 2, time_y))
        )
        self.screen.blit(
            dist_txt, dist_txt.get_rect(center=(SCREEN_WIDTH // 2, dist_y))
        )

        if self.replay_button.draw(self.screen):
            self._reset_run()
        if self.home_button.draw(self.screen):
            self._go_to_home()

        hint = self.font.render("R = újraindítás, ESC = kilépés", True, WHITE)
        self.screen.blit(
            hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
        )

    def _reset_run(self) -> None:
        self._init_variables()
        self._init_objects()
        self.screen_state = "playing"

    def _start_game_from_home(self) -> None:
        self._reset_run()

    def _go_to_home(self) -> None:
        self._init_variables()
        self._init_objects()
        self.screen_state = "home"

    def _draw_hud(self) -> None:
        box = pygame.Surface((180, 105), pygame.SRCALPHA)
        box.fill((0, 0, 0, 180))
        self.screen.blit(box, (10, 20))
        stats = [
            f"{self.distance_meters} m",
            f"Coins: {self.score}",
            f"Time: {self.elapsed_time}s",
        ]
        for i, text in enumerate(stats):
            self.screen.blit(self.font.render(text, True, WHITE), (20, 30 + i * 25))

        center = (SCREEN_WIDTH - 82, SCREEN_HEIGHT - 98)
        radius = 44
        gauge_bg = pygame.Surface((130, 130), pygame.SRCALPHA)
        pygame.draw.circle(gauge_bg, (0, 0, 0, 165), (65, 65), 57)
        self.screen.blit(gauge_bg, (center[0] - 65, center[1] - 65))

        if self.is_nitro_active:
            glow_surf = pygame.Surface((170, 170), pygame.SRCALPHA)
            pulse = 85 + int(40 * (1 + math.sin(pygame.time.get_ticks() * 0.02)) / 2)
            pygame.draw.circle(glow_surf, (255, 140, 0, pulse), (85, 85), 62, 16)
            pygame.draw.circle(glow_surf, (255, 170, 60, pulse // 2), (85, 85), 70, 10)
            self.screen.blit(glow_surf, (center[0] - 85, center[1] - 85))

        ring_rect = pygame.Rect(0, 0, radius * 2, radius * 2)
        ring_rect.center = center
        border_color = (255, 170, 60) if self.is_nitro_active else (255, 135, 45)
        track_color = (70, 30, 0) if self.is_nitro_active else (40, 40, 40)
        arc_color = (255, 130, 0) if self.is_nitro_active else (255, 190, 40)
        pygame.draw.circle(self.screen, border_color, center, radius, 3)
        pygame.draw.circle(self.screen, track_color, center, radius, 8)
        fill_ratio = self.nitro_gas / 100.0
        start_angle = -math.pi / 2
        end_angle = start_angle + (2 * math.pi * fill_ratio)
        pygame.draw.arc(
            self.screen,
            arc_color,
            ring_rect,
            start_angle,
            end_angle,
            8,
        )

        if self.nitro_icon:
            icon_rect = self.nitro_icon.get_rect(center=center)
            self.screen.blit(self.nitro_icon, icon_rect)
        else:
            fallback = self.font.render("N2O", True, WHITE)
            self.screen.blit(fallback, fallback.get_rect(center=center))

        nitro_label = self.font.render(f"{int(self.nitro_gas)}%", True, WHITE)
        self.screen.blit(
            nitro_label, nitro_label.get_rect(center=(center[0], center[1] + 58))
        )

    def _check_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit_game()
            if event.type == pygame.KEYDOWN:
                if self.screen_state == "home":
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self._start_game_from_home()
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        self.selected_car_idx = (self.selected_car_idx - 1) % len(
                            self.car_options
                        )
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.selected_car_idx = (self.selected_car_idx + 1) % len(
                            self.car_options
                        )
                elif self.game_over:
                    if event.key == pygame.K_r:
                        self._reset_run()
                    if event.key == pygame.K_ESCAPE:
                        self._quit_game()
                else:
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        self.player.move_left()
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.player.move_right()

    def _quit_game(self) -> None:
        self.running = False
        pygame.quit()


if __name__ == "__main__":
    pygame.init()
    Game().run()
