import pygame
from settings import LANE_POSITIONS


# Ez a játékos autója.
class Player(pygame.sprite.Sprite):
    # Az autó sávok között mozog.
    # Nem ugrik azonnal, hanem szépen odacsúszik.

    def __init__(self, y: int, image_path: str) -> None:
        super().__init__()
        # Betöltjük az autó képét.
        # Beállítjuk a méretét.
        img = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(img, (112, 210))
        self.rect = self.image.get_rect()

        self.lane_idx = 1
        self.rect.centerx = LANE_POSITIONS[self.lane_idx]
        self.rect.centery = y
        self.target_x = self.rect.centerx
        self.lane_change_speed = 18
        # A találati doboz kisebb, így nem túl szigorú az ütközés.
        self.hitbox = self.rect.inflate(-40, -46)

    def move_left(self) -> None:
        # Ha lehet, egy sávot balra megyünk.
        if self.lane_idx > 0:
            self.lane_idx -= 1
            self.target_x = LANE_POSITIONS[self.lane_idx]

    def move_right(self) -> None:
        # Ha lehet, egy sávot jobbra megyünk.
        if self.lane_idx < len(LANE_POSITIONS) - 1:
            self.lane_idx += 1
            self.target_x = LANE_POSITIONS[self.lane_idx]

    def update(self, _is_nitro_active: bool = False) -> None:
        # Minden körben közelítünk a cél helyhez.
        # A találati dobozt is ugyanoda igazítjuk.
        if self.rect.centerx < self.target_x:
            self.rect.centerx = min(
                self.rect.centerx + self.lane_change_speed, self.target_x
            )
        elif self.rect.centerx > self.target_x:
            self.rect.centerx = max(
                self.rect.centerx - self.lane_change_speed, self.target_x
            )
        self.hitbox.center = self.rect.center

    def draw(self, screen: pygame.Surface) -> None:
        # Kirajzoljuk az autót.
        screen.blit(self.image, self.rect)
