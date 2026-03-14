import sys
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLUE
from road import Road
from player import Player


class Game:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Highway Dodge")
        self.clock = pygame.time.Clock()
        self.running = True
        self.bg_image = pygame.image.load("Assets/backgrounds/5.jpg").convert()
        self.bg_image = pygame.transform.scale(
            self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        # Távolság és Biome adatok
        self.distance: int = 0
        self.biome_index: int = 1  # Az 1.jpg-vel kezdünk
        self.bg_list: list[str] = ["1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg"]

        self._load_current_bg()
        self.speed: int = 5
        self.road = Road("Assets/road.png")
        self.player = Player(SCREEN_HEIGHT - 150, "Assets/cars/1.png")

    def run(self) -> None:
        while self.running:
            self._check_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)

    def _check_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit_game()
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)

    def _handle_keydown(self, event: pygame.event.Event) -> None:
        if event.key in (pygame.K_LEFT, pygame.K_a):
            self.player.move_left()
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.player.move_right()

    def _update(self) -> None:
        self.road.update(self.speed)
        self.player.update()
        self._update_distance()

    def _update_distance(self) -> None:
        # Növeljük a távolságot és nézzük, kell-e biome-ot váltani
        self.distance += 1
        if self.distance % 500 == 0:  # BIOME_DISTANCE értéke
            self._cycle_biome()

    def _cycle_biome(self) -> None:
        # Következő biome kiválasztása (ha az 5. után vagyunk, visszaugrik az 1.-re)
        self.biome_index = (self.biome_index % 5) + 1
        self._load_current_bg()

    def _draw_hud(self) -> None:
        # KM szöveg elkészítése és kirajzolása
        km_text = self.font.render(
            f"Distance: {self.distance // 10} KM", True, (255, 255, 255)
        )
        self.screen.blit(km_text, (20, 20))

    def _draw(self) -> None:
        self.screen.blit(self.bg_image, (0, 0))
        self.road.draw(self.screen)
        self.player.draw(self.screen)
        self._draw_hud()  # <--- Új HUD hívás
        pygame.display.update()

    def _quit_game(self) -> None:
        self.running = False
        pygame.quit()
        sys.exit()
