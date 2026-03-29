import pygame
from settings import SCREEN_HEIGHT, ROAD_WIDTH, ROAD_X


# Ez kezeli az út kirajzolását.
class Road:
    # Két egyforma út képet tárolunk.
    # Ettől úgy látszik, mintha az út sosem érne véget.

    def __init__(self, image_path: str) -> None:
        # Betöltjük az út képét.
        # A kép méretét az út méretéhez igazítjuk.
        raw_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(raw_image, (ROAD_WIDTH, SCREEN_HEIGHT))
        # Az egyik kép a képernyőn van.
        # A másik közvetlenül felette indul.
        self.y1, self.y2 = 0, -SCREEN_HEIGHT

    def update(self, speed: int) -> None:
        # Minden körben lejjebb visszük a két képet.
        self.y1 += speed
        self.y2 += speed
        self._wrap()

    def _wrap(self) -> None:
        # Ha egy kép teljesen lement, visszatesszük felülre.
        if self.y1 >= SCREEN_HEIGHT:
            self.y1 = self.y2 - SCREEN_HEIGHT
        if self.y2 >= SCREEN_HEIGHT:
            self.y2 = self.y1 - SCREEN_HEIGHT

    def draw(self, screen: pygame.Surface) -> None:
        # Kirajzoljuk mindkét út képet.
        screen.blit(self.image, (ROAD_X, self.y1))
        screen.blit(self.image, (ROAD_X, self.y2))
