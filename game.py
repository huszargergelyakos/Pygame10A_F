# type: ignore
import random
import pygame
from typing import Any
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    DISTANCE_PER_BIOME,
    LANE_POSITIONS,
)
from road import Road
from player import Player
from objects import Obstacle, Coin, Fuel, Enemy
from game_ui import GameUIMixin

PG_DOUBLEBUF = int(getattr(pygame, "DOUBLEBUF", 0))
PG_QUIT = int(getattr(pygame, "QUIT", 0))
PG_MOUSEBUTTONDOWN = int(getattr(pygame, "MOUSEBUTTONDOWN", 0))
PG_KEYDOWN = int(getattr(pygame, "KEYDOWN", 0))
PG_K_SPACE = int(getattr(pygame, "K_SPACE", 0))
PG_K_RETURN = int(getattr(pygame, "K_RETURN", 0))
PG_K_C = int(getattr(pygame, "K_c", 0))
PG_K_S = int(getattr(pygame, "K_s", 0))
PG_K_ESCAPE = int(getattr(pygame, "K_ESCAPE", 0))
PG_K_BACKSPACE = int(getattr(pygame, "K_BACKSPACE", 0))
PG_K_LEFT = int(getattr(pygame, "K_LEFT", 0))
PG_K_A = int(getattr(pygame, "K_a", 0))
PG_K_RIGHT = int(getattr(pygame, "K_RIGHT", 0))
PG_K_D = int(getattr(pygame, "K_d", 0))
PG_K_R = int(getattr(pygame, "K_r", 0))
PG_ERROR: Any = getattr(pygame, "error", RuntimeError)
PG_INIT = getattr(pygame, "init", lambda: None)
PG_QUIT_FN = getattr(pygame, "quit", lambda: None)


