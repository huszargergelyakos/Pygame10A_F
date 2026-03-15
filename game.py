import sys
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLUE
from road import Road
from player import Player


class Game:
    def __init__(self) -> None:
        # 1. Alapok inicializálása
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Highway Dodge")
        self.clock = pygame.time.Clock()
        self.running = True

        # 2. Játék adatok (EZEK HIÁNYOZTAK!)
        self.speed: int = 5
        self.distance: int = 0
        self.biome_index: int = 1
        self.bg_list: list[str] = ["1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg"]
        self.font = pygame.font.SysFont("Arial", 32, bold=True)

        # 3. Objektumok és Háttér betöltése
        self._load_current_bg()
        self.road = Road("Assets/road.png")
        self.player = Player(SCREEN_HEIGHT - 150, "Assets/cars/1.png")

    def _load_current_bg(self) -> None:
        # Aktuális háttér betöltése
        bg_name = self.bg_list[self.biome_index - 1]
        path = f"Assets/Backgrounds/{bg_name}"
        self.bg_image = pygame.image.load(path).convert()
        self.bg_image = pygame.transform.scale(
            self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT)
        )

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
        # Távolság növelése és biome váltás 500 egységenként
        self.distance += 1
        if self.distance % 500 == 0:
            self._cycle_biome()

    def _cycle_biome(self) -> None:
        # Következő háttérre ugrás
        self.biome_index = (self.biome_index % 5) + 1
        self._load_current_bg()

    def _draw(self) -> None:
        # 1. Háttér (biome)
        self.screen.blit(self.bg_image, (0, 0))
        # 2. Út
        self.road.draw(self.screen)
        # 3. Játékos
        self.player.draw(self.screen)
        # 4. HUD (szöveg)
        self._draw_hud()

        pygame.display.update()

    def _draw_hud(self) -> None:
        # Távolság kiírása a bal felső sarokba
        km_text = self.font.render(
            f"Distance: {self.distance // 10} KM", True, (255, 255, 255)
        )
        self.screen.blit(km_text, (20, 20))

    def _quit_game(self) -> None:
        self.running = False
        pygame.quit()
        sys.exit()
