from game import Game
from settings import PG_INIT


# Elindítja a játékot: pygame init, majd fő ciklus.
def main() -> None:
    # Innen indul az egész program.
    # Először beindítjuk a pygame-et.
    # Utána elindítjuk a játékot.
    PG_INIT()
    Game().run()


if __name__ == "__main__":
    main()
