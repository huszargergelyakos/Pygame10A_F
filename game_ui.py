import math
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE

SRCALPHA = int(getattr(pygame, "SRCALPHA", 0))


class GameUIMixin:
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
        self.player.draw(self.screen)
        self.obstacles.draw(self.screen)
        self.coins.draw(self.screen)
        self.fuels.draw(self.screen)
        self.enemies.draw(self.screen)
        self._draw_hud()
        if self.game_over:
            self._draw_game_over()
        elif self.screen_state == "playing":
            self._draw_pause_menu_button()
            if self.paused:
                self._draw_pause_overlay()
        self._draw_sound_button()
        pygame.display.update()

    def _draw_home(self) -> None:
        if self.home_bg:
            self.screen.blit(self.home_bg, (0, 0))
        else:
            self.screen.fill((22, 20, 40))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), SRCALPHA)
        overlay.fill((0, 0, 0, 70))
        self.screen.blit(overlay, (0, 0))

        self._draw_home_title_box("MAIN MENU")

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
        self._draw_selected_car_box(f"SELECTED CAR {self.selected_car_idx + 1}")

        if click_started and self.home_play_rect.collidepoint(mouse_pos):
            self._start_game_from_home()
        elif click_started and self.home_select_rect.collidepoint(mouse_pos):
            self.screen_state = "select_car"
        elif click_started and self.home_quit_rect.collidepoint(mouse_pos):
            self._quit_game()

        self._mouse_prev_down = mouse_pressed

    def _draw_home_title_box(self, title_text: str, center_y: int = 120) -> None:
        title_rect = pygame.Rect(0, 0, 520, 92)
        title_rect.center = (SCREEN_WIDTH // 2, center_y)
        self._draw_cut_box(
            rect=title_rect,
            label=title_text,
            text_size=56,
            fill_color=(38, 18, 72, 192),
            border_color=(162, 128, 245),
            glow_color=(162, 128, 245, 70),
        )

    def _draw_selected_car_box(self, label: str) -> None:
        self._draw_cut_box(
            rect=self.home_selected_rect,
            label=label,
            text_size=24,
            fill_color=(45, 14, 40, 170),
            border_color=(255, 160, 210),
            glow_color=(255, 160, 210, 55),
        )

    def _draw_select_car(self) -> None:
        if self.home_bg:
            self.screen.blit(self.home_bg, (0, 0))
        else:
            self.screen.fill((22, 20, 40))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), SRCALPHA)
        overlay.fill((0, 0, 0, 92))
        self.screen.blit(overlay, (0, 0))

        self._draw_home_title_box("SELECT CAR", center_y=145)

        preview = self.car_preview_surfaces[self.selected_car_idx]
        preview_rect = preview.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10)
        )
        panel = pygame.Rect(0, 0, 280, 400)
        panel.center = preview_rect.center
        self._draw_select_preview_panel(panel)
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
        alpha_fill = 120 if hovered else 85
        fill_surf = pygame.Surface((rect.width, rect.height), SRCALPHA)

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

        glow_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), SRCALPHA)
        pygame.draw.polygon(glow_surf, glow_col, pts, 4)
        self.screen.blit(glow_surf, (0, 0))
        pygame.draw.polygon(self.screen, border_col, pts, 2)

        btn_font = self._get_menu_font(text_size)
        text = btn_font.render(label, True, WHITE)
        self.screen.blit(text, text.get_rect(center=rect.center))

    def _draw_cut_box(
        self,
        rect: pygame.Rect,
        label: str,
        text_size: int,
        fill_color: tuple[int, int, int, int],
        border_color: tuple[int, int, int],
        glow_color: tuple[int, int, int, int],
    ) -> None:
        fill_surf = pygame.Surface((rect.width, rect.height), SRCALPHA)
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
        pygame.draw.polygon(fill_surf, fill_color, local_pts)
        self.screen.blit(fill_surf, rect.topleft)

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
        glow_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), SRCALPHA)
        pygame.draw.polygon(glow_surf, glow_color, pts, 4)
        self.screen.blit(glow_surf, (0, 0))
        pygame.draw.polygon(self.screen, border_color, pts, 2)

        text = self._get_menu_font(text_size).render(label, True, WHITE)
        self.screen.blit(text, text.get_rect(center=rect.center))

    def _draw_select_preview_panel(self, rect: pygame.Rect) -> None:
        panel_surf = pygame.Surface(rect.size, SRCALPHA)
        panel_rect = panel_surf.get_rect()
        pygame.draw.rect(panel_surf, (24, 10, 38, 168), panel_rect, border_radius=20)
        pygame.draw.rect(panel_surf, (40, 18, 66, 120), panel_rect, 2, border_radius=20)
        self.screen.blit(panel_surf, rect.topleft)

    def _active_sound_button_rect(self) -> pygame.Rect | None:
        if self.game_over:
            return self.sound_btn_end_rect
        return None

    def _draw_pause_menu_button(self) -> None:
        rect = self.pause_menu_btn_rect
        mouse_pos = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse_pos)

        fill_col = (10, 10, 14, 205 if hovered else 188)
        border_col = (170, 230, 255)
        pygame.draw.rect(self.screen, fill_col, rect, border_radius=13)
        pygame.draw.rect(self.screen, border_col, rect, 2, border_radius=13)

        icon_center = (rect.x + 25, rect.centery)
        if self.paused:
            play_pts = [
                (icon_center[0] - 7, icon_center[1] - 11),
                (icon_center[0] - 7, icon_center[1] + 11),
                (icon_center[0] + 11, icon_center[1]),
            ]
            pygame.draw.polygon(self.screen, WHITE, play_pts)
        else:
            icon_x = rect.x + 16
            icon_y = rect.y + 15
            icon_w = 16
            icon_h = 24
            pygame.draw.rect(
                self.screen, WHITE, (icon_x, icon_y, 5, icon_h), border_radius=2
            )
            pygame.draw.rect(
                self.screen,
                WHITE,
                (icon_x + icon_w - 5, icon_y, 5, icon_h),
                border_radius=2,
            )

        menu_text = self._get_menu_font(26).render("Menu", True, WHITE)
        text_rect = menu_text.get_rect(midleft=(rect.x + 44, rect.centery + 1))
        self.screen.blit(menu_text, text_rect)

    def _draw_pause_overlay(self) -> None:
        panel = pygame.Surface(self.pause_panel_rect.size, SRCALPHA)
        pygame.draw.rect(panel, (10, 10, 14, 196), panel.get_rect(), border_radius=24)
        pygame.draw.rect(panel, (205, 215, 235), panel.get_rect(), 3, border_radius=24)
        self.screen.blit(panel, self.pause_panel_rect.topleft)

        self._draw_cut_box(
            rect=self.pause_title_rect,
            label="Paused",
            text_size=48,
            fill_color=(14, 14, 20, 206),
            border_color=(215, 226, 245),
            glow_color=(180, 210, 255, 32),
        )

        self._draw_pause_icon_button(
            self.pause_restart_rect,
            self.replay_btn_end_img,
            fallback_label="R",
        )
        self._draw_pause_icon_button(
            self.pause_home_rect,
            self.home_btn_end_img,
            fallback_label="H",
        )
        sound_icon = self.sound_on_img if self.sound_on else self.sound_off_img
        self._draw_pause_icon_button(
            self.pause_sound_rect,
            sound_icon,
            fallback_label="S",
        )

        self._draw_cut_box(
            rect=self.pause_resume_rect,
            label="Resume",
            text_size=44,
            fill_color=(26, 86, 34, 188),
            border_color=(196, 255, 210),
            glow_color=(196, 255, 210, 36),
        )

    def _draw_pause_icon_button(
        self,
        rect: pygame.Rect,
        icon: pygame.Surface | None,
        fallback_label: str,
    ) -> None:
        mouse_pos = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse_pos)

        bg_col = (14, 14, 20, 216 if hovered else 188)
        border_col = (205, 220, 246)
        pygame.draw.rect(self.screen, bg_col, rect, border_radius=14)
        pygame.draw.rect(self.screen, border_col, rect, 2, border_radius=14)

        if icon is not None:
            icon_size = int(rect.width * 0.72)
            scaled = pygame.transform.smoothscale(icon, (icon_size, icon_size))
            icon_rect = scaled.get_rect(center=rect.center)
            self.screen.blit(scaled, icon_rect)
            return

        label = self._get_menu_font(30).render(fallback_label, True, WHITE)
        self.screen.blit(label, label.get_rect(center=rect.center))

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

        fallback = pygame.Surface(btn_rect.size, SRCALPHA)
        fallback.fill((0, 0, 0, 120))
        self.screen.blit(fallback, btn_rect.topleft)
        pygame.draw.rect(self.screen, WHITE, btn_rect, 2)
        label = self.font.render("S", True, WHITE)
        self.screen.blit(label, label.get_rect(center=btn_rect.center))

    def _draw_game_over(self) -> None:
        if self.game_over_main_bg:
            self.screen.blit(self.game_over_main_bg, (0, 0))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), SRCALPHA)
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
        hud_rect = pygame.Rect(12, 18, 158, 118)
        hud_panel = pygame.Surface((hud_rect.width, hud_rect.height), SRCALPHA)
        pygame.draw.rect(
            hud_panel,
            (10, 10, 14, 188),
            (0, 0, hud_rect.width, hud_rect.height),
            border_radius=16,
        )
        pygame.draw.rect(
            hud_panel,
            (170, 230, 255, 170),
            (0, 0, hud_rect.width, hud_rect.height),
            2,
            border_radius=16,
        )
        self.screen.blit(hud_panel, hud_rect.topleft)

        hud_glow = pygame.Surface((hud_rect.width + 8, hud_rect.height + 8), SRCALPHA)
        pygame.draw.rect(
            hud_glow,
            (150, 220, 255, 42),
            (0, 0, hud_rect.width + 8, hud_rect.height + 8),
            4,
            border_radius=18,
        )
        self.screen.blit(hud_glow, (hud_rect.x - 4, hud_rect.y - 4))

        stats = [
            f"{self.distance_meters} m",
            f"Coins: {self.score}",
            f"Time: {self.elapsed_time}s",
            f"Biome: {self.biome_counter}",
        ]
        for i, text in enumerate(stats):
            self.screen.blit(
                self.font.render(text, True, WHITE),
                (hud_rect.x + 12, hud_rect.y + 10 + i * 25),
            )

        center = (SCREEN_WIDTH - 82, SCREEN_HEIGHT - 98)
        radius = 44
        gauge_bg = pygame.Surface((130, 130), SRCALPHA)
        pygame.draw.circle(gauge_bg, (0, 0, 0, 165), (65, 65), 57)
        self.screen.blit(gauge_bg, (center[0] - 65, center[1] - 65))

        if self.is_nitro_active:
            glow_surf = pygame.Surface((170, 170), SRCALPHA)
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
