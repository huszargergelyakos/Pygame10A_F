import pygame
from settings import LANE_POSITIONS


# A játékos autó: sávváltás és kirajzolás.
class Player(pygame.sprite.Sprite):
    # A játékos fix sávok között mozog, nem szabadon az X tengelyen.
    # A target_x a cél sáv közepe, és az autó finoman csúszik oda.

    def __init__(self, y: int, image_path: str) -> None:
        super().__init__()
        # Jármű kép betöltése és méretezése.
        img = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(img, (112, 210))
        self.rect = self.image.get_rect()

        self.lane_idx = 1
        self.rect.centerx = LANE_POSITIONS[self.lane_idx]
        self.rect.centery = y
        self.target_x = self.rect.centerx
        self.lane_change_speed = 18
        # A hitbox kisebb a sprite téglalapnál, így igazságosabb az ütközés.
        self.hitbox = self.rect.inflate(-40, -46)

    def move_left(self) -> None:
        # Balra vált egy sávot, ha nem a legszélső bal sávban van.
        # Egy sávval balra lép, ha lehet.
        if self.lane_idx > 0:
            self.lane_idx -= 1
            self.target_x = LANE_POSITIONS[self.lane_idx]

    def move_right(self) -> None:
        # Jobbra vált egy sávot, ha nem a legszélső jobb sávban van.
        # Egy sávval jobbra lép, ha lehet.
        if self.lane_idx < len(LANE_POSITIONS) - 1:
            self.lane_idx += 1
            self.target_x = LANE_POSITIONS[self.lane_idx]

    def update(self, _is_nitro_active: bool = False) -> None:
        # Frame-enként közelítjük a pozíciót a cél sávhoz.
        # Utána a hitboxot is ugyanoda igazítjuk.
        # Finoman csúszik a cél sáv közepe felé.
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
        # Az autó kirajzolása a képernyőre.
        # Játékos autó kirajzolása.
        screen.blit(self.image, self.rect)
