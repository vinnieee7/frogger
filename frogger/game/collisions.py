"""
collisions: frog-vs-vehicle collision detection.

Task 1 Fix: The original implementation compared grid columns, which is
inaccurate because vehicles move in continuous pixel space and are often
mid-cell. Now we use pygame.Rect.colliderect() for proper AABB detection.
"""

import pygame

CELL_SIZE = 50


def check_collision(frog, vehicles):
    """
    Returns True if the frog's bounding rect overlaps any vehicle's rect.
    Uses pixel-accurate AABB collision instead of the broken grid-column
    comparison that was in the starter code.
    """
    frog_rect = frog.get_rect(CELL_SIZE)
    for v in vehicles:
        if v.row == frog.row and frog_rect.colliderect(v.get_rect(CELL_SIZE)):
            return True
    return False
