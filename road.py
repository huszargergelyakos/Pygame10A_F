import pygame
from settings import SCREEN_HEIGHT, ROAD_WIDTH, ROAD_X


# Az út képe folyamatosan görgetve rajzolódik.
class Road:
    # Két ugyanilyen út képet tartunk (y1 és y2 pozícióval).
    # Ha az egyik leér, visszakerül felülre, így végtelennek tűnik a mozgás.

    def __init__(self, image_path: str) -> None:
        # Kép betöltés és átméretezés a pálya méretére.
        raw_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(raw_image, (ROAD_WIDTH, SCREEN_HEIGHT))
        # y1 látható tartományban indul, y2 közvetlenül fölötte.
        self.y1, self.y2 = 0, -SCREEN_HEIGHT

    def update(self, speed: int) -> None:
        # Minden frame-ben lefelé mozgatjuk mindkét út szeletet.
        # Két textúra mozog lefelé, így végtelen hatás lesz.
        self.y1 += speed
        self.y2 += speed
        self._wrap()

    def _wrap(self) -> None:
        # Ha egy szelet lecsúszott a képernyőről, visszatesszük a másik fölé.
        if self.y1 >= SCREEN_HEIGHT:
            self.y1 = self.y2 - SCREEN_HEIGHT
        if self.y2 >= SCREEN_HEIGHT:
            self.y2 = self.y1 - SCREEN_HEIGHT

    def draw(self, screen: pygame.Surface) -> None:
        # A két út szelet kirajzolása.
        # Mindkét út-szelet kirajzolása.
        screen.blit(self.image, (ROAD_X, self.y1))
        screen.blit(self.image, (ROAD_X, self.y2))
