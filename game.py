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
        self.player.update()  # <--- Ez a sor felel mostantól a sima mozgásért!

    def _draw(self) -> None:
        self.screen.fill(BLUE)
        self.road.draw(self.screen)
        self.player.draw(self.screen)
        pygame.display.update()

    def _quit_game(self) -> None:
        self.running = False
        pygame.quit()
        sys.exit()
