# type: ignore
from settings import PG_INIT
from setup import GameSetupMixin
from runtime import GameRuntimeMixin
from ui import GameUIMixin


# A játék fő osztálya setup, runtime és UI mixinekből áll össze.
class Game(GameUIMixin, GameRuntimeMixin, GameSetupMixin):
    # Ez az osztály nem ír saját metódust, csak összerakja a mixineket.
    # Így egyetlen Game példányban benne van minden: setup, runtime és UI.
    __slots__ = ()


if __name__ == "__main__":
    # A pygame inicializálása után indul a fő ciklus.
    PG_INIT()
    Game().run()