class Game(GameUIMixin):
    def __init__(self) -> None:
        self.running = False
        self.base_speed = 0
        self.speed = 0
        self.distance_meters = 0
        self.elapsed_time = 0
        self.score = 0
        self.nitro_gas = 0.0
        self.nitro_regen_delay_timer = 0
        self.game_over = False
        self.paused = False
        self.pause_started_ticks = None
        self.paused_total_ms = 0
        self.safe_lane_idx = 0
        self.safe_lane_until_meter = 0
        self.blocker_spawn_gap_timer = 0
        self.current_biome_idx = 0
        self.next_biome_idx = 0
        self.biome_counter = 0
        self.is_nitro_active = False
        self.bg1_surf = None
        self.bg2_surf = None
        self.bg1_y = 0
        self.bg2_y = 0
        self.sound_on = True
        self.screen_state = "home"
        self.selected_car_idx = 0

        flags = PG_DOUBLEBUF
        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT), flags, vsync=1
        )
        pygame.display.set_caption("Highway Dodge")
        self.clock = pygame.time.Clock()
        self._init_audio_state()
        self._init_menu_state()
        self._init_variables()
        self._init_objects()

    def _init_audio_state(self) -> None:
        self.sound_on = True
        self.music_volume = 0.35
        self.sfx_volume = 0.50

        self.music_path = "Sounds/mixkit-tech-house-vibes-130.mp3"
        self.coin_sound = self._load_optional_sound("Sounds/coin.mp3")
        self.fuel_sound = self._load_optional_sound("Sounds/fuel.wav")
        self.click_sound = self._load_optional_sound("Sounds/click.mp3")

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(self.music_path)
            pygame.mixer.music.play(-1)
        except (PG_ERROR, FileNotFoundError):
            pass

        self._apply_audio_state()

    def _init_menu_state(self) -> None:
        self.screen_state = "home"
        self.car_options = [f"Assets/cars/{i}.png" for i in range(1, 14)]
        self.selected_car_idx = 0
        self.menu_fonts: dict[int, pygame.font.Font] = {}

        self.home_bg = self._load_optional_image(
            "Assets/home.png", (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        self.home_title_font = self._get_menu_font(64)
        self.home_info_font = self._get_menu_font(28)

        menu_w = 360
        menu_h = 68
        menu_x = (SCREEN_WIDTH - menu_w) // 2
        menu_start_y = 220
        menu_gap = 24
        self.home_play_rect = pygame.Rect(menu_x, menu_start_y, menu_w, menu_h)
        self.home_select_rect = pygame.Rect(
            menu_x, menu_start_y + menu_h + menu_gap, menu_w, menu_h
        )
        self.home_quit_rect = pygame.Rect(
            menu_x, menu_start_y + (menu_h + menu_gap) * 2, menu_w, menu_h
        )
        self.home_selected_rect = pygame.Rect(
            menu_x + 26, self.home_quit_rect.bottom + 18, menu_w - 52, 54
        )

        self.sound_on_img = self._load_optional_image(
            "Assets/buttons/soundOn.png", (54, 54)
        )
        self.sound_off_img = self._load_optional_image(
            "Assets/buttons/soundOff.png", (54, 54)
        )
        self.pause_menu_btn_rect = pygame.Rect(SCREEN_WIDTH - 164, 18, 146, 54)
        self.sound_btn_end_rect = pygame.Rect(
            SCREEN_WIDTH // 2 + 104, SCREEN_HEIGHT - 126, 62, 62
        )

        self.select_play_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT - 115, 190, 62
        )
        self.select_back_rect = pygame.Rect(
            SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT - 115, 190, 62
        )

        arrow_img = self._load_optional_image("Assets/buttons/arrow.png", (78, 78))
        self.arrow_left_img = arrow_img
        self.arrow_right_img = (
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

        panel_w, panel_h = 360, 340
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = (SCREEN_HEIGHT - panel_h) // 2
        self.pause_panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        self.pause_title_rect = pygame.Rect(
            panel_x + 30, panel_y + 24, panel_w - 60, 62
        )
        icon_size = 70
        icon_gap = 30
        icons_y = panel_y + 128
        icons_start_x = panel_x + (panel_w - ((icon_size * 3) + (icon_gap * 2))) // 2

        self.pause_restart_rect = pygame.Rect(
            icons_start_x, icons_y, icon_size, icon_size
        )
        self.pause_home_rect = pygame.Rect(
            icons_start_x + icon_size + icon_gap, icons_y, icon_size, icon_size
        )
        self.pause_sound_rect = pygame.Rect(
            icons_start_x + (icon_size + icon_gap) * 2, icons_y, icon_size, icon_size
        )
        self.pause_resume_rect = pygame.Rect(
            panel_x + 52, panel_y + 238, panel_w - 104, 68
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
        self.paused = False
        self.pause_started_ticks: int | None = None
        self.paused_total_ms = 0
        self.lane_cooldowns = [0, 0, 0, 0]
        self.safe_lane_idx = random.randint(0, len(LANE_POSITIONS) - 1)
        self.safe_lane_span_m = 95
        self.safe_lane_until_meter = self.safe_lane_span_m
        self.safe_lane_clear_px = 260
        self.obstacle_window_px = 420
        self.max_obstacles_in_window = 3
        self.critical_window_px = 360
        self.blocker_spawn_gap_frames = 4
        self.blocker_spawn_gap_timer = 0
        self.start_ticks = pygame.time.get_ticks()
        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.game_over_title_font = self._get_menu_font(64)
        self.game_over_stat_font = self._get_menu_font(52)
        self.bg_surfaces = [self._load_bg(i) for i in [2, 5, 4, 3, 8, 1, 7, 6]]
        self.next_biome_idx = 0
        self.current_biome_idx = 0
        self.biome_counter = 1
        self.is_nitro_active = False
        self.nitro_icon = self._load_nitro_icon()
        self.game_over_main_bg = self._load_optional_image(
            "Assets/end.jpg", (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        self.game_over_logo = self._load_optional_image(
            "Assets/game_over.png", (560, 270)
        )
        self.coin_stat_icon = self._load_optional_image("Assets/coins/1.png", (82, 82))
        self.car_stat_icon = self._load_optional_image(
            "Assets/car_dodge.png", (166, 96)
        )

        end_btn_size = 96
        end_btn_gap = 156
        end_btn_y = SCREEN_HEIGHT - 100
        end_center_x = SCREEN_WIDTH // 2

        self.home_btn_end_rect = pygame.Rect(0, 0, end_btn_size, end_btn_size)
        self.replay_btn_end_rect = pygame.Rect(0, 0, end_btn_size, end_btn_size)
        self.sound_btn_end_rect = pygame.Rect(0, 0, end_btn_size, end_btn_size)

        self.home_btn_end_rect.center = (end_center_x - end_btn_gap, end_btn_y)
        self.replay_btn_end_rect.center = (end_center_x, end_btn_y)
        self.sound_btn_end_rect.center = (end_center_x + end_btn_gap, end_btn_y)

        self.home_btn_end_img = self._load_optional_image(
            "Assets/buttons/home.png", (end_btn_size, end_btn_size)
        )
        self.replay_btn_end_img = self._load_optional_image(
            "Assets/buttons/replay.png", (end_btn_size, end_btn_size)
        )
        self.sound_on_end_img = self._load_optional_image(
            "Assets/buttons/soundOn.png", (end_btn_size, end_btn_size)
        )
        self.sound_off_end_img = self._load_optional_image(
            "Assets/buttons/soundOff.png", (end_btn_size, end_btn_size)
        )

        self._end_prev_down = False

    def _init_objects(self) -> None:
        self.road = Road("Assets/road.png")
        self.player = Player(
            SCREEN_HEIGHT - 150, self.car_options[self.selected_car_idx]
        )
        self.obstacles = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.fuels = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

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
        except (PG_ERROR, FileNotFoundError):
            return None

    def _load_menu_font(self, size: int) -> pygame.font.Font:
        for font_name in [
            "Press Start 2P",
            "Pixel Emulator",
            "Perfect DOS VGA 437",
            "VT323",
            "Fixedsys",
        ]:
            font_path = pygame.font.match_font(font_name, bold=True)
            if font_path:
                return pygame.font.Font(font_path, size)
        return pygame.font.SysFont("Courier New", size, bold=True)

    def _get_menu_font(self, size: int) -> pygame.font.Font:
        if size not in self.menu_fonts:
            self.menu_fonts[size] = self._load_menu_font(size)
        return self.menu_fonts[size]

    def _load_nitro_icon(self) -> pygame.Surface | None:
        for icon_path in [
            "Assets/nitro.png",
            "Assets/nitro/nitro.png",
            "nitro.png",
        ]:
            try:
                icon = pygame.image.load(icon_path).convert_alpha()
                return pygame.transform.smoothscale(icon, (54, 54))
            except (PG_ERROR, FileNotFoundError):
                continue
        return None

    def _load_optional_sound(self, path: str) -> pygame.mixer.Sound | None:
        try:
            return pygame.mixer.Sound(path)
        except (PG_ERROR, FileNotFoundError):
            return None

    def _apply_audio_state(self) -> None:
        music_level = self.music_volume if self.sound_on else 0.0
        sfx_level = self.sfx_volume if self.sound_on else 0.0

        try:
            pygame.mixer.music.set_volume(music_level)
        except PG_ERROR:
            pass

        for sfx in [self.coin_sound, self.fuel_sound, self.click_sound]:
            if sfx is not None:
                sfx.set_volume(sfx_level)

    def _play_sfx(self, sfx: pygame.mixer.Sound | None) -> None:
        if self.sound_on and sfx is not None:
            sfx.play()

    def _toggle_sound(self) -> None:
        self.sound_on = not self.sound_on
        self._apply_audio_state()
        if self.sound_on:
            self._play_sfx(self.click_sound)

    def run(self) -> None:
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

    def _handle_nitro(self) -> None:
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

    def _handle_spawning(self) -> None:
        self._refresh_safe_lane_if_needed()
        for i in range(4):
            self.lane_cooldowns[i] -= self.speed
            if self.lane_cooldowns[i] <= 0:
                self._spawn_in_lane(i)

    def _spawn_in_lane(self, lane_idx: int) -> None:
        if lane_idx == self.safe_lane_idx:
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
        enemy_threshold = 0.09 + (0.16 * difficulty)
        obstacle_threshold = enemy_threshold + (0.09 + (0.20 * difficulty))

        r = random.random()
        can_spawn_blocker_now = self.blocker_spawn_gap_timer == 0

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
        return min(1.0, self.distance_meters / 4000.0)

    def _scaled_cooldown(self, min_cd: int, max_cd: int, difficulty: float) -> int:
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
        self.enemies.update(self.speed + 2)

        gone_enemies = [enemy for enemy in prev_enemies if enemy not in self.enemies]
        self.cars_dodged += len(gone_enemies)

    def _check_collisions(self) -> None:
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
        active_ms = pygame.time.get_ticks() - self.start_ticks - self.paused_total_ms
        self.elapsed_time = max(0, active_ms // 1000)
        computed_idx = (self.distance_meters // DISTANCE_PER_BIOME) % len(
            self.bg_surfaces
        )
        if computed_idx != self.current_biome_idx:
            self.current_biome_idx = computed_idx
            self.biome_counter += 1
        self.next_biome_idx = computed_idx

    def _toggle_pause(self) -> None:
        if self.screen_state != "playing" or self.game_over:
            return
        self.paused = not self.paused
        if self.paused:
            self.pause_started_ticks = pygame.time.get_ticks()
        elif self.pause_started_ticks is not None:
            self.paused_total_ms += pygame.time.get_ticks() - self.pause_started_ticks
            self.pause_started_ticks = None

    def _check_events(self) -> None:
        for event in pygame.event.get():
            if event.type == PG_QUIT:
                self._quit_game()
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

    def _quit_game(self) -> None:
        self.running = False
        try:
            pygame.mixer.music.stop()
        except PG_ERROR:
            pass
        PG_QUIT_FN()


if __name__ == "__main__":
    PG_INIT()
    Game().run()
