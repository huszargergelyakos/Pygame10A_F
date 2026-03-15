import pygame
from settings import SCREEN_HEIGHT, ROAD_WIDTH, ROAD_X


class Road:
    def __init__(self, image_path: str) -> None:
        # Út képének betöltése és méretezése
        raw_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(raw_image, (ROAD_WIDTH, SCREEN_HEIGHT))
        self.y1, self.y2 = 0, -SCREEN_HEIGHT

    def update(self, speed: int) -> None:
        # Az út darabok mozgatása lefelé
        self.y1 += speed
        self.y2 += speed
        self._wrap()

    def _wrap(self) -> None:
        # Pozíciók alaphelyzetbe állítása a végtelen görgetéshez
        if self.y1 >= SCREEN_HEIGHT:
            self.y1 = self.y2 - SCREEN_HEIGHT
        if self.y2 >= SCREEN_HEIGHT:
            self.y2 = self.y1 - SCREEN_HEIGHT

    def draw(self, screen: pygame.Surface) -> None:
        # Mindkét útszelet kirajzolása
        screen.blit(self.image, (ROAD_X, self.y1))
        screen.blit(self.image, (ROAD_X, self.y2))
