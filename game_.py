import pygame
import random
import sys
import time

from unit_ import *
from personnages import *


class Game:
    """
    Classe pour représenter le jeu.

    ...
    Attributs
    ---------
    screen: pygame.Surface
        La surface de la fenêtre du jeu.
    player_units : list[Unit]
        La liste des unités du joueur.
    enemy_units : list[Unit]
        La liste des unités de l'adversaire.
    """

    def __init__(self, screen):
        """
        Construit le jeu avec la surface de la fenêtre.

        Paramètres
        ----------
        screen : pygame.Surface
            La surface de la fenêtre du jeu.
        """


        self.screen = screen
        self.player_units = [fighter_freddy, 
                             fighter_chica, 
                             fighter_bonnie, 
                             fighter_foxy
                             ]

        self.enemy_units = [fighter_eren,
                            fighter_armin,
                            fighter_mikasa,
                            fighter_levi
                            ]




#----------------------------------------


    def handle_player_turn(self):
        """
        #Tour du joueur
        """
        if len(self.enemy_units)!=0 and len(self.player_units)!=0:
            for selected_unit in self.player_units:
    
                # Tant que l'unité n'a pas terminé son tour
                has_acted = False
                selected_unit.is_selected = True
                self.flip_display(selected_unit)
                print(f'il vous reste {selected_unit.nombre_deplacements - selected_unit.current_move} déplacements, pour cette unité')
                while not has_acted:
    
                    # Important: cette boucle permet de gérer les événements Pygame
                    for event in pygame.event.get():
    
                        # Gestion de la fermeture de la fenêtre
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        
                        
                        
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:  # Vérifier si la touche Échap est pressée
                                pygame.quit()
                                sys.exit()
                        
                        
                        
                        # Gestion des touches du clavier
                        if event.type == pygame.KEYDOWN:
    
                            # Déplacement (touches fléchées)
                            dx, dy = 0, 0
                            if event.key == pygame.K_LEFT:
                                dx = -1
                            elif event.key == pygame.K_RIGHT:
                                dx = 1
                            elif event.key == pygame.K_UP:
                                dy = -1
                            elif event.key == pygame.K_DOWN:
                                dy = 1
                            
                            
                            if dx != 0 or dy != 0:
                                selected_unit.move(dx, dy, self.player_units, self.enemy_units)
                                print(f'il vous reste {selected_unit.nombre_deplacements - selected_unit.current_move} déplacements, pour cette unité')
                                
                                self.flip_display(selected_unit)
    
                            # Attaque (touche espace) met fin au tour
                            if event.key == pygame.K_SPACE:
                                selected_unit.current_move = 0
                                for enemy in self.enemy_units:
                                    if abs(selected_unit.x - enemy.x) <= 1 and abs(selected_unit.y - enemy.y) <= 1:
                                        selected_unit.attack(enemy)
                                        for enemies in self.enemy_units:
                                            if enemies.health <= 0:
                                                self.enemy_units.remove(enemies)
                                                #print('ENEMIES A ETE REMOVED')
                                        for units in self.player_units:
                                            if units.health <= 0:
                                                self.player_units.remove(units)
                                                #print('UNITS A ETE REMOVED')
                                        self.flip_display(selected_unit)
    
                                has_acted = True
                                selected_unit.is_selected = False
                                self.flip_display(selected_unit)
                                
                            
                            

    def handle_enemy_turn(self):
        """
        #IA très simple pour les ennemis.
        """
        
        print(len(self.enemy_units), len(self.player_units))
        if len(self.enemy_units)!=0 and len(self.player_units)!=0:
            for enemy in self.enemy_units:
                self.flip_display(enemy)
                time.sleep(0.5)
    
                # Déplacement aléatoire
                target = random.choice(self.player_units)
                dx = 1 if enemy.x < target.x else -1 if enemy.x > target.x else 0
                dy = 1 if enemy.y < target.y else -1 if enemy.y > target.y else 0
                enemy.move(dx, dy, self.enemy_units, self.player_units)
    
                # Attaque si possible
                if abs(enemy.x - target.x) <= 1 and abs(enemy.y - target.y) <= 1:
                    enemy.attack(target)
                    for enemies in self.enemy_units:
                        if enemies.health <= 0:
                            self.enemy_units.remove(enemies)
                            print('ENEMIES A ETE REMOVED')
                    for units in self.player_units:
                        if units.health <= 0:
                            self.player_units.remove(units)
                            print('UNITS A ETE REMOVED')
                
                
                            
                
    

    def flip_display(self, selected_unit):
        """
        #Affiche le jeu.
        """

        # Affiche la grille
        self.screen.fill(BLACK)
        for x in range(0, WIDTH, CELL_SIZE):
            for y in range(0, HEIGHT, CELL_SIZE):
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, WHITE, rect, 1)

       
        units = self.player_units + self.enemy_units
        # Affiche les unités
        for unit in units:
            unit.draw(self.screen, units)
            
        #CURSEUR DE sélection
        pygame.draw.rect(self.screen, GREEN, (selected_unit.x * CELL_SIZE, selected_unit.y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
        
        print('boop')
            
            

        # Rafraîchit l'écran
        pygame.display.flip()
        
    def test_fin(self):
        if len(self.player_units) == 0 or len(self.enemy_units) == 0:
            return False
        else:
            return True
        
    

def main():

    # Initialisation de Pygame
    pygame.init()

    # Instanciation de la fenêtre
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mon jeu de stratégie")

    # Instanciation du jeu
    game = Game(screen)

    running = True
    while running:
        game.handle_player_turn()
        running = game.test_fin()
        game.handle_enemy_turn()
        running = game.test_fin()
        if len(game.player_units) == 0 or len(game.enemy_units) == 0: 
            running = False
            
    print('FIN DU JEU, vous pouvez quitter')
    fin = True
    while fin:
        game.flip_display()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Vérifier si la touche Échap est pressée
                    pygame.quit()
                    sys.exit()
            


if __name__ == "__main__":
    main()
