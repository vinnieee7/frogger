"""
GameEngine: owns the frog and all vehicles, and runs one frame's worth
of game logic.

Changes from starter:
  Task 1 - Collision detection fixed in game/collisions.py
  Task 2 - 3-life system; frog respawns after a collision; losing all
            lives triggers GAME OVER.
  Task 3 - Score tracking; reaching the goal increments score and
            triggers a WIN state after the first successful crossing.
  Task 4 - 30-second countdown per attempt; running out of time loses
            a life and resets the timer.
"""

import random

import pygame

from game.frog import Frog
from game.vehicle import Vehicle
from game.collisions import check_collision
from game.renderer import (
    GRID_COLS, GRID_ROWS, GOAL_ROW, ROAD_ROWS, START_ROW, CELL_SIZE, WIDTH, HEIGHT,
)

LANE_SPEEDS = [1.5, -2, 2, -2.5, 1.5, -2]   # one entry per road row, alternating direction

# Game state constants
STATE_PLAYING   = "playing"
STATE_WIN       = "win"
STATE_GAME_OVER = "game_over"

MAX_LIVES      = 3
ATTEMPT_TIME_S = 30        # seconds allowed per attempt
FPS            = 60        # must match clock.tick() in main.py


class GameEngine:
    def __init__(self):
        self._reset_game()

    # ------------------------------------------------------------------
    # Initialisation helpers
    # ------------------------------------------------------------------

    def _reset_game(self):
        """Full reset: lives, score, timer, entities."""
        self.lives = MAX_LIVES
        self.score = 0
        self.state = STATE_PLAYING
        self._reset_attempt()

    def _reset_attempt(self):
        """Reset the timer and rebuild/reposition entities for a new attempt."""
        self.timer_frames = ATTEMPT_TIME_S * FPS   # count down in frames
        self._build_entities()

    def _build_entities(self):
        start_col = GRID_COLS // 2
        self.frog = Frog(
            col=start_col, row=START_ROW,
            start_col=start_col, start_row=START_ROW,
            cols=GRID_COLS, start_row_limit=START_ROW,
        )
        frog_x_range = (start_col * CELL_SIZE, start_col * CELL_SIZE + CELL_SIZE)

        self.vehicles = []
        for i, row in enumerate(ROAD_ROWS):
            speed = LANE_SPEEDS[i % len(LANE_SPEEDS)]
            vehicle_width = 40 if i % 2 == 0 else 70
            spacing = 300
            count = 2

            for _attempt in range(20):
                phase = random.randint(0, spacing - 1)
                positions = []
                safe = True
                for n in range(count):
                    offset = phase + n * spacing
                    x = offset if speed > 0 else WIDTH - offset - vehicle_width
                    positions.append(x)
                    if not (x + vehicle_width <= frog_x_range[0] or x >= frog_x_range[1]):
                        safe = False
                if safe:
                    break

            for x in positions:
                self.vehicles.append(Vehicle(x=x, row=row, width=vehicle_width,
                                              height=CELL_SIZE - 8, speed=speed))

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def handle_keydown(self, key):
        if key == pygame.K_r:
            self._reset_game()
            return

        if self.state != STATE_PLAYING:
            return   # ignore movement keys on win/game-over screen

        if key == pygame.K_UP:
            self.frog.move(0, -1)
        elif key == pygame.K_DOWN:
            self.frog.move(0, 1)
        elif key == pygame.K_LEFT:
            self.frog.move(-1, 0)
        elif key == pygame.K_RIGHT:
            self.frog.move(1, 0)

    # ------------------------------------------------------------------
    # Update (called every frame)
    # ------------------------------------------------------------------

    def update(self):
        if self.state != STATE_PLAYING:
            return

        # Move vehicles
        for v in self.vehicles:
            v.update(road_width_px=WIDTH)

        # --- Task 4: countdown timer ---
        self.timer_frames -= 1
        if self.timer_frames <= 0:
            self._lose_life()
            return   # don't check other conditions this frame

        # --- Task 1 + Task 2: pixel-accurate collision → lose a life ---
        if check_collision(self.frog, self.vehicles):
            self._lose_life()
            return

        # --- Task 3: goal reached → win / score ---
        if self.frog.row == GOAL_ROW:
            self.score += 1
            self.state = STATE_WIN   # first successful crossing = win

    def _lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.state = STATE_GAME_OVER
        else:
            self._reset_attempt()

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, surface, font):
        from game import renderer

        renderer.draw_scene(surface, self.frog, self.vehicles)

        # HUD: lives, score, timer
        seconds_left = max(0, self.timer_frames // FPS)
        renderer.draw_text(surface, font, f"Lives: {self.lives}   Score: {self.score}   Time: {seconds_left}s", (10, HEIGHT - 24))

        if self.state == STATE_WIN:
            renderer.draw_banner(surface, font, f"YOU WIN!  Score: {self.score}   Press R to restart")

        elif self.state == STATE_GAME_OVER:
            renderer.draw_banner(surface, font, f"GAME OVER   Score: {self.score}   Press R to restart")
