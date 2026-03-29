# type: ignore
from settings import PG_INIT
from setup import GameSetupMixin
from runtime import GameRuntimeMixin
from ui import GameUIMixin


class Game(GameUIMixin, GameRuntimeMixin, GameSetupMixin):
    pass


if __name__ == "__main__":
    PG_INIT()
    Game().run()
