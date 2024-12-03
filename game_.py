import pygame
import random
import sys

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
        self.player_units = [#Archer(perso=perso1, x=0, y=0, health=100, team='player1', attack_power=4, defense_power=3, agility_power=2, speed = 60),
                             #Aerien(perso=perso2, x=1, y=0, health=100, team='player1', attack_power=1, defense_power=5, agility_power=1, speed = 85),
                             #Terrien(perso=perso3, x=1, y=1, health=100, team='player1', attack_power=6, defense_power=5, agility_power=1, speed = 10),
                             Terrien(perso=perso3, x=0, y=1, health=180, team='player1', attack_power=5, defense_power=4, agility_power=2, speed = 40)
                             ]

        self.enemy_units = [#Terrien(perso=perso3, x=6, y=6, health=80, team='enemy', attack_power=5, defense_power=4, agility_power=2, speed = 40),
                            #Archer(perso=perso1, x=7, y=6, health=80, team='enemy',  attack_power=2, defense_power=2, agility_power=1, speed = 70),
                            #Aerien(perso=perso2, x=7, y=7, health=100, team='enemy', attack_power=1, defense_power=5, agility_power=1, speed = 65),
                            Archer(perso=perso2, x=6, y=7, health=200, team='enemy', attack_power=4, defense_power=1, agility_power=2, speed = 60)
                            ]




#----------------------------------------


    def handle_player_turn(self):
        """
        #Tour du joueur
        """
        if len(self.player_units)!=0:
            for selected_unit in self.player_units:
    
                # Tant que l'unité n'a pas terminé son tour
                has_acted = False
                selected_unit.is_selected = True
                self.flip_display()
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
                                selected_unit.move(dx, dy)
                                print(f'il vous reste {selected_unit.nombre_deplacements - selected_unit.current_move} déplacements, pour cette unité')
                                self.flip_display()
    
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
    
                                has_acted = True
                                selected_unit.is_selected = False
                            
                            
                            

    def handle_enemy_turn(self):
        """
        #IA très simple pour les ennemis.
        """
        if len(self.enemy_units)!=0:
            for enemy in self.enemy_units:
    
                # Déplacement aléatoire
                target = random.choice(self.player_units)
                dx = 1 if enemy.x < target.x else -1 if enemy.x > target.x else 0
                dy = 1 if enemy.y < target.y else -1 if enemy.y > target.y else 0
                enemy.move(dx, dy)
    
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

    def flip_display(self):
        """
        #Affiche le jeu.
        """

        # Affiche la grille
        self.screen.fill(BLACK)
        for x in range(0, WIDTH, CELL_SIZE):
            for y in range(0, HEIGHT, CELL_SIZE):
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, WHITE, rect, 1)

        # Affiche les unités
        for unit in self.player_units + self.enemy_units:
            unit.draw(self.screen)

        # Rafraîchit l'écran
        pygame.display.flip()


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
        game.handle_enemy_turn()
        game.flip_display()
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
