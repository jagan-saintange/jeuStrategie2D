import pygame
import sys


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
WIDTH = 750
HEIGHT = 700
DECALAGE = 20


# Constantes
GRID_SIZE = 8
CELL_SIZE = 60
GRID_WIDTH = GRID_SIZE * CELL_SIZE 
GRID_HEIGHT = GRID_SIZE * CELL_SIZE
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Initialisation de Pygame
pygame.init()

# Instanciation de la fenêtre
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mon jeu de stratégie")



# Set up font
font = pygame.font.Font(None, 36)

def draw_info_box(screen, text, box_rect):
    # Draw the box
    pygame.draw.rect(screen, GRAY, box_rect)
    
    # Prepare the text to display
    text_surface = font.render(text, True, BLACK)
    
    # Get the rectangle of the text surface
    text_rect = text_surface.get_rect(center=box_rect.center)
    
    # Draw the text on the box
    screen.blit(text_surface, text_rect)

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Fill the screen with black
# Affiche la grille
    screen.fill(BLACK)
    for x in range(DECALAGE, GRID_WIDTH+DECALAGE, CELL_SIZE):
        for y in range(DECALAGE, GRID_HEIGHT+DECALAGE, CELL_SIZE):
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, WHITE, rect, 1)

    # Define the box dimensions and position
    box_height = HEIGHT - (GRID_HEIGHT+DECALAGE*2+DECALAGE)
    box_width = WIDTH - DECALAGE*2
    box_x = DECALAGE
    box_y = GRID_HEIGHT+DECALAGE*2
    box_rect = pygame.Rect(box_x, box_y, box_width, box_height)

    # Draw the info box with static information
    static_info = "Static Information Box"
    draw_info_box(screen, static_info, box_rect)

    # Update the display
   
    pygame.display.flip()
