import pygame
from settings import SCREEN_HEIGHT, LANE_POSITIONS


class BaseObject(pygame.sprite.Sprite):
    def __init__(self, image_path: str, scale_size: tuple, lane_idx: int):
        super().__init__()
        # Kép betöltése a megadott útvonalról
        img = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(img, scale_size)
        self.rect = self.image.get_rect()
        self.rect.centerx = LANE_POSITIONS[lane_idx]
        self.rect.bottom = 0

    def update(self, speed: int):
        self.rect.y += speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Obstacle(BaseObject):
    def __init__(self, type_name: str, lane_idx: int):
        # Mappa: Assets/obstacles/ (kisbetű)
        path = f"Assets/obstacles/{type_name}.png"
        super().__init__(path, (100, 100), lane_idx)


class Fuel(BaseObject):
    def __init__(self, lane_idx: int):
        # Mappa: Assets/Collectibles/ (Nagy C!), fájl: fuel.png (kis f)
        super().__init__("Assets/Collectibles/fuel.png", (70, 90), lane_idx)


class Coin(pygame.sprite.Sprite):
    def __init__(self, lane_idx: int):
        super().__init__()
        self.frames = []
        # Mappa: Assets/coins/ (kisbetű)
        for i in range(1, 7):
            img = pygame.image.load(f"Assets/coins/{i}.png").convert_alpha()
            self.frames.append(pygame.transform.scale(img, (60, 60)))

        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.centerx = LANE_POSITIONS[lane_idx]
        self.rect.bottom = 0
        self.anim_timer = 0

    def update(self, speed: int):
        self.rect.y += speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

        self.anim_timer += 1
        if self.anim_timer >= 5:  # Pörgési sebesség
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
            self.anim_timer = 0


class Player(pygame.sprite.Sprite):
    def __init__(self, y: int, image_path: str) -> None:
        super().__init__()
        img = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(img, (102, 190))
        self.rect = self.image.get_rect()

        self.lane_idx = 1
        self.rect.centerx = LANE_POSITIONS[self.lane_idx]
        self.rect.centery = y
        self.target_x = self.rect.centerx
        self.lane_change_speed = 18
        self.hitbox = self.rect.inflate(-34, -40)

    def move_left(self) -> None:
        if self.lane_idx > 0:
            self.lane_idx -= 1
            self.target_x = LANE_POSITIONS[self.lane_idx]

    def move_right(self) -> None:
        if self.lane_idx < len(LANE_POSITIONS) - 1:
            self.lane_idx += 1
            self.target_x = LANE_POSITIONS[self.lane_idx]

    def update(self, is_nitro_active: bool = False) -> None:
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
