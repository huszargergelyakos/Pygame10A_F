import pygame
from settings import LANE_POSITIONS


class Player(pygame.sprite.Sprite):
    def __init__(self, y: int, image_path: str) -> None:
        super().__init__()
        self._load_image(image_path)
        self.current_lane = 1
        self.rect = self.image.get_rect()
        self.rect.center = (LANE_POSITIONS[self.current_lane], y)
        self.target_x = self.rect.centerx
        self.slide_speed = 20

    def _load_image(self, image_path: str) -> None:
        # Játékos autó képének betöltése és méretezése
        img = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(img, (140, 240))

    def move_left(self) -> None:
        # Cél sáv módosítása balra
        if self.current_lane > 0:
            self.current_lane -= 1
            self.target_x = LANE_POSITIONS[self.current_lane]

    def move_right(self) -> None:
        # Cél sáv módosítása jobbra
        if self.current_lane < len(LANE_POSITIONS) - 1:
            self.current_lane += 1
            self.target_x = LANE_POSITIONS[self.current_lane]

    def update(self) -> None:
        # Folyamatos csúszás a cél koordináta felé
        if self.rect.centerx != self.target_x:
            diff = self.target_x - self.rect.centerx
            move = self.slide_speed if diff > 0 else -self.slide_speed
            if abs(diff) < self.slide_speed:
                self.rect.centerx = self.target_x
            else:
                self.rect.centerx += move

    def draw(self, screen: pygame.Surface) -> None:
        # Játékos kirajzolása
        screen.blit(self.image, self.rect)
