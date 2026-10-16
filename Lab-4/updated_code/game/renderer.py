"""
renderer: all pygame drawing lives here, kept separate from game logic.

Updated to support a semi-transparent banner overlay for win/game-over
states and a richer HUD showing lives, score, and remaining time.
"""

import pygame

CELL_SIZE = 50
GRID_COLS = 12
GRID_ROWS = 8

WIDTH = CELL_SIZE * GRID_COLS
HEIGHT = CELL_SIZE * GRID_ROWS
WINDOW_SIZE = (WIDTH, HEIGHT)

GOAL_ROW  = 0
ROAD_ROWS = list(range(1, GRID_ROWS - 1))   # rows 1..6
START_ROW = GRID_ROWS - 1                    # row 7

COLOR_BG         = (20, 20, 25)
COLOR_GOAL       = (40, 130, 60)
COLOR_ROAD       = (45, 45, 50)
COLOR_START      = (40, 90, 60)
COLOR_LANE_LINE  = (90, 90, 90)
COLOR_FROG       = (80, 220, 100)
COLOR_VEHICLE    = (220, 80, 70)
COLOR_TEXT       = (255, 255, 255)
COLOR_WIN_BANNER = (255, 220, 80)
COLOR_GO_BANNER  = (255, 80, 80)


def draw_scene(surface, frog, vehicles):
    surface.fill(COLOR_BG)

    for row in range(GRID_ROWS):
        rect = pygame.Rect(0, row * CELL_SIZE, WIDTH, CELL_SIZE)
        if row == GOAL_ROW:
            pygame.draw.rect(surface, COLOR_GOAL, rect)
        elif row == START_ROW:
            pygame.draw.rect(surface, COLOR_START, rect)
        else:
            pygame.draw.rect(surface, COLOR_ROAD, rect)
            pygame.draw.line(surface, COLOR_LANE_LINE,
                             (0, row * CELL_SIZE), (WIDTH, row * CELL_SIZE), 1)

    for v in vehicles:
        pygame.draw.rect(surface, COLOR_VEHICLE, v.get_rect(CELL_SIZE), border_radius=6)

    pygame.draw.rect(surface, COLOR_FROG, frog.get_rect(CELL_SIZE), border_radius=8)


def draw_text(surface, font, text, pos, color=COLOR_TEXT):
    surface.blit(font.render(text, True, color), pos)


def draw_banner(surface, font, text):
    """Draw a semi-transparent dark overlay and centred banner text."""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    # Choose colour based on win vs game-over keyword in text
    color = COLOR_WIN_BANNER if "WIN" in text else COLOR_GO_BANNER

    # Render main banner text in a larger ad-hoc font
    big_font = pygame.font.SysFont("consolas", 32, bold=True)
    surf = big_font.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    surface.blit(surf, rect)

    # Sub-text hint
    small_font = pygame.font.SysFont("consolas", 18)
    hint = small_font.render("Press  R  to restart", True, COLOR_TEXT)
    hrect = hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 44))
    surface.blit(hint, hrect)
