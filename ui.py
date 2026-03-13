import pygame
from settings import WHITE, YELLOW


class Button:
    def __init__(self, x: int, y: int, image_path: str, scale: float = 1.0) -> None:
        # Kép betöltése és méretezése
        img = pygame.image.load(image_path).convert_alpha()
        width = int(img.get_width() * scale)
        height = int(img.get_height() * scale)
        self.image = pygame.transform.scale(img, (width, height))
        
        # Pozicionálás
        self.rect = self.image.get_rect(center=(x, y))
        self.clicked: bool = False

    def draw(self, screen: pygame.Surface) -> bool:
        """Kirajzolja a gombot és visszatér True-val, ha rákattintottak."""
        action = False
        pos = pygame.mouse.get_pos()

        # Egér feletti detektálás és kattintás figyelése
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        screen.blit(self.image, self.rect)
        return action