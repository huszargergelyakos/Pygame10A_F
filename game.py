import random
import math
import pygame
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    WHITE,
    DISTANCE_PER_BIOME,
    LANE_POSITIONS,
)
from road import Road
from player import Player
from objects import Obstacle, Coin, Fuel, Enemy  # Új import: Enemy


class Game:
    def __init__(self) -> None:
        flags = pygame.DOUBLEBUF
        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT), flags, vsync=1
        )
        pygame.display.set_caption("Highway Dodge")
        self.clock = pygame.time.Clock()
        self._init_variables()
        self._init_objects()

    def _init_variables(self) -> None:
        self.running, self.base_speed = True, 5
        self.speed = self.base_speed
        self.distance_meters, self.elapsed_time = 0, 0
        self.score, self.nitro_gas = 0, 0.0
        self.nitro_passive_rate = 0.45 / FPS
        self.nitro_drain_rate = 0.75
        self.nitro_cooldown_timer = 0
        self.nitro_cooldown_frames = int(1.8 * FPS)
        self.nitro_regen_delay_timer = 0
        self.nitro_regen_delay_frames = int(1.2 * FPS)
        self.nitro_burst_frames = 0
        self.nitro_max_burst_frames = int(2.2 * FPS)
        self.game_over = False
        self.lane_cooldowns = [0, 0, 0, 0]
        self.start_ticks = pygame.time.get_ticks()
        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.bg_surfaces = [self._load_bg(i) for i in [2, 5, 4, 3, 8, 1, 7, 6]]
        self.next_biome_idx = 0
        self.is_nitro_active = False
        self.nitro_icon = self._load_nitro_icon()

    def _init_objects(self) -> None:
        self.road = Road("Assets/road.png")
        self.player = Player(SCREEN_HEIGHT - 150, "Assets/cars/1.png")
        self.obstacles = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.fuels = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()  # Új csoport

        self.bg1_surf = self.bg_surfaces[0]
        self.bg2_surf = self.bg_surfaces[0]
        self.bg1_y, self.bg2_y = 0, -SCREEN_HEIGHT

    def _load_bg(self, index: int) -> pygame.Surface:
        return pygame.transform.scale(
            pygame.image.load(f"Assets/backgrounds/{index}.jpg").convert(),
            (SCREEN_WIDTH, SCREEN_HEIGHT),
        )

    def _load_nitro_icon(self) -> pygame.Surface | None:
        for icon_path in [
            "Assets/nitro/nitro.png",
            "Assets/nitro/0.gif",
            "Assets/nitro/1.gif",
            "Assets/nitro/2.gif",
            "Assets/nitro.png",
            "nitro.png",
        ]:
            try:
                icon = pygame.image.load(icon_path).convert_alpha()
                return pygame.transform.smoothscale(icon, (54, 54))
            except (pygame.error, FileNotFoundError):
                continue
        return None

    def run(self) -> None:
        while self.running:
            self._check_events()
            if not self.game_over:
                self._handle_nitro()
                self._update()
            self._draw()
            self.clock.tick(FPS)

    def _handle_nitro(self) -> None:
        keys = pygame.key.get_pressed()

        if self.nitro_cooldown_timer > 0:
            self.speed = self.base_speed
            self.is_nitro_active = False
            return

        if keys[pygame.K_SPACE] and self.nitro_gas > 0:
            self.speed = self.base_speed * 2
            self.nitro_gas = max(0.0, self.nitro_gas - self.nitro_drain_rate)
            self.is_nitro_active = True
            self.nitro_regen_delay_timer = self.nitro_regen_delay_frames
            self.nitro_burst_frames += 1

            if (
                self.nitro_gas <= 0
                or self.nitro_burst_frames >= self.nitro_max_burst_frames
            ):
                self.speed = self.base_speed
                self.is_nitro_active = False
                self.nitro_burst_frames = 0
                self.nitro_cooldown_timer = self.nitro_cooldown_frames
        else:
            self.speed = self.base_speed
            self.is_nitro_active = False
            if self.nitro_burst_frames > 0 and not keys[pygame.K_SPACE]:
                self.nitro_burst_frames = 0

    def _update(self) -> None:
        if self.nitro_cooldown_timer > 0:
            self.nitro_cooldown_timer -= 1
        if self.nitro_regen_delay_timer > 0:
            self.nitro_regen_delay_timer -= 1

        if (
            not self.is_nitro_active
            and self.nitro_cooldown_timer == 0
            and self.nitro_regen_delay_timer == 0
        ):
            self.nitro_gas = min(100.0, self.nitro_gas + self.nitro_passive_rate)

        self.road.update(self.speed)
        self.player.update(self.is_nitro_active)
        self._handle_spawning()
        self._update_groups()
        self._check_collisions()
        self._scroll_background()
        self._update_stats()

    def _handle_spawning(self) -> None:
        for i in range(4):
            self.lane_cooldowns[i] -= self.speed
            if self.lane_cooldowns[i] <= 0:
                self._spawn_in_lane(i)

    def _spawn_in_lane(self, lane_idx: int) -> None:
        r = random.random()
        if r < 0.10:  # 10% Ellenálló autó
            if self._can_spawn_blocker_in_lane(lane_idx):
                self.enemies.add(Enemy(lane_idx))
                self.lane_cooldowns[lane_idx] = random.randint(400, 600)
            else:
                self.coins.add(Coin(lane_idx))
                self.lane_cooldowns[lane_idx] = random.randint(120, 220)
        elif r < 0.20:  # 10% Akadály
            if self._can_spawn_blocker_in_lane(lane_idx):
                self.obstacles.add(
                    Obstacle(random.choice(["roadblock", "barrel"]), lane_idx)
                )
                self.lane_cooldowns[lane_idx] = random.randint(250, 400)
            else:
                self.fuels.add(Fuel(lane_idx))
                self.lane_cooldowns[lane_idx] = random.randint(220, 360)
        elif r < 0.35:  # 15% Érme
            self.coins.add(Coin(lane_idx))
            self.lane_cooldowns[lane_idx] = random.randint(100, 200)
        elif r < 0.40:  # 5% Benzin
            self.fuels.add(Fuel(lane_idx))
            self.lane_cooldowns[lane_idx] = random.randint(400, 700)
        else:
            self.lane_cooldowns[lane_idx] = random.randint(50, 150)

    def _lane_from_x(self, x_pos: int) -> int:
        return min(
            range(len(LANE_POSITIONS)), key=lambda idx: abs(LANE_POSITIONS[idx] - x_pos)
        )

    def _can_spawn_blocker_in_lane(self, lane_idx: int) -> bool:
        # Ne engedjük, hogy a játékos környezetében minden sáv egyszerre le legyen zárva.
        blocked_lanes = set()
        danger_top = self.player.rect.top - 260
        danger_bottom = self.player.rect.bottom + 120

        for sprite in list(self.obstacles) + list(self.enemies):
            if danger_top <= sprite.rect.centery <= danger_bottom:
                blocked_lanes.add(self._lane_from_x(sprite.rect.centerx))

        return len(blocked_lanes | {lane_idx}) < len(LANE_POSITIONS)

    def _update_groups(self) -> None:
        self.obstacles.update(self.speed)
        self.coins.update(self.speed)
        self.fuels.update(self.speed)
        self.enemies.update(self.speed + 2)  # Az ellenfelek picit gyorsabbak

    def _check_collisions(self) -> None:
        # Ütközés ellenséggel vagy akadállyal
        if pygame.sprite.spritecollide(
            self.player, self.obstacles, False, self._hitbox_collide
        ) or pygame.sprite.spritecollide(
            self.player, self.enemies, False, self._hitbox_collide
        ):
            self.game_over = True
            self.speed = 0

        if pygame.sprite.spritecollide(self.player, self.coins, True):
            self.score += 10

        if pygame.sprite.spritecollide(self.player, self.fuels, True):
            self.nitro_gas = min(100.0, self.nitro_gas + 25.0)

    def _hitbox_collide(
        self, player_sprite: pygame.sprite.Sprite, obj_sprite: pygame.sprite.Sprite
    ) -> bool:
        player_hitbox = getattr(player_sprite, "hitbox", player_sprite.rect)
        obj_hitbox = getattr(obj_sprite, "hitbox", obj_sprite.rect)
        return player_hitbox.colliderect(obj_hitbox)

    def _scroll_background(self) -> None:
        self.bg1_y += self.speed
        self.bg2_y += self.speed
        if self.bg1_y >= SCREEN_HEIGHT:
            self.bg1_y = self.bg2_y - SCREEN_HEIGHT + 1
            self.bg1_surf = self.bg_surfaces[self.next_biome_idx]
        if self.bg2_y >= SCREEN_HEIGHT:
            self.bg2_y = self.bg1_y - SCREEN_HEIGHT + 1
            self.bg2_surf = self.bg_surfaces[self.next_biome_idx]

    def _update_stats(self) -> None:
        self.distance_meters += self.speed // 2
        self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) // 1000
        self.next_biome_idx = (self.distance_meters // DISTANCE_PER_BIOME) % len(
            self.bg_surfaces
        )

    def _draw(self) -> None:
        self.screen.blit(self.bg1_surf, (0, self.bg1_y))
        self.screen.blit(self.bg2_surf, (0, self.bg2_y))
        self.road.draw(self.screen)
        self.player.draw(self.screen)
        self.obstacles.draw(self.screen)
        self.coins.draw(self.screen)
        self.fuels.draw(self.screen)
        self.enemies.draw(self.screen)
        self._draw_hud()
        if self.game_over:
            self._draw_game_over()
        pygame.display.update()

    def _draw_game_over(self) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        title = pygame.font.SysFont("Arial", 64, bold=True).render(
            "GAME OVER", True, (255, 80, 80)
        )
        hint = self.font.render("R = újraindítás, ESC = kilépés", True, WHITE)
        self.screen.blit(
            title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        )
        self.screen.blit(
            hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 35))
        )

    def _draw_hud(self) -> None:
        box = pygame.Surface((180, 105), pygame.SRCALPHA)
        box.fill((0, 0, 0, 180))
        self.screen.blit(box, (10, 20))
        stats = [
            f"{self.distance_meters} m",
            f"Coins: {self.score}",
            f"Time: {self.elapsed_time}s",
        ]
        for i, text in enumerate(stats):
            self.screen.blit(self.font.render(text, True, WHITE), (20, 30 + i * 25))

        center = (SCREEN_WIDTH - 82, SCREEN_HEIGHT - 98)
        radius = 44
        gauge_bg = pygame.Surface((130, 130), pygame.SRCALPHA)
        pygame.draw.circle(gauge_bg, (0, 0, 0, 165), (65, 65), 57)
        self.screen.blit(gauge_bg, (center[0] - 65, center[1] - 65))

        ring_rect = pygame.Rect(0, 0, radius * 2, radius * 2)
        ring_rect.center = center
        pygame.draw.circle(self.screen, (255, 135, 45), center, radius, 3)
        pygame.draw.circle(self.screen, (40, 40, 40), center, radius, 8)
        fill_ratio = self.nitro_gas / 100.0
        start_angle = -math.pi / 2
        end_angle = start_angle + (2 * math.pi * fill_ratio)
        pygame.draw.arc(
            self.screen,
            (255, 190, 40),
            ring_rect,
            start_angle,
            end_angle,
            8,
        )

        if self.nitro_icon:
            icon_rect = self.nitro_icon.get_rect(center=center)
            self.screen.blit(self.nitro_icon, icon_rect)
        else:
            fallback = self.font.render("N2O", True, WHITE)
            self.screen.blit(fallback, fallback.get_rect(center=center))

        nitro_label = self.font.render(f"{int(self.nitro_gas)}%", True, WHITE)
        self.screen.blit(
            nitro_label, nitro_label.get_rect(center=(center[0], center[1] + 58))
        )

    def _check_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit_game()
            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self._init_variables()
                        self._init_objects()
                    if event.key == pygame.K_ESCAPE:
                        self._quit_game()
                else:
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        self.player.move_left()
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.player.move_right()

    def _quit_game(self) -> None:
        self.running = False
        pygame.quit()


if __name__ == "__main__":
    pygame.init()
    Game().run()
