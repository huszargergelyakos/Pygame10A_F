import pygame
from settings import SCREEN_HEIGHT, ROAD_WIDTH, ROAD_X


class Road:
    def __init__(self, image_path: str) -> None:
        raw_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(raw_image, (ROAD_WIDTH, SCREEN_HEIGHT))
        self.y1: int = 0
        self.y2: int = -SCREEN_HEIGHT

        # Kezdőpozíciók inicializálása (így már nem jelez hibát a linter)
        self.y1: int = 0
        self.y2: int = -SCREEN_HEIGHT

    def update(self, speed: int) -> None:
        self.y1 += speed
        self.y2 += speed
        if self.y1 >= SCREEN_HEIGHT:
            self.y1 = self.y2 - SCREEN_HEIGHT
        if self.y2 >= SCREEN_HEIGHT:
            self.y2 = self.y1 - SCREEN_HEIGHT

    def _check_boundaries(self) -> None:
        # Pontos illeszkedés: a másik útdarab tetejéhez fűzzük hozzá
        if self.y1 >= SCREEN_HEIGHT:
            self.y1 = self.y2 - SCREEN_HEIGHT
        if self.y2 >= SCREEN_HEIGHT:
            self.y2 = self.y1 - SCREEN_HEIGHT

    def draw(self, screen: pygame.Surface) -> None:
        # Most már a ROAD_X (középső) pozícióba rajzolunk
        screen.blit(self.image, (ROAD_X, self.y1))
        screen.blit(self.image, (ROAD_X, self.y2))
