# type: ignore
from settings import PG_INIT
from setup import GameSetupMixin
from runtime import GameRuntimeMixin
from ui import GameUIMixin


# A játék fő osztálya setup, runtime és UI mixinekből áll össze.
class Game(GameUIMixin, GameRuntimeMixin, GameSetupMixin):
    # Ez a fő játék osztály.
    # A játék részei itt kerülnek össze egy helyre.
    __slots__ = ()


if __name__ == "__main__":
    # Itt indul el a játék futása.
    PG_INIT()
    Game().run()
