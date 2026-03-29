import math
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE

SRCALPHA = int(getattr(pygame, "SRCALPHA", 0))


class GameUIMixin:
    # Fő render folyamat
    def _draw(self) -> None:
        # Ez a teljes kirajzolás központja: minden frame-ben ez fut le.
        # Először megnézi, hogy melyik képernyő aktív (menü vagy játék).
        # Ez azért fontos, mert mindig csak az adott képernyő elemeit kell rajzolni.
        # A végén meghívjuk a display.update()-et, hogy látszódjon minden változás.
        # A menü képernyők külön rajzolódnak, nem a játéktérrel együtt.
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

    # Közös UI elemek
    def _draw_simple_button(
        self,
        rect: pygame.Rect,
        label: str,
        hovered: bool,
        text_size: int = 40,
        fill_base: tuple[int, int, int, int] = (34, 34, 40, 190),
        fill_hover: tuple[int, int, int, int] = (34, 34, 40, 228),
        border: tuple[int, int, int] = (242, 242, 242),
    ) -> None:
        # Ez egy általános gombrajzoló, hogy ne kelljen minden gombot külön megírni.
        # Ha az egér rajta van a gombon, erősebb (hover) hátteret kap.
        # A felirat mindig a gomb közepére kerül.
        bg = fill_hover if hovered else fill_base
        self._draw_box(rect, bg, border, radius=12)
        text = self._get_menu_font(text_size).render(label, True, WHITE)
        self.screen.blit(text, text.get_rect(center=rect.center))

    def _draw_box(
        self,
        rect: pygame.Rect,
        fill: tuple[int, int, int, int],
        border: tuple[int, int, int],
        radius: int = 12,
    ) -> None:
        # Lekerekített panelt rajzol árnyékkal.
        # Az árnyék segít, hogy a doboz jobban elkülönüljön a háttértől.
        shadow = pygame.Surface((rect.width + 10, rect.height + 10), SRCALPHA)
        pygame.draw.rect(
            shadow,
            (0, 0, 0, 70),
            (0, 0, rect.width + 10, rect.height + 10),
            border_radius=radius + 3,
        )
        self.screen.blit(shadow, (rect.x - 2, rect.y + 3))
        pygame.draw.rect(self.screen, fill, rect, border_radius=radius)
        pygame.draw.rect(self.screen, border, rect, 2, border_radius=radius)

    # Kezdő és autó választó képernyők
    def _draw_home(self) -> None:
        # A főmenü teljes kirajzolása itt történik.
        # Ebben a függvényben nem csak rajzolunk, hanem a kattintásokat is kezeljük.
        if self.home_bg:
            self.screen.blit(self.home_bg, (0, 0))
        else:
            self.screen.fill((22, 20, 40))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), SRCALPHA)
        # Finom sötét réteg a jobb olvashatóságért.
        overlay.fill((0, 0, 0, 70))
        self.screen.blit(overlay, (0, 0))

        title_box = pygame.Rect(0, 0, 520, 92)
        title_box.center = (SCREEN_WIDTH // 2, 112)
        self._draw_box(title_box, (64, 30, 96, 210), (245, 220, 255), radius=20)

        title = self._get_menu_font(64).render("MAIN MENU", True, WHITE)
        self.screen.blit(title, title.get_rect(center=title_box.center))

        mouse_pressed = pygame.mouse.get_pressed()[0] == 1
        # click_started csak a lenyomás pillanatában igaz (nem minden frame-ben).
        click_started = mouse_pressed and not self._mouse_prev_down
        mouse_pos = pygame.mouse.get_pos()

        home_fill = (64, 30, 96, 205)
        home_fill_hover = (88, 48, 132, 225)
        home_border = (245, 220, 255)

        self._draw_simple_button(
            self.home_play_rect,
            "PLAY",
            self.home_play_rect.collidepoint(mouse_pos),
            fill_base=home_fill,
            fill_hover=home_fill_hover,
            border=home_border,
        )
        self._draw_simple_button(
            self.home_select_rect,
            "SELECT CAR",
            self.home_select_rect.collidepoint(mouse_pos),
            fill_base=home_fill,
            fill_hover=home_fill_hover,
            border=home_border,
        )
        self._draw_simple_button(
            self.home_quit_rect,
            "QUIT",
            self.home_quit_rect.collidepoint(mouse_pos),
            fill_base=home_fill,
            fill_hover=home_fill_hover,
            border=home_border,
        )
        self._draw_simple_button(
            self.home_selected_rect,
            f"SELECTED CAR {self.selected_car_idx + 1}",
            False,
            text_size=30,
            fill_base=home_fill,
            fill_hover=home_fill_hover,
            border=home_border,
        )

        if click_started and self.home_play_rect.collidepoint(mouse_pos):
            self._start_game_from_home()
        elif click_started and self.home_select_rect.collidepoint(mouse_pos):
            self.screen_state = "select_car"
        elif click_started and self.home_quit_rect.collidepoint(mouse_pos):
            self._quit_game()

        self._mouse_prev_down = mouse_pressed

    def _draw_select_car(self) -> None:
        # Az autóválasztó képernyő logikája.
        # Látszik az aktuális autó nagyban, a nyilakkal pedig lehet váltani.
        if self.home_bg:
            self.screen.blit(self.home_bg, (0, 0))
        else:
            self.screen.fill((22, 20, 40))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), SRCALPHA)
        overlay.fill((0, 0, 0, 92))
        self.screen.blit(overlay, (0, 0))

        title_box = pygame.Rect(0, 0, 500, 88)
        title_box.center = (SCREEN_WIDTH // 2, 130)
        self._draw_box(title_box, (64, 30, 96, 210), (245, 220, 255), radius=20)

        title = self._get_menu_font(58).render("SELECT CAR", True, WHITE)
        self.screen.blit(title, title.get_rect(center=title_box.center))

        preview = self.car_preview_surfaces[self.selected_car_idx]
        # Az aktuálisan kiválasztott autó nagy preview-ban jelenik meg.
        preview_rect = preview.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10)
        )
        panel = preview_rect.inflate(56, 56)
        panel_surf = pygame.Surface(panel.size, SRCALPHA)
        pygame.draw.rect(
            panel_surf, (22, 22, 28, 145), panel_surf.get_rect(), border_radius=14
        )
        pygame.draw.rect(
            panel_surf, (215, 215, 215), panel_surf.get_rect(), 2, border_radius=14
        )
        self.screen.blit(panel_surf, panel.topleft)
        self.screen.blit(preview, preview_rect)

        mouse_pressed = pygame.mouse.get_pressed()[0] == 1
        click_started = mouse_pressed and not self._mouse_prev_down
        mouse_pos = pygame.mouse.get_pos()

        if self.arrow_left_img:
            self.screen.blit(self.arrow_left_img, self.arrow_left_rect)
            if click_started and self.arrow_left_rect.collidepoint(mouse_pos):
                # Körbeforgó indexelés: 0 elé lépve az utolsó autó jön.
                self.selected_car_idx = (self.selected_car_idx - 1) % len(
                    self.car_options
                )

        if self.arrow_right_img:
            self.screen.blit(self.arrow_right_img, self.arrow_right_rect)
            if click_started and self.arrow_right_rect.collidepoint(mouse_pos):
                # Körbeforgó indexelés jobbra.
                self.selected_car_idx = (self.selected_car_idx + 1) % len(
                    self.car_options
                )

        car_label = self._get_menu_font(32).render(
            f"Selected Car: {self.selected_car_idx + 1}/13", True, WHITE
        )
        self.screen.blit(
            car_label,
            car_label.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 205)),
        )

        self._draw_simple_button(
            self.select_play_rect,
            "PLAY",
            self.select_play_rect.collidepoint(mouse_pos),
            text_size=42,
        )
        self._draw_simple_button(
            self.select_back_rect,
            "BACK",
            self.select_back_rect.collidepoint(mouse_pos),
            text_size=42,
        )

        if click_started and self.select_play_rect.collidepoint(mouse_pos):
            self._start_game_from_home()
        elif click_started and self.select_back_rect.collidepoint(mouse_pos):
            self.screen_state = "home"

        self._mouse_prev_down = mouse_pressed

    # Pause réteg
    def _draw_pause_menu_button(self) -> None:
        # A jobb felső kis pause/menu gomb kirajzolása.
        # Ugyanaz a gomb mutat pause vagy play ikont az aktuális állapottól függően.
        rect = self.pause_menu_btn_rect
        mouse_pos = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse_pos)

        fill_col = (10, 10, 14, 205 if hovered else 188)
        border_col = (170, 230, 255)
        self._draw_box(rect, fill_col, border_col, radius=13)

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

        menu_text = self._get_menu_font(30).render("Menu", True, WHITE)
        text_rect = menu_text.get_rect(midleft=(rect.x + 44, rect.centery + 1))
        self.screen.blit(menu_text, text_rect)

    def _draw_pause_overlay(self) -> None:
        # A szünet menü (overlay) kirajzolása.
        # Itt látszanak az újrakezdés, főmenü, hang és visszatérés gombok.
        self._draw_box(
            self.pause_panel_rect, (16, 16, 18, 220), (210, 210, 210), radius=18
        )
        paused_txt = self._get_menu_font(54).render("Paused", True, WHITE)
        self.screen.blit(
            paused_txt, paused_txt.get_rect(center=self.pause_title_rect.center)
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

        self._draw_simple_button(
            self.pause_resume_rect,
            "Resume",
            self.pause_resume_rect.collidepoint(pygame.mouse.get_pos()),
            text_size=46,
        )

    # Kisegítő függvény a pause panel ikon gombjaihoz.
    def _draw_pause_icon_button(
        self,
        rect: pygame.Rect,
        icon: pygame.Surface | None,
        fallback_label: str,
    ) -> None:
        # Ikonos gomb rajzolása a pause panelen.
        # Ha nincs kép, akkor tartalékként egy betűt rajzolunk a gomb közepére.
        mouse_pos = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse_pos)

        bg_col = (14, 14, 20, 216 if hovered else 188)
        border_col = (205, 220, 246)
        self._draw_box(rect, bg_col, border_col, radius=14)

        if icon is not None:
            icon_size = int(rect.width * 0.72)
            scaled = pygame.transform.smoothscale(icon, (icon_size, icon_size))
            icon_rect = scaled.get_rect(center=rect.center)
            self.screen.blit(scaled, icon_rect)
            return

        label = self._get_menu_font(34).render(fallback_label, True, WHITE)
        self.screen.blit(label, label.get_rect(center=rect.center))

    # Game over nézet és végi gombok
    def _active_sound_button_rect(self) -> pygame.Rect | None:
        # Megmondja, melyik hang gomb legyen aktív az aktuális képernyőn.
        # Most a game over képernyőn használjuk.
        if self.game_over:
            return self.sound_btn_end_rect
        return None

    def _draw_sound_button(self) -> None:
        # Hang gomb rajzolása.
        # Ha van ikon, azt rajzoljuk. Ha nincs, egy egyszerű tartalék gomb jelenik meg.
        btn_rect = self._active_sound_button_rect()
        if btn_rect is None:
            return

        icon = self.sound_on_end_img if self.sound_on else self.sound_off_end_img
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
        # Game over képernyő kirajzolása.
        # Ebben benne van: háttér, sötét overlay, cím, statisztika panel és alsó gombok.
        # Kezdőként ezt úgy érdemes olvasni, hogy fentről lefelé építjük fel a képet.
        if self.game_over_main_bg:
            # 1) Ha van külön game over háttérkép, kirajzoljuk teljes képernyőre.
            self.screen.blit(self.game_over_main_bg, (0, 0))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), SRCALPHA)
        # 2) Erre jön egy félig átlátszó fekete réteg, hogy a fehér szöveg jobban látszódjon.
        overlay.fill((0, 0, 0, 95))
        self.screen.blit(overlay, (0, 0))

        if self.game_over_logo:
            # 3) Ha létezik logó kép, azt használjuk címnek.
            logo_rect = self.game_over_logo.get_rect(center=(SCREEN_WIDTH // 2, 150))
            self.screen.blit(self.game_over_logo, logo_rect)
        else:
            # 4) Ha nincs logó kép, akkor szöveges címet írunk ki.
            title = self.game_over_title_font.render("GAME OVER", True, (255, 80, 80))
            self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 150)))

        # A statisztika sorok elkészítése.
        # Fontos: előbb kirendereljük a szöveget, utána tudjuk pontosan a panel méretét.
        stat_font = pygame.font.SysFont("Segoe UI", 38, bold=True)
        line_gap = 58
        start_y = 380
        # 5) Ez a lista mondja meg, milyen sorrendben jelenjenek meg az adatok.
        lines = [
            f"Coins: {self.score}",
            f"Cars Dodged: {self.cars_dodged}",
            f"Time: {self.elapsed_time}s",
            f"Biome: {self.biome_counter}",
            f"Distance: {self.distance_meters / 1000.0:.2f} km",
        ]
        # 6) A sima szövegekből képet (surface-t) csinálunk, hogy ki tudjuk rajzolni őket.
        line_surfs = [stat_font.render(line, True, WHITE) for line in lines]
        # A panel mérete a leghosszabb sorhoz igazodik, ezért nem lóg ki semmi.

        # 7) Megkeressük az első és utolsó sor helyét, ebből jön a panel magassága.
        first_rect = line_surfs[0].get_rect(center=(SCREEN_WIDTH // 2, start_y))
        last_center_y = start_y + (line_gap * (len(line_surfs) - 1))
        last_rect = line_surfs[-1].get_rect(center=(SCREEN_WIDTH // 2, last_center_y))

        # 8) A panel szélességét a leghosszabb sorhoz igazítjuk egy kis ráhagyással.
        stats_width = line_surfs[-1].get_width() + 36
        stats_height = last_rect.bottom - first_rect.top
        stats_box = pygame.Rect(0, 0, stats_width, stats_height)
        stats_box.centerx = SCREEN_WIDTH // 2
        stats_box.top = first_rect.top
        # 9) Maga a háttérpanel kirajzolása (áttetsző fekete + világos keret).
        self._draw_box(stats_box, (0, 0, 0, 80), (230, 230, 230), radius=14)

        # 10) Soronként kirajzoljuk a stat szöveget a panel tetejétől lefelé.
        for idx, surf in enumerate(line_surfs):
            self.screen.blit(
                surf,
                surf.get_rect(center=(SCREEN_WIDTH // 2, start_y + idx * line_gap)),
            )

        # 11) Kattintáskezelés az alsó gombokhoz (home/replay).
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

        # 12) Replay: új kör indul. Home: vissza a főmenübe.
        if click_started and self.replay_btn_end_rect.collidepoint(mouse_pos):
            self._reset_run()
        if click_started and self.home_btn_end_rect.collidepoint(mouse_pos):
            self._go_to_home()

        # 13) Elmentjük az előző egérállapotot, hogy ne számoljuk többször ugyanazt a kattintást.
        self._end_prev_down = mouse_pressed

    # Állapotváltások
    def _reset_run(self) -> None:
        # Teljes futás újraindítása.
        # Újraépítjük a változókat és az objektumokat, majd játék módra váltunk.
        self._init_variables()
        self._init_objects()
        self.screen_state = "playing"

    def _start_game_from_home(self) -> None:
        # A menüből indított játék ugyanazt a reset logikát használja.
        self._reset_run()

    def _go_to_home(self) -> None:
        # Visszalépés a főmenübe.
        # Itt is teljes reset történik, hogy tiszta állapotból induljon a következő kör.
        self._init_variables()
        self._init_objects()
        self.screen_state = "home"

    # Játék közbeni HUD
    def _draw_hud(self) -> None:
        # Játék közbeni információs felület (HUD).
        # Bal felül stat sorok, jobb alul kör alakú nitro kijelző.
        hud_rect = pygame.Rect(12, 18, 188, 138)
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

        hud_font = pygame.font.SysFont("Arial", 28, bold=True)
        stats = [
            f"{self.distance_meters} m",
            f"Coins: {self.score}",
            f"Time: {self.elapsed_time}s",
            f"Biome: {self.biome_counter}",
        ]
        # A stat sorok fix függőleges ritmussal kerülnek egymás alá.
        for i, text in enumerate(stats):
            self.screen.blit(
                hud_font.render(text, True, WHITE),
                (hud_rect.x + 12, hud_rect.y + 8 + i * 30),
            )

        center = (SCREEN_WIDTH - 82, SCREEN_HEIGHT - 98)
        radius = 44
        gauge_bg = pygame.Surface((130, 130), SRCALPHA)
        pygame.draw.circle(gauge_bg, (0, 0, 0, 165), (65, 65), 57)
        self.screen.blit(gauge_bg, (center[0] - 65, center[1] - 65))

        ring_rect = pygame.Rect(0, 0, radius * 2, radius * 2)
        ring_rect.center = center
        border_color = (255, 170, 60) if self.is_nitro_active else (255, 135, 45)
        track_color = (70, 30, 0) if self.is_nitro_active else (40, 40, 40)
        arc_color = (255, 130, 0) if self.is_nitro_active else (255, 190, 40)
        pygame.draw.circle(self.screen, border_color, center, radius, 3)
        pygame.draw.circle(self.screen, track_color, center, radius, 8)
        fill_ratio = self.nitro_gas / 100.0
        # A nitro százalék arányosan határozza meg az ív hosszát.
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
            fallback = hud_font.render("N2O", True, WHITE)
            self.screen.blit(fallback, fallback.get_rect(center=center))

        nitro_label = hud_font.render(f"{int(self.nitro_gas)}%", True, WHITE)
        self.screen.blit(
            nitro_label, nitro_label.get_rect(center=(center[0], center[1] + 62))
        )
