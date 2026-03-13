import pygame
from settings import WHITE, YELLOW

class Button:
    def __init__(self, x: int, y: int, image_path: str, scale: float = 1.0) -> None:
        img = pygame.image.load(image_path).convert_alpha()
        width = int(img.get_width() * scale)
        height = int(img.get_height() * scale)
        self.image = pygame.transform.scale(img, (width, height))
        self.rect = self.image.get_rect(center=(x, y))
        self.clicked: bool = False

    def draw(self, screen: pygame.Surface) -> bool:
        """Kirajzolja a gombot és jelzi, ha rákattintottak."""
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        screen.blit(self.image, self.rect)
        return action

class HUD:
    def __init__(self, font_size: int = 30) -> None:
        self.font = pygame.font.SysFont("Arial", font_size, bold=True)

    def draw_stat(self, screen: pygame.Surface, score: int, fuel: int) -> None:
        """Megjeleníti a pontszámot és az üzemanyagot."""
        score_surf = self.font.render(f"SCORE: {score}", True, WHITE)
        fuel_surf = self.font.render(f"FUEL: {fuel}%", True, YELLOW if fuel > 20 else (255, 0, 0))
        
        screen.blit(score_surf, (10, 10))
        screen.blit(fuel_surf, (10, 40))