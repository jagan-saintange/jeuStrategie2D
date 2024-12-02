import pygame
import sys
from grid import grid, draw_grid

# Taille de la grille et de la fenêtre
GRID_SIZE = 20  # Agrandissement de la grille à 20x20
CELL_SIZE = 30  # Diminuer la taille des cases pour s'adapter à une plus grande grille
WIDTH = GRID_SIZE * CELL_SIZE  # Calculer la largeur de la fenêtre
HEIGHT = GRID_SIZE * CELL_SIZE  # Calculer la hauteur de la fenêtre

def initialize_window():
    pygame.init()  # Initialise Pygame
    screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Crée la fenêtre
    pygame.display.set_caption("Jeu avec Grille 20x20")  # Titre de la fenêtre
    return screen

def main():
    screen = initialize_window()
    clock = pygame.time.Clock()

    game_grid = grid()  # Génère la grille 20x20

    running = True
    while running:
        for event in pygame.event.get():  # Gestion des événements
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))  # Remplir l'écran en blanc
        draw_grid(screen, game_grid, CELL_SIZE)  # Dessiner la grille
        pygame.display.flip()  # Rafraîchir l'affichage
        clock.tick(30)  # Limiter le framerate à 30 FPS

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
