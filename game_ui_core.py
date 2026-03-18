import math
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE

SRCALPHA = int(getattr(pygame, "SRCALPHA", 0))


class GameUICoreMixin:
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

    def _active_sound_button_rect(self) -> pygame.Rect | None:
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
