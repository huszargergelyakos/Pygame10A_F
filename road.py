import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


class Road:
    def __init__(self, image_path: str) -> None:
        # Kép betöltése és átméretezése
        raw_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(raw_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Kezdőpozíciók inicializálása (így már nem jelez hibát a linter)
        self.y1: int = 0
        self.y2: int = -SCREEN_HEIGHT

    def update(self, speed: int) -> None:
        # Az út mozgatása lefelé
        self.y1 += speed
        self.y2 += speed
        self._check_boundaries()

    def _check_boundaries(self) -> None:
        # Ha az egyik útdarab kiment a képernyőről, visszaugrik
        if self.y1 >= SCREEN_HEIGHT:
            self.y1 = -SCREEN_HEIGHT
        if self.y2 >= SCREEN_HEIGHT:
            self.y2 = -SCREEN_HEIGHT

    def draw(self, screen: pygame.Surface) -> None:
        # Az út kirajzolása
        screen.blit(self.image, (0, self.y1))
        screen.blit(self.image, (0, self.y2))
