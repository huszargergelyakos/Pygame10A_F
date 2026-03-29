from game import Game
from settings import PG_INIT


# Elindítja a játékot: pygame init, majd fő ciklus.
def main() -> None:
    # Ez a program belépési pontja.
    # 1) pygame indul
    # 2) Game objektum létrejön
    # 3) elindul a fő játékhurok
    PG_INIT()
    Game().run()


if __name__ == "__main__":
    main()
