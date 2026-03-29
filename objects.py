import random
from pathlib import Path
import pygame
from settings import SCREEN_HEIGHT, LANE_POSITIONS


# Ez az alap osztály a pályán mozgó dolgokhoz.
class BaseObject(pygame.sprite.Sprite):
    # Több másik osztály is ezt használja.
    # Itt van a közös rész: kép, hely, mozgás, törlés.

    def __init__(self, image_path: str, scale_size: tuple[int, int], lane_idx: int):
        super().__init__()
        # Betöltjük a képet.
        # A képet a kívánt méretre állítjuk.
        # A tárgyat a megadott sávba tesszük.
        img = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(img, scale_size)
        self.rect = self.image.get_rect()
        self.rect.centerx = LANE_POSITIONS[lane_idx]
        self.rect.bottom = 0
        self.hitbox = self.rect.inflate(-24, -28)

    def update(self, speed: int):
        # A tárgy lefelé megy.
        # A találati doboz követi a képet.
        # Ha lement a képernyőről, töröljük.
        self.rect.y += speed
        self.hitbox.center = self.rect.center
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


# Akadályok.
class Obstacle(BaseObject):
    # Többféle akadály képet tud használni.

    def __init__(self, type_name: str, lane_idx: int):
        path = f"Assets/obstacles/{type_name}.png"
        if type_name == "barrel":
            # A hordóhoz kicsit más méret kell.
            super().__init__(path, (56, 112), lane_idx)
            self.hitbox = self.rect.inflate(-24, -22)
        else:
            super().__init__(path, (100, 100), lane_idx)


# Ez ad plusz nitrót.
class Fuel(BaseObject):
    # Egyszerűen csak egy gyűjthető tárgy.

    def __init__(self, lane_idx: int):
        super().__init__("Assets/collectibles/fuel.png", (42, 54), lane_idx)


class Enemy(BaseObject):
    # Ez az ellenfél autó.
    # Mindig választ egy képet a listából.

    def __init__(self, lane_idx: int):
        path = self._pick_enemy_image_path()
        super().__init__(path, (98, 174), lane_idx)

    def _pick_enemy_image_path(self) -> str:
        # Végignézi a mappákat.
        # Ami kép tényleg megvan, azt felveszi a listába.
        candidates: list[str] = []
        for folder in ["Assets/enemy", "Assets/enemies"]:
            for i in range(1, 11):
                candidate = f"{folder}/{i}.png"
                if Path(candidate).exists():
                    candidates.append(candidate)

        if candidates:
            # Ha van legalább egy kép, abból választunk egyet.
            return random.choice(candidates)
        # Ha nincs találat, adunk egy biztos képet.
        return "Assets/cars/1.png"


# Ez a pénz érme.
class Coin(pygame.sprite.Sprite):
    # Több képből áll, így forgónak látszik.

    def __init__(self, lane_idx: int):
        super().__init__()
        self.frames: list[pygame.Surface] = []
        # Betöltjük a coin képeket.
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
        # Lejjebb visszük az érmét.
        # Ha lement, töröljük.
        # Közben léptetjük a képeket, hogy forogjon.
        self.rect.y += speed
        self.hitbox.center = self.rect.center
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

        self.anim_timer += 1
        if self.anim_timer >= 5:
            # Néhány körönként a következő képre váltunk.
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
            self.anim_timer = 0
