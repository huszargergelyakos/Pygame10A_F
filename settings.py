import pygame
from typing import Any

# Képernyő és frissítés alap értékek.
# SCREEN_WIDTH / SCREEN_HEIGHT: a teljes ablak mérete pixelben.
# FPS: ennyi frissítést célzunk másodpercenként.
SCREEN_WIDTH = 950
SCREEN_HEIGHT = 1000
FPS = 60

# Gyakran használt színek.
# Ezeket több UI elem újrahasználja, így nem kell mindenhol kézzel
# ugyanazt az RGB értéket ismételni.
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

# Út mérete és vízszintes helye.
# ROAD_X úgy számolódik, hogy az út középre kerüljön a képernyőn.
ROAD_WIDTH = 550
ROAD_X = (SCREEN_WIDTH - ROAD_WIDTH) // 2

# Sávok középvonalai, ide igazodik minden jármű.
# A lane pozíciók fix X koordináták: a játékos és az objektumok
# ezek között mozognak/ezekre spawnolnak.
LANE_POSITIONS = [ROAD_X + 100, ROAD_X + 212, ROAD_X + 325, ROAD_X + 435]

# Ennyi méterenként vált a háttér biom.
DISTANCE_PER_BIOME = 1250

# Pygame konstansok biztonságos aliasai.
# A getattr azért kell, hogy statikus elemzőknél és eltérő környezetben
# se dobjon hibát, ha egy konstans hiányzik.
# Ilyenkor egy biztonságos alapértéket használunk.
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
