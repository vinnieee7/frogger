"""
record_before.py
----------------
Records a ~10-second video of the ORIGINAL BUGGY frogger behaviour:
  - The frog walks directly into a vehicle without being detected as a hit.
  - This demonstrates the broken grid-column collision logic.

Saves: before_changes.avi  (in the current directory)
"""

import sys, os, random
sys.path.insert(0, os.path.dirname(__file__))

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
import cv2
import numpy as np

# ------------------------------------------------------------------ constants
CELL_SIZE = 50
GRID_COLS = 12
GRID_ROWS = 8
WIDTH  = CELL_SIZE * GRID_COLS
HEIGHT = CELL_SIZE * GRID_ROWS

FPS        = 30
DURATION_S = 10
TOTAL_FRAMES = FPS * DURATION_S

OUT_PATH = os.path.join(os.path.dirname(__file__), "before_changes.avi")

# ------------------------------------------------------------------ colours
COLOR_BG         = (20,  20,  25)
COLOR_GOAL       = (40, 130,  60)
COLOR_ROAD       = (45,  45,  50)
COLOR_START      = (40,  90,  60)
COLOR_LANE_LINE  = (90,  90,  90)
COLOR_FROG       = (80, 220, 100)
COLOR_VEHICLE    = (220, 80,  70)
COLOR_TEXT       = (255, 255, 255)

# ------------------------------------------------------------------ original buggy collision
def buggy_check_collision(frog_col, vehicles):
    """Original broken logic: converts vehicle pixel x to a grid column."""
    for v in vehicles:
        vehicle_col = int(v["x"] // CELL_SIZE)
        if vehicle_col == frog_col and v["row"] == 3:
            return True
    return False

# ------------------------------------------------------------------ minimal game state
class BuggyDemo:
    def __init__(self):
        self.frog_col   = GRID_COLS // 2
        self.frog_row   = GRID_ROWS - 1
        self.hit_flash  = 0
        self.message    = ""

        # One fast vehicle in row 3 that will visibly overlap the frog but NOT trigger
        self.vehicle = {"x": float(WIDTH), "row": 3, "width": 70, "speed": -3.5}

    def update(self, frame):
        # Vehicle moves left
        self.vehicle["x"] += self.vehicle["speed"]
        if self.vehicle["x"] < -self.vehicle["width"]:
            self.vehicle["x"] = float(WIDTH)

        # Auto-pilot frog: walk to row 3 and stay, so vehicle passes through it
        if frame < 40:
            if frame % 10 == 0 and self.frog_row > 3:
                self.frog_row -= 1

        # Buggy collision check
        frog_rect = pygame.Rect(
            self.frog_col * CELL_SIZE + 4,
            self.frog_row * CELL_SIZE + 4,
            CELL_SIZE - 8, CELL_SIZE - 8,
        )
        v = self.vehicle
        v_rect = pygame.Rect(int(v["x"]), v["row"] * CELL_SIZE + 4, v["width"], CELL_SIZE - 8)

        actually_overlapping = frog_rect.colliderect(v_rect)
        buggy_says_hit       = buggy_check_collision(self.frog_col, [v]) if self.frog_row == 3 else False

        if actually_overlapping and not buggy_says_hit:
            self.message = "BUG: Vehicle overlaps frog — no collision detected!"
        elif actually_overlapping and buggy_says_hit:
            self.message = "Hit detected (rare alignment)"
        else:
            self.message = "Frog in lane 3 — waiting for vehicle..."

        if self.hit_flash > 0:
            self.hit_flash -= 1

    def draw(self, surface, font):
        surface.fill(COLOR_BG)
        for row in range(GRID_ROWS):
            rect = pygame.Rect(0, row * CELL_SIZE, WIDTH, CELL_SIZE)
            if row == 0:
                pygame.draw.rect(surface, COLOR_GOAL, rect)
            elif row == GRID_ROWS - 1:
                pygame.draw.rect(surface, COLOR_START, rect)
            else:
                pygame.draw.rect(surface, COLOR_ROAD, rect)
                pygame.draw.line(surface, COLOR_LANE_LINE, (0, row*CELL_SIZE), (WIDTH, row*CELL_SIZE), 1)

        v = self.vehicle
        pygame.draw.rect(surface, COLOR_VEHICLE,
                         pygame.Rect(int(v["x"]), v["row"]*CELL_SIZE+4, v["width"], CELL_SIZE-8),
                         border_radius=6)

        frog_color = (255, 80, 80) if self.hit_flash else COLOR_FROG
        pygame.draw.rect(surface, frog_color,
                         pygame.Rect(self.frog_col*CELL_SIZE+4, self.frog_row*CELL_SIZE+4,
                                     CELL_SIZE-8, CELL_SIZE-8), border_radius=8)

        # HUD
        title = font.render("BEFORE: Buggy Collision Detection", True, (255, 220, 80))
        surface.blit(title, (8, 4))
        msg_surf = font.render(self.message, True, (255, 120, 120))
        surface.blit(msg_surf, (8, HEIGHT - 24))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    font   = pygame.font.SysFont("consolas", 16, bold=True)

    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    writer = cv2.VideoWriter(OUT_PATH, fourcc, FPS, (WIDTH, HEIGHT))

    demo = BuggyDemo()

    for frame in range(TOTAL_FRAMES):
        demo.update(frame)
        demo.draw(screen, font)
        pygame.display.flip()

        # Capture frame
        raw  = pygame.surfarray.array3d(screen)           # shape (W, H, 3) RGB
        bgr  = cv2.cvtColor(raw.transpose(1, 0, 2), cv2.COLOR_RGB2BGR)
        writer.write(bgr)

    writer.release()
    pygame.quit()
    print(f"Saved: {OUT_PATH}")

if __name__ == "__main__":
    main()
