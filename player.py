import pygame
from settings import SCREEN_WIDTH


class Player(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, image_path: str) -> None:
        super().__init__()
        # Kép betöltése és beállítása
        raw_image = pygame.image.load(image_path).convert_alpha()
        # MEGNÖVELT MÉRET: itt tudod állítani, mekkora legyen az autó!
        self.image = pygame.transform.scale(raw_image, (140, 240))

        # Pozíció és hitbox (rect)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self, move_left: bool, move_right: bool) -> None:
        # A játékos mozgatása a bemenetek alapján
        if move_left:
            self.rect.x -= 5
        if move_right:
            self.rect.x += 5
        self._check_boundaries()

    def _check_boundaries(self) -> None:
        # A képernyő széléhez igazítjuk, nem fix számhoz
        if self.rect.left < 30:
            self.rect.left = 30
        if self.rect.right > SCREEN_WIDTH - 30:
            self.rect.right = SCREEN_WIDTH - 30

    def draw(self, screen: pygame.Surface) -> None:
        # Játékos kirajzolása
        screen.blit(self.image, self.rect)
