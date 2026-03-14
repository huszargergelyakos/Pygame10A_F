SCREEN_WIDTH: int = 900  # Megnövelt szélesség a háttér miatt
SCREEN_HEIGHT: int = 960
FPS: int = 60

# Színek
BLUE: tuple[int, int, int] = (53, 81, 92)

# Út beállítások - Középre igazítva
ROAD_WIDTH: int = 540
ROAD_X: int = (SCREEN_WIDTH - ROAD_WIDTH) // 2

# 4 sáv koordinátái az ÚTON BELÜL (hozzáadva az út kezdőpontját)
LANE_POSITIONS: list[int] = [ROAD_X + 100, ROAD_X + 212, ROAD_X + 325, ROAD_X + 435]

BIOME_DISTANCE: int = 500 # Ennyi megtett egység után váltunk hátteret