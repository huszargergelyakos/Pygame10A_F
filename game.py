import sys
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLUE
from road import Road
from player import Player  # <--- Új import!


class Game:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Highway Dodge")
        self.clock = pygame.time.Clock()
        self.running = True

        self.speed: int = 5
        self.road = Road("Assets/road.png")
        # Játékos példányosítása (állítsd be a helyes kép-elérési utat!)
        self.player = Player(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150, "Assets/cars/1.png"
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

    def _quit_game(self) -> None:
        self.running = False
        pygame.quit()
        sys.exit()

    def _update(self) -> None:
        self.road.update(self.speed)
        self._handle_player_input()  # <--- Játékos irányítása

    def _handle_player_input(self) -> None:
        # Gombok lekérdezése és a játékos frissítése
        keys = pygame.key.get_pressed()
        move_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        move_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        self.player.update(move_left, move_right)

    def _draw(self) -> None:
        self.screen.fill(BLUE)
        self.road.draw(self.screen)
        self.player.draw(self.screen)  # <--- Játékos kirajzolása
        pygame.display.update()
