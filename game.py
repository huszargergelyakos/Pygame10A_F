import sys
import pygame
from settings import *
from road import Road
from player import Player


class Game:
    def __init__(self) -> None:
        # Ablak létrehozása VSync-el és Double Buffer-el a képtörés ellen
        flags = pygame.DOUBLEBUF
        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT), flags, vsync=1
        )
        pygame.display.set_caption("Highway Dodge")
        self.clock = pygame.time.Clock()
        self._init_variables()
        self._init_objects()

    def _init_variables(self) -> None:
        # Alap számlálók és a kért sorrend meghatározása
        self.running, self.speed = True, 5
        self.distance_meters, self.elapsed_time = 0, 0
        self.start_ticks = pygame.time.get_ticks()
        self.font = pygame.font.SysFont("Arial", 24, bold=True)

        # A pontos sorrend, amit kértél
        self.order = [2, 5, 4, 3, 8, 1, 7, 6]
        # Képek előre betöltése a megadott sorrendben
        self.bg_surfaces = [self._load_bg(i) for i in self.order]
        self.next_biome_idx = 0

    def _load_bg(self, index: int) -> pygame.Surface:
        # Háttérképek betöltése a Backgrounds mappából
        img = pygame.image.load(f"Assets/Backgrounds/{index}.jpg").convert()
        return pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))

    def _init_objects(self) -> None:
        # Út, játékos és kezdő háttér rétegek beállítása
        self.road = Road("Assets/road.png")
        self.player = Player(SCREEN_HEIGHT - 150, "Assets/cars/1.png")
        self.bg1_surf = self.bg_surfaces[0]
        self.bg2_surf = self.bg_surfaces[0]
        self.bg1_y, self.bg2_y = 0, -SCREEN_HEIGHT

    def run(self) -> None:
        # Fő játékciklus
        while self.running:
            self._check_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)

    def _check_events(self) -> None:
        # Bemenetek kezelése
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit_game()
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)

    def _handle_keydown(self, event) -> None:
        # Játékos irányítása (nyilak vagy WASD)
        if event.key in (pygame.K_LEFT, pygame.K_a):
            self.player.move_left()
        if event.key in (pygame.K_RIGHT, pygame.K_d):
            self.player.move_right()

    def _update(self) -> None:
        # Játéklogika frissítése
        self.road.update(self.speed)
        self.player.update()
        self._scroll_background()
        self._update_stats()

    def _scroll_background(self) -> None:
        # Háttér mozgatása és váltása 1px átfedéssel a vonalak ellen
        self.bg1_y += self.speed
        self.bg2_y += self.speed
        if self.bg1_y >= SCREEN_HEIGHT:
            self.bg1_y = self.bg2_y - SCREEN_HEIGHT + 1
            self.bg1_surf = self.bg_surfaces[self.next_biome_idx]
        if self.bg2_y >= SCREEN_HEIGHT:
            self.bg2_y = self.bg1_y - SCREEN_HEIGHT + 1
            self.bg2_surf = self.bg_surfaces[self.next_biome_idx]

    def _update_stats(self) -> None:
        # Távolság, idő és a következő háttér indexének számítása
        self.distance_meters += self.speed // 2
        self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) // 1000
        # Meghatározza, melyik kép jöjjön a listából (1000 méterenként)
        self.next_biome_idx = (self.distance_meters // DISTANCE_PER_BIOME) % len(
            self.order
        )

    def _draw(self) -> None:
        # Megjelenítés: háttér -> út -> játékos -> HUD
        self.screen.blit(self.bg1_surf, (0, self.bg1_y))
        self.screen.blit(self.bg2_surf, (0, self.bg2_y))
        self.road.draw(self.screen)
        self.player.draw(self.screen)
        self._draw_hud()
        pygame.display.update()

    def _draw_hud(self) -> None:
        # Statisztikai doboz kirajzolása a bal felső sarokba
        box = pygame.Surface((160, 80), pygame.SRCALPHA)
        box.fill((0, 0, 0, 180))
        self.screen.blit(box, (10, 20))
        d_txt = self.font.render(f"{self.distance_meters} m", True, WHITE)
        t_txt = self.font.render(f"Time: {self.elapsed_time}s", True, WHITE)
        self.screen.blit(d_txt, (25, 30))
        self.screen.blit(t_txt, (25, 60))

    def _quit_game(self) -> None:
        # Kilépés a programból
        pygame.quit()
        sys.exit()
