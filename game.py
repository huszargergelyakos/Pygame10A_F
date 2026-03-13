import sys
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLUE
from road import Road


class Game:
    def __init__(self) -> None:
        # Inicializálja a játékot és a képernyőt.
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Highway Dodge")
        self.clock = pygame.time.Clock()
        self.running = True

        # Objektumok példányosítása
        self.speed: int = 5  # Ez lesz a játék alap sebessége
        self.road = Road("Assets/road.png")  # Út létrehozása

    def run(self) -> None:
        # A fő játékciklus, ami futtatja a játékot.
        while self.running:
            self._check_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)

    def _check_events(self) -> None:
        # Felhasználói inputok és események kezelése.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit_game()

    def _quit_game(self) -> None:
        # Biztonságos kilépés a játékból.
        self.running = False
        pygame.quit()
        sys.exit()

    def _update(self) -> None:
        # A játék logikájának frissítése.
        self.road.update(self.speed)  # <--- Út mozgatása

    def _draw(self) -> None:
        # Minden kirajzolása a képernyőre.
        self.screen.fill(BLUE)
        self.road.draw(self.screen)  # <--- Út kirajzolása
        pygame.display.update()
