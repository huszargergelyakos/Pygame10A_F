import pygame
from game import Game

PG_INIT = getattr(pygame, "init", lambda: None)


def main() -> None:
    PG_INIT()
    Game().run()


if __name__ == "__main__":
    main()
