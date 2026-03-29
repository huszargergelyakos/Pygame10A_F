import random
from pathlib import Path
import pygame
from settings import SCREEN_HEIGHT, LANE_POSITIONS


# Közös alap osztály az úton mozgó objektumokhoz.
class BaseObject(pygame.sprite.Sprite):
    # Ezt örökli az akadály, üzemanyag és enemy.
    # A közös rész: betöltés, sávba rakás, mozgás és törlés.

    def __init__(self, image_path: str, scale_size: tuple[int, int], lane_idx: int):
        super().__init__()
        # Kép betöltése, méretezése és sávba helyezése.
        img = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(img, scale_size)
        self.rect = self.image.get_rect()
        self.rect.centerx = LANE_POSITIONS[lane_idx]
        self.rect.bottom = 0
        self.hitbox = self.rect.inflate(-24, -28)

    def update(self, speed: int):
        # Lefelé mozgatás és hitbox frissítés.
        # Lefelé mozog, majd képernyőn kívül törlődik.
        self.rect.y += speed
        self.hitbox.center = self.rect.center
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


# Statikus akadály típusok.
class Obstacle(BaseObject):
    # Több akadály típus (pl. roadblock, barrel).

    def __init__(self, type_name: str, lane_idx: int):
        path = f"Assets/obstacles/{type_name}.png"
        if type_name == "barrel":
            # A hordó magasabb, keskenyebb hitboxot kap a jobb érzés miatt.
            super().__init__(path, (56, 112), lane_idx)
            self.hitbox = self.rect.inflate(-24, -22)
        else:
            super().__init__(path, (100, 100), lane_idx)


# Üzemanyag pickup objektum.
class Fuel(BaseObject):
    # Nitro töltéshez gyűjthető objektum.

    def __init__(self, lane_idx: int):
        super().__init__("Assets/collectibles/fuel.png", (42, 54), lane_idx)


class Enemy(BaseObject):
    # Ellenség autó véletlen képpel.

    def __init__(self, lane_idx: int):
        path = self._pick_enemy_image_path()
        super().__init__(path, (98, 174), lane_idx)

    def _pick_enemy_image_path(self) -> str:
        # Olyan enemy képet keres, ami tényleg létezik a mappában.
        # Több mappából keres elérhető ellenség képet.
        candidates: list[str] = []
        for folder in ["Assets/enemy", "Assets/enemies"]:
            for i in range(1, 11):
                candidate = f"{folder}/{i}.png"
                if Path(candidate).exists():
                    candidates.append(candidate)

        if candidates:
            return random.choice(candidates)
        return "Assets/cars/1.png"


# Forgó coin animáció külön sprite-ként.
class Coin(pygame.sprite.Sprite):
    # Coin sprite saját frame animációval.

    def __init__(self, lane_idx: int):
        super().__init__()
        self.frames: list[pygame.Surface] = []
        # 6 képkockás coin animáció betöltése.
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
        # Coin mozgás + frame váltás.
        # Mozgás, törlés és képkocka animáció.
        self.rect.y += speed
        self.hitbox.center = self.rect.center
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

        self.anim_timer += 1
        if self.anim_timer >= 5:
            # Minden 5. frame-ben képet vált, ettől lesz pörgés hatás.
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
            self.anim_timer = 0
