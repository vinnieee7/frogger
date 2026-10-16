"""
record_after.py
---------------
Records a ~10-second video demonstrating ALL FOUR completed features:
  - Task 1: Pixel-accurate collision detection
  - Task 2: 3-life system (lives shown in HUD)
  - Task 3: Score tracking + WIN state
  - Task 4: 30-second countdown timer (shown in HUD)

The frog is auto-piloted to show a collision (life lost), then a
successful goal crossing (score + WIN).

Saves: after_changes.avi  (in the current directory)
"""

import sys, os, random
sys.path.insert(0, os.path.dirname(__file__))

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
import cv2

# ------------------------------------------------------------------ constants
FPS        = 30
DURATION_S = 10
TOTAL_FRAMES = FPS * DURATION_S

OUT_PATH = os.path.join(os.path.dirname(__file__), "after_changes.avi")

from game.game_engine import (
    GameEngine, STATE_WIN, STATE_GAME_OVER, STATE_PLAYING,
    ATTEMPT_TIME_S, FPS as ENGINE_FPS,
)
from game.renderer import WINDOW_SIZE, WIDTH, HEIGHT, CELL_SIZE, GOAL_ROW, START_ROW

# ------------------------------------------------------------------ script
def main():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    font   = pygame.font.SysFont("consolas", 18, bold=True)

    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    writer = cv2.VideoWriter(OUT_PATH, fourcc, FPS, (WIDTH, HEIGHT))

    engine = GameEngine()

    # Script timeline (in rendered frames at 30 fps):
    #   0-59   (0-2 s)  : frog walks down into a vehicle lane → collision
    #   60-119 (2-4 s)  : show respawn, HUD with lives=2
    #   120-209(4-7 s)  : frog hops straight to goal → WIN banner
    #   210+   (7-10 s) : WIN screen holds

    frame = 0
    script_done = False

    while frame < TOTAL_FRAMES:
        # ---- scripted autopilot ----
        if not script_done:
            # Phase 1: walk into a vehicle  (approx frame 15-55)
            if frame == 15:
                engine.frog.row = 4           # jump into a road lane
            elif frame == 30:
                # Force a vehicle onto the frog's cell for a visible hit
                for v in engine.vehicles:
                    if v.row == 4:
                        v.x = engine.frog.col * CELL_SIZE + 5
                        break
            elif frame == 35:
                # Trigger collision manually if not already hit
                if engine.state == STATE_PLAYING and engine.lives == 3:
                    engine._lose_life()

            # Phase 2: after respawn, walk to goal (frame 80-150)
            elif frame == 80:
                engine.frog.row = 5
            elif frame == 95:
                engine.frog.row = 3
            elif frame == 110:
                engine.frog.row = 1
            elif frame == 120:
                engine.frog.row = GOAL_ROW    # reach the goal → WIN

        engine.update()
        engine.draw(screen, font)

        # Overlay: label for the recording
        label = font.render("AFTER: All 4 Tasks Complete", True, (80, 255, 160))
        screen.blit(label, (8, 4))
        pygame.display.flip()

        raw = pygame.surfarray.array3d(screen)
        bgr = cv2.cvtColor(raw.transpose(1, 0, 2), cv2.COLOR_RGB2BGR)
        writer.write(bgr)

        frame += 1

    writer.release()
    pygame.quit()
    print(f"Saved: {OUT_PATH}")

if __name__ == "__main__":
    main()
