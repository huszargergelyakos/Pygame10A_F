import pygame
from settings import LANE_POSITIONS


class Player(pygame.sprite.Sprite):
    def __init__(self, y: int, image_path: str) -> None:
        super().__init__()
        self._load_image(image_path)
        self.current_lane: int = 1  # Kezdés a 2. sávból (indexek: 0, 1, 2, 3)

        self.rect = self.image.get_rect()
        self.rect.center = (LANE_POSITIONS[self.current_lane], y)

        # Új változók a finom mozgáshoz
        self.target_x: int = self.rect.centerx
        self.slide_speed: int = (
            20  # Mozgás sebessége (állíthatod, ha gyorsabbat/lassabbat akarsz)
        )

    def _load_image(self, image_path: str) -> None:
        raw_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(raw_image, (140, 240))

    def move_left(self) -> None:
        # Csak a cél X koordinátát frissítjük, nem az autót teleportáljuk
        if self.current_lane > 0:
            self.current_lane -= 1
            self.target_x = LANE_POSITIONS[self.current_lane]

    def move_right(self) -> None:
        # Csak a cél X koordinátát frissítjük
        if self.current_lane < len(LANE_POSITIONS) - 1:
            self.current_lane += 1
            self.target_x = LANE_POSITIONS[self.current_lane]

    def update(self) -> None:
        # Finom csúszás a cél pozíció felé
        if self.rect.centerx < self.target_x:
            # Ne menjen túl a célon (min függvény)
            self.rect.centerx += min(
                self.slide_speed, self.target_x - self.rect.centerx
            )
        elif self.rect.centerx > self.target_x:
            self.rect.centerx -= min(
                self.slide_speed, self.rect.centerx - self.target_x
            )

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect)
