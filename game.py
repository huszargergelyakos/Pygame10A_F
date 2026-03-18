# type: ignore
from game_compat import PG_INIT
from game_setup import GameSetupMixin
from game_runtime import GameRuntimeMixin
from game_ui import GameUIMixin


class Game(GameUIMixin, GameRuntimeMixin, GameSetupMixin):
    pass


if __name__ == "__main__":
    PG_INIT()
    Game().run()
