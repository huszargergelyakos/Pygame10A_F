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


class Game:
    def __init__(self) -> None:
        flags = pygame.DOUBLEBUF
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
        except (pygame.error, FileNotFoundError):
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
        self.sound_btn_top_rect = pygame.Rect(SCREEN_WIDTH - 72, 18, 54, 54)
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
        self.game_over_title_font = self._get_menu_font(64)
        self.game_over_stat_font = self._get_menu_font(52)
        self.bg_surfaces = [self._load_bg(i) for i in [2, 5, 4, 3, 8, 1, 7, 6]]
        self.next_biome_idx = 0
        self.current_biome_idx = 0
        self.biome_counter = 1
        self.is_nitro_active = False
        self.nitro_frames = self._load_nitro_frames()
        self.nitro_anim_index = 0
        self.nitro_anim_timer = 0
        self.nitro_anim_speed = 4
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
            except (pygame.error, FileNotFoundError):
                continue
        return None

    def _load_nitro_frames(self) -> list[pygame.Surface]:
        frames: list[pygame.Surface] = []
        for i in range(6):
            frame = self._load_optional_image(f"Assets/nitro/{i}.gif", (88, 128))
            if frame is not None:
                frames.append(frame)
        return frames

    def _load_optional_sound(self, path: str) -> pygame.mixer.Sound | None:
        try:
            return pygame.mixer.Sound(path)
        except (pygame.error, FileNotFoundError):
            return None

    def _apply_audio_state(self) -> None:
        music_level = self.music_volume if self.sound_on else 0.0
        sfx_level = self.sfx_volume if self.sound_on else 0.0

        try:
            pygame.mixer.music.set_volume(music_level)
        except pygame.error:
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
        self._update_nitro_anim()
        self._scroll_background()
        self._update_stats()

    def _update_nitro_anim(self) -> None:
        if not self.nitro_frames:
            return

        if self.is_nitro_active:
            self.nitro_anim_timer += 1
            if self.nitro_anim_timer >= self.nitro_anim_speed:
                self.nitro_anim_timer = 0
                self.nitro_anim_index = (self.nitro_anim_index + 1) % len(
                    self.nitro_frames
                )
        else:
            self.nitro_anim_index = 0
            self.nitro_anim_timer = 0

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
        self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) // 1000
        computed_idx = (self.distance_meters // DISTANCE_PER_BIOME) % len(
            self.bg_surfaces
        )
        if computed_idx != self.current_biome_idx:
            self.current_biome_idx = computed_idx
            self.biome_counter += 1
        self.next_biome_idx = computed_idx

    def _draw(self) -> None:
        if self.screen_state == "home":
            self._draw_home()
            pygame.display.update()
            return

        if self.screen_state == "select_car":
            self._draw_select_car()
            pygame.display.update()
            return

        self.screen.blit(self.bg1_surf, (0, self.bg1_y))
        self.screen.blit(self.bg2_surf, (0, self.bg2_y))
        self.road.draw(self.screen)
        self._draw_nitro_trail()
        self.player.draw(self.screen)
        self.obstacles.draw(self.screen)
        self.coins.draw(self.screen)
        self.fuels.draw(self.screen)
        self.enemies.draw(self.screen)
        self._draw_hud()
        if self.game_over:
            self._draw_game_over()
        self._draw_sound_button()
        pygame.display.update()

    def _draw_home(self) -> None:
        if self.home_bg:
            self.screen.blit(self.home_bg, (0, 0))
        else:
            self.screen.fill((22, 20, 40))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 70))
        self.screen.blit(overlay, (0, 0))

        title = self.home_title_font.render("MAIN MENU", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 120)))

        mouse_pressed = pygame.mouse.get_pressed()[0] == 1
        click_started = mouse_pressed and not self._mouse_prev_down
        mouse_pos = pygame.mouse.get_pos()

        self._draw_menu_box(
            self.home_play_rect,
            "PLAY",
            self.home_play_rect.collidepoint(mouse_pos),
        )
        self._draw_menu_box(
            self.home_select_rect,
            "SELECT CAR",
            self.home_select_rect.collidepoint(mouse_pos),
        )
        self._draw_menu_box(
            self.home_quit_rect,
            "QUIT",
            self.home_quit_rect.collidepoint(mouse_pos),
        )
        self._draw_menu_box(
            self.home_selected_rect,
            f"SELECTED CAR {self.selected_car_idx + 1}",
            False,
            text_size=24,
        )

        if click_started and self.home_play_rect.collidepoint(mouse_pos):
            self._start_game_from_home()
        elif click_started and self.home_select_rect.collidepoint(mouse_pos):
            self.screen_state = "select_car"
        elif click_started and self.home_quit_rect.collidepoint(mouse_pos):
            self._quit_game()

        self._mouse_prev_down = mouse_pressed

    def _draw_select_car(self) -> None:
        if self.home_bg:
            self.screen.blit(self.home_bg, (0, 0))
        else:
            self.screen.fill((22, 20, 40))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 92))
        self.screen.blit(overlay, (0, 0))

        title = self.home_title_font.render("SELECT CAR", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 95)))

        preview = self.car_preview_surfaces[self.selected_car_idx]
        preview_rect = preview.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10)
        )
        panel = pygame.Rect(0, 0, 280, 400)
        panel.center = preview_rect.center
        panel_surf = pygame.Surface(panel.size, pygame.SRCALPHA)
        panel_surf.fill((8, 8, 18, 155))
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

        car_label = self.home_info_font.render(
            f"Selected Car: {self.selected_car_idx + 1}/13", True, WHITE
        )
        self.screen.blit(
            car_label,
            car_label.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 205)),
        )

        self._draw_menu_box(
            self.select_play_rect,
            "PLAY",
            self.select_play_rect.collidepoint(mouse_pos),
            text_size=34,
        )
        self._draw_menu_box(
            self.select_back_rect,
            "BACK",
            self.select_back_rect.collidepoint(mouse_pos),
            text_size=34,
        )

        if click_started and self.select_play_rect.collidepoint(mouse_pos):
            self._start_game_from_home()
        elif click_started and self.select_back_rect.collidepoint(mouse_pos):
            self.screen_state = "home"

        self._mouse_prev_down = mouse_pressed

    def _draw_menu_box(
        self,
        rect: pygame.Rect,
        label: str,
        hovered: bool,
        text_size: int = 38,
    ) -> None:
        # Vágott sarkú, fényes keret a képen látható "box" stílushoz.
        alpha_fill = 120 if hovered else 85
        fill_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        cut = 10
        local_pts = [
            (cut, 0),
            (rect.width - cut, 0),
            (rect.width, cut),
            (rect.width, rect.height - cut),
            (rect.width - cut, rect.height),
            (cut, rect.height),
            (0, rect.height - cut),
            (0, cut),
        ]
        pygame.draw.polygon(fill_surf, (20, 20, 24, alpha_fill), local_pts)
        self.screen.blit(fill_surf, rect.topleft)

        border_col = (255, 255, 255)
        glow_col = (255, 255, 255, 65 if hovered else 35)
        pts = [
            (rect.left + cut, rect.top),
            (rect.right - cut, rect.top),
            (rect.right, rect.top + cut),
            (rect.right, rect.bottom - cut),
            (rect.right - cut, rect.bottom),
            (rect.left + cut, rect.bottom),
            (rect.left, rect.bottom - cut),
            (rect.left, rect.top + cut),
        ]

        glow_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(glow_surf, glow_col, pts, 4)
        self.screen.blit(glow_surf, (0, 0))
        pygame.draw.polygon(self.screen, border_col, pts, 2)

        btn_font = self._get_menu_font(text_size)
        text = btn_font.render(label, True, WHITE)
        self.screen.blit(text, text.get_rect(center=rect.center))

    def _active_sound_button_rect(self) -> pygame.Rect | None:
        if self.screen_state == "playing" and not self.game_over:
            return self.sound_btn_top_rect
        if self.game_over:
            return self.sound_btn_end_rect
        return None

    def _draw_sound_button(self) -> None:
        btn_rect = self._active_sound_button_rect()
        if btn_rect is None:
            return

        if self.game_over:
            icon = self.sound_on_end_img if self.sound_on else self.sound_off_end_img
        else:
            icon = self.sound_on_img if self.sound_on else self.sound_off_img

        if icon is not None:
            self.screen.blit(icon, btn_rect)
            return

        fallback = pygame.Surface(btn_rect.size, pygame.SRCALPHA)
        fallback.fill((0, 0, 0, 120))
        self.screen.blit(fallback, btn_rect.topleft)
        pygame.draw.rect(self.screen, WHITE, btn_rect, 2)
        label = self.font.render("S", True, WHITE)
        self.screen.blit(label, label.get_rect(center=btn_rect.center))

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

        coin_y = 332
        car_y = 430
        stats_start_y = 530
        stats_step = 82

        if self.coin_stat_icon:
            self.screen.blit(
                self.coin_stat_icon, (SCREEN_WIDTH // 2 - 195, coin_y - 44)
            )
        if self.car_stat_icon:
            self.screen.blit(self.car_stat_icon, (SCREEN_WIDTH // 2 - 232, car_y - 36))

        coins_txt = self.game_over_stat_font.render(str(self.score), True, WHITE)
        cars_txt = self.game_over_stat_font.render(str(self.cars_dodged), True, WHITE)

        time_label_txt = self.game_over_stat_font.render("Time:", True, WHITE)
        time_value_txt = self.game_over_stat_font.render(
            f"{self.elapsed_time}s", True, WHITE
        )

        biome_label_txt = self.game_over_stat_font.render("Biomes:", True, WHITE)
        biome_value_txt = self.game_over_stat_font.render(
            str(self.biome_counter), True, WHITE
        )

        dist_km = self.distance_meters / 1000.0
        dist_label_txt = self.game_over_stat_font.render("Distance:", True, WHITE)
        dist_value_txt = self.game_over_stat_font.render(
            f"{dist_km:.2f} km", True, WHITE
        )

        self.screen.blit(coins_txt, (SCREEN_WIDTH // 2 + 18, coin_y - 24))
        self.screen.blit(cars_txt, (SCREEN_WIDTH // 2 + 18, car_y - 24))

        time_row_y = stats_start_y
        biome_row_y = stats_start_y + stats_step
        dist_row_y = stats_start_y + (stats_step * 2)

        time_pair_width = time_label_txt.get_width() + 18 + time_value_txt.get_width()
        time_start_x = (SCREEN_WIDTH - time_pair_width) // 2
        self.screen.blit(time_label_txt, (time_start_x, time_row_y - 28))
        self.screen.blit(
            time_value_txt,
            (time_start_x + time_label_txt.get_width() + 18, time_row_y - 32),
        )

        biome_pair_width = (
            biome_label_txt.get_width() + 18 + biome_value_txt.get_width()
        )
        biome_start_x = (SCREEN_WIDTH - biome_pair_width) // 2
        self.screen.blit(biome_label_txt, (biome_start_x, biome_row_y - 28))
        self.screen.blit(
            biome_value_txt,
            (biome_start_x + biome_label_txt.get_width() + 18, biome_row_y - 32),
        )

        dist_pair_width = dist_label_txt.get_width() + 18 + dist_value_txt.get_width()
        dist_start_x = (SCREEN_WIDTH - dist_pair_width) // 2
        self.screen.blit(dist_label_txt, (dist_start_x, dist_row_y - 28))
        self.screen.blit(
            dist_value_txt,
            (dist_start_x + dist_label_txt.get_width() + 18, dist_row_y - 32),
        )

        mouse_pressed = pygame.mouse.get_pressed()[0] == 1
        click_started = mouse_pressed and not self._end_prev_down
        mouse_pos = pygame.mouse.get_pos()

        if self.home_btn_end_img:
            self.screen.blit(self.home_btn_end_img, self.home_btn_end_rect)
        else:
            pygame.draw.rect(self.screen, WHITE, self.home_btn_end_rect, 2)

        if self.replay_btn_end_img:
            self.screen.blit(self.replay_btn_end_img, self.replay_btn_end_rect)
        else:
            pygame.draw.rect(self.screen, WHITE, self.replay_btn_end_rect, 2)

        if click_started and self.replay_btn_end_rect.collidepoint(mouse_pos):
            self._reset_run()
        if click_started and self.home_btn_end_rect.collidepoint(mouse_pos):
            self._go_to_home()

        self._end_prev_down = mouse_pressed

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

        biome_box = pygame.Surface((190, 48), pygame.SRCALPHA)
        biome_box.fill((0, 0, 0, 165))
        biome_box_pos = (SCREEN_WIDTH - 280, 20)
        self.screen.blit(biome_box, biome_box_pos)
        biome_txt = self.font.render(f"Biome: {self.biome_counter}", True, WHITE)
        self.screen.blit(biome_txt, (SCREEN_WIDTH - 270, 32))

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

    def _draw_nitro_trail(self) -> None:
        if not self.is_nitro_active or not self.nitro_frames:
            return

        frame = self.nitro_frames[self.nitro_anim_index]
        trail_rect = frame.get_rect(
            center=(self.player.rect.centerx, self.player.rect.bottom + 18)
        )
        self.screen.blit(frame, trail_rect)

    def _check_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                sound_rect = self._active_sound_button_rect()
                if sound_rect and sound_rect.collidepoint(event.pos):
                    self._toggle_sound()
            if event.type == pygame.KEYDOWN:
                if self.screen_state == "home":
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self._start_game_from_home()
                    if event.key in (pygame.K_c, pygame.K_s):
                        self.screen_state = "select_car"
                    if event.key == pygame.K_ESCAPE:
                        self._quit_game()
                elif self.screen_state == "select_car":
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self._start_game_from_home()
                    if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                        self.screen_state = "home"
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
        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass
        pygame.quit()


if __name__ == "__main__":
    pygame.init()
    Game().run()
