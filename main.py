from game import Game
from settings import PG_INIT


def main() -> None:
    PG_INIT()
    Game().run()


if __name__ == "__main__":
    main()
