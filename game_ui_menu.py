import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE

SRCALPHA = int(getattr(pygame, "SRCALPHA", 0))


class GameUIMenuMixin:
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
            fill_color=(45, 18, 72, 192),
            border_color=(162, 128, 245),
            glow_color=(162, 128, 245, 70),
        )

    def _draw_selected_car_box(self, label: str) -> None:
        self._draw_cut_box(
            rect=self.home_selected_rect,
            label=label,
            text_size=24,
            fill_color=(50, 14, 40, 170),
            border_color=(255, 150, 210),
            glow_color=(255, 150, 210, 55),
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
