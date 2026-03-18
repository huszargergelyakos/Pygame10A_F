import random
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, LANE_POSITIONS
from road import Road
from player import Player
from game_compat import PG_DOUBLEBUF, PG_ERROR


class GameSetupMixin:
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
