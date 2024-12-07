import pygame
import random
import sys
import time

from unit_ import *
from personnages import *
from ui_ import *

LEVEL = 3 #doit etre >1

class Game:
    """
    Classe pour représenter le jeu.

    ...
    Attributs
    ---------
    screen: pygame.Surface
        La surface de la fenêtre du jeu.
    player1_units : list[Unit]
        La liste des unités du joueur.
    enemy_units : list[Unit]
        La liste des unités de l'adversaire.
    """

    def __init__(self, screen, player1_units, enemy_units):
        """
        Construit le jeu avec la surface de la fenêtre.

        Paramètres
        ----------
        screen : pygame.Surface
            La surface de la fenêtre du jeu.
        """


        self.screen = screen
        self.player1_units = player1_units
        self.enemy_units = enemy_units 
        
        startposP1 = [(0,0), (1,0), (1,1), (0,1)]
        startposE = [(GRID_SIZE-1,GRID_SIZE-1), (GRID_SIZE-2,GRID_SIZE-1), (GRID_SIZE-2,GRID_SIZE-2), (GRID_SIZE-2,GRID_SIZE-1)]
        random.shuffle(startposP1)
        random.shuffle(startposE)

#----------------------------------------


    def handle_player_turn(self):
        """
        #Tour du joueur
        """
        if len(self.enemy_units)!=0 and len(self.player1_units)!=0:
            for selected_unit in self.player1_units:
    
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
                                selected_unit.move(dx, dy, self.player1_units, self.enemy_units)
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
                                        for units in self.player1_units:
                                            if units.health <= 0:
                                                self.player1_units.remove(units)
                                                #print('UNITS A ETE REMOVED')
                                        self.flip_display(selected_unit)
    
                                has_acted = True
                                selected_unit.is_selected = False
                                self.flip_display(selected_unit)
                                
                            
                            

    def handle_enemy_turn(self):
        """
        #IA très simple pour les ennemis.
        """
        
        print(len(self.enemy_units), len(self.player1_units))
        if len(self.enemy_units)!=0 and len(self.player1_units)!=0:
            for enemy in self.enemy_units:
                #self.flip_display(enemy)
                #time.sleep(0.5)
    
                # Déplacement aléatoire différencié selon le niveau de l'IA
                target = random.choice(self.player1_units)
                for _ in range(LEVEL): #plus le niveau de l'IA sera grand, plus il aura le temps de réfléchir
                    if target.comparateur_faiblesse_resistance(enemy)[1]: #si target a une résistance, il cherche encore
                       target = random.choice(self.player1_units)
                    if LEVEL > 3: #si niveau superieur à 3
                        if not target.comparateur_faiblesse_resistance(enemy)[0]: #si target n'a pas de faiblesse, il cherche encore
                            target = random.choice(self.player1_units)
                    #niveau 5/7 où il garde en mémoire un target pour toute la partie, cette fois en estimant le meilleur enemy dans la liste des joueurs?
                
                
                enemy.current_move = 0
                essai = 0
                while enemy.current_move < enemy.nombre_deplacements:
                    if essai : 
                        if abs(enemy.x - target.x) <= 1 and abs(enemy.y - target.y) <= 1:
                            break
                        else:
                            essai = enemy.move(random.randint(-1, 1), random.randint(-1, 1), self.enemy_units, self.player1_units)
                            if essai:
                                dx, dy = 0, 0
                                if random.randint(0, 1) == 0:
                                    dx = -1
                                else:
                                    dy = -1
                                    essai = enemy.move(dx, dy, self.enemy_units, self.player1_units)
                                    if essai :
                                        break
                    
                    dx = 1 if enemy.x < target.x else -1 if enemy.x > target.x else 0
                    dy = 1 if enemy.y < target.y else -1 if enemy.y > target.y else 0
                    if abs(dx) - abs(dx) == 0:
                        if abs(enemy.x - target.x) > abs(enemy.y - target.y):
                            dy = 0
                        elif abs(enemy.x - target.x) < abs(enemy.y - target.y):
                            dx = 0
                        else:
                            if random.randint(0, 1) == 0:
                                dx = 0
                            else:
                                dy = 0
                    #print(dx, dy)
                    essai = enemy.move(dx, dy, self.enemy_units, self.player1_units)
                    self.flip_display(enemy)
                    time.sleep(0.3)
                    #print(enemy.current_move)
                enemy.current_move = 0
    
                # Attaque si possible
                if abs(enemy.x - target.x) <= 1 and abs(enemy.y - target.y) <= 1:
                    enemy.attack(target)
                    for enemies in self.enemy_units:
                        if enemies.health <= 0:
                            self.enemy_units.remove(enemies)
                            print('ENEMIES A ETE REMOVED')
                    for units in self.player1_units:
                        if units.health <= 0:
                            self.player1_units.remove(units)
                            print('UNITS A ETE REMOVED')
                
                
                            
                
    

    def flip_display(self, selected_unit=False):
        """
        #Affiche le jeu.
        """

        # Affiche la grille
        self.screen.fill(BLACK)
        for x in range(0, WIDTH, CELL_SIZE):
            for y in range(0, HEIGHT, CELL_SIZE):
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, WHITE, rect, 1)

       
        units = self.player1_units + self.enemy_units
        # Affiche les unités
        for unit in units:
            unit.draw(self.screen, units)
            
        #CURSEUR DE sélection
        if selected_unit != False:
            pygame.draw.rect(self.screen, GREEN, (selected_unit.x * CELL_SIZE, selected_unit.y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
        
        #print('boop')
            
            

        # Rafraîchit l'écran
        pygame.display.flip()
        
    def test_fin(self):
        if len(self.player1_units) == 0 or len(self.enemy_units) == 0:
            return False
        else:
            return True
        
    

def main():
    
    #menu type console ui pour paramétrer le combat
    ui=Ui()
    player1_units, enemy_units = ui.run_ui()
    print('chargement du jeu...')
    time.sleep(1)

    # Initialisation de Pygame
    pygame.init()

    # Instanciation de la fenêtre
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mon jeu de stratégie")

    # Instanciation du jeu
    game = Game(screen, player1_units, enemy_units)

    running = True    
    
    while running:
        game.handle_player_turn()
        running = game.test_fin()
        game.handle_enemy_turn()
        running = game.test_fin()
        if len(game.player1_units) == 0 or len(game.enemy_units) == 0: 
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
