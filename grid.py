import random
import pygame
from case import Case

def grid():
    grid = []
    for x in range(20):  # Augmentation de la taille de la grille à 20x20
        row = []
        for y in range(20):  # Augmenter la grille à 20x20
            case_type = random.choices(
                ["normal", "obstacle", "heal", "trap"],
                weights=[70, 20, 5, 5]  # Probabilités de chaque type de case
            )[0]
            row.append(Case(x, y, case_type))
        grid.append(row)
    return grid

def draw_grid(screen, grid, cell_size):
    for row in grid:
        for case in row:
            pygame.draw.rect(
                screen, case.get_color(),
                (case.x * cell_size, case.y * cell_size, cell_size, cell_size)
            )
            pygame.draw.rect(
                screen, (0, 0, 0),
                (case.x * cell_size, case.y * cell_size, cell_size, cell_size), 1  # Contour
            )
