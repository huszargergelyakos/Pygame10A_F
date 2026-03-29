import pygame
from typing import Any

# A játék ablak méretei.
# FPS azt mondja meg, másodpercenként kb. hányszor frissül a kép.
SCREEN_WIDTH = 950
SCREEN_HEIGHT = 1000
FPS = 60

# Itt vannak a gyakran használt színek.
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

# Az út szélessége és helye.
# A képlet középre teszi az utat a képernyőn.
ROAD_WIDTH = 550
ROAD_X = (SCREEN_WIDTH - ROAD_WIDTH) // 2

# Az autósávok közepének x értékei.
# A játékos és a többi autó ezekhez a pontokhoz igazodik.
LANE_POSITIONS = [ROAD_X + 100, ROAD_X + 212, ROAD_X + 325, ROAD_X + 435]

# Ennyi méter után jön a következő háttér.
DISTANCE_PER_BIOME = 1250

# Ezek a pygame gombok és események nevei.
# A getattr miatt akkor sem áll le a kód, ha valami nincs meg.
PG_DOUBLEBUF = int(getattr(pygame, "DOUBLEBUF", 0))
PG_QUIT = int(getattr(pygame, "QUIT", 0))
PG_MOUSEBUTTONDOWN = int(getattr(pygame, "MOUSEBUTTONDOWN", 0))
PG_KEYDOWN = int(getattr(pygame, "KEYDOWN", 0))
PG_K_SPACE = int(getattr(pygame, "K_SPACE", 0))
PG_K_RETURN = int(getattr(pygame, "K_RETURN", 0))
PG_K_C = int(getattr(pygame, "K_c", 0))
PG_K_S = int(getattr(pygame, "K_s", 0))
PG_K_ESCAPE = int(getattr(pygame, "K_ESCAPE", 0))
PG_K_BACKSPACE = int(getattr(pygame, "K_BACKSPACE", 0))
PG_K_LEFT = int(getattr(pygame, "K_LEFT", 0))
PG_K_A = int(getattr(pygame, "K_a", 0))
PG_K_RIGHT = int(getattr(pygame, "K_RIGHT", 0))
PG_K_D = int(getattr(pygame, "K_d", 0))
PG_K_R = int(getattr(pygame, "K_r", 0))
PG_ERROR: Any = getattr(pygame, "error", RuntimeError)
PG_INIT = getattr(pygame, "init", lambda: None)
PG_QUIT_FN = getattr(pygame, "quit", lambda: None)
