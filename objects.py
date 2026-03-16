import pygame
import random
from pathlib import Path
from settings import SCREEN_HEIGHT, LANE_POSITIONS


class BaseObject(pygame.sprite.Sprite):
    def __init__(self, image_path: str, scale_size: tuple, lane_idx: int):
        super().__init__()
        # Kép betöltése és skálázása
        img = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(img, scale_size)
        self.rect = self.image.get_rect()
        self.rect.centerx = LANE_POSITIONS[lane_idx]
        self.rect.bottom = 0
        self.hitbox = self.rect.inflate(-24, -28)

    def update(self, speed: int):
        self.rect.y += speed
        self.hitbox.center = self.rect.center
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Obstacle(BaseObject):
    def __init__(self, type_name: str, lane_idx: int):
        # Mappa: assets/obstacles/
        path = f"Assets/obstacles/{type_name}.png"
        if type_name == "barrel":
            super().__init__(path, (56, 112), lane_idx)
            self.hitbox = self.rect.inflate(-24, -22)
        else:
            super().__init__(path, (100, 100), lane_idx)


class Fuel(BaseObject):
    def __init__(self, lane_idx: int):
        # Mappa: assets/collectibles/ (kis c!)
        super().__init__("Assets/collectibles/fuel.png", (42, 54), lane_idx)


class Enemy(BaseObject):
    def __init__(self, lane_idx: int):
        path = self._pick_enemy_image_path()
        super().__init__(path, (98, 174), lane_idx)

    def _pick_enemy_image_path(self) -> str:
        candidates: list[str] = []
        for folder in ["Assets/enemy", "Assets/enemies"]:
            for i in range(1, 11):
                candidate = f"{folder}/{i}.png"
                if Path(candidate).exists():
                    candidates.append(candidate)

        if candidates:
            return random.choice(candidates)

        # Fallback, ha nincs meg az enemy mappa vagy a fajlok.
        return "Assets/cars/1.png"


class Coin(pygame.sprite.Sprite):
    def __init__(self, lane_idx: int):
        super().__init__()
        self.frames = []
        # Mappa: assets/coins/ (kis c!)
        for i in range(1, 7):
            img = pygame.image.load(f"Assets/coins/{i}.png").convert_alpha()
            self.frames.append(pygame.transform.scale(img, (60, 60)))

        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.centerx = LANE_POSITIONS[lane_idx]
        self.rect.bottom = 0
        self.hitbox = self.rect.inflate(-16, -16)
        self.anim_timer = 0

    def update(self, speed: int):
        self.rect.y += speed
        self.hitbox.center = self.rect.center
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

        self.anim_timer += 1
        if self.anim_timer >= 5:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
            self.anim_timer = 0
