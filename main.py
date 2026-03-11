import pygame
from game import Game


def main() -> None:
    # A játék inicializálása és elindítása.
    pygame.init()

    # Később ide jöhet a menü vagy a car selector betöltése is
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
