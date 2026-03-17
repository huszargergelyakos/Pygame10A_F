import pygame
from settings import LANE_POSITIONS


class Player(pygame.sprite.Sprite):
    def __init__(self, y: int, image_path: str) -> None:
        super().__init__()
        img = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(img, (112, 210))
        self.rect = self.image.get_rect()

        self.lane_idx = 1
        self.rect.centerx = LANE_POSITIONS[self.lane_idx]
        self.rect.centery = y
        self.target_x = self.rect.centerx
        self.lane_change_speed = 18
        self.hitbox = self.rect.inflate(-40, -46)

    def move_left(self) -> None:
        if self.lane_idx > 0:
            self.lane_idx -= 1
            self.target_x = LANE_POSITIONS[self.lane_idx]

    def move_right(self) -> None:
        if self.lane_idx < len(LANE_POSITIONS) - 1:
            self.lane_idx += 1
            self.target_x = LANE_POSITIONS[self.lane_idx]

    def update(self, _is_nitro_active: bool = False) -> None:
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
        screen.blit(self.image, self.rect)
