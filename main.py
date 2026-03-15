import pygame
from game import Game


def main() -> None:
    # Pygame indítása és a játék példányosítása
    pygame.init()
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
