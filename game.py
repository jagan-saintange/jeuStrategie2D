import pygame
import random
import sys
import time

from unit import *
from personnages import *
from ui import *

LEVEL = 3 #doit etre >1 ordre de grandeur des facultés débloquées : 1-3, mettre >3 fera réfléchir l'IA plus longtemps encore tho
        
# Initialisation de Pygame
pygame.init()

# Set up font
font = pygame.font.Font(".\\Fonts\\comic.ttf", 36)

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


    def handle_player_turn(self, game):
        """
        #Tour du joueur
        """
        if len(self.enemy_units)!=0 and len(self.player1_units)!=0: #ce if ne marche pas comme souhaité
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
                            if event.key == pygame.K_TAB:
                                game.toggle_inspect(selected_unit)
                                self.flip_display(selected_unit)
                        
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
                                        print(selected_unit.perso.nom)
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
                                        #running = self.test_fin()
                                        #if not running:
                                        #    break
    
                                has_acted = True
                                selected_unit.is_selected = False
                                self.flip_display(selected_unit)
                running = self.test_fin()
                if not running:
                    break
                                
                            
                            

    def handle_enemy_turn(self):
        """
        #IA très simple pour les ennemis.
        """
        
        print(len(self.enemy_units), len(self.player1_units))
        for enemy in self.enemy_units:
            if len(self.enemy_units)!=0 and len(self.player1_units)!=0:
                #self.flip_display(enemy)
                #time.sleep(0.5)
    
                # Déplacement aléatoire différencié selon le niveau de l'IA (normalement, l'intelligence de l'ia augmente de façon exponnentielle jusqu'à probablement atteindre un plafond, il faudrait étudier la fonction)
                target = random.choice(self.player1_units)
                for _ in range(LEVEL): #plus le niveau de l'IA sera grand, plus il aura le temps de réfléchir
                    if LEVEL > 1:
                        if target.comparateur_faiblesse_resistance(enemy)[1]: #si target a une résistance, il cherche encore
                           target = random.choice(self.player1_units)
                    if LEVEL > 2: #si niveau superieur à 2
                        if not target.comparateur_faiblesse_resistance(enemy)[0]: #si target n'a pas de faiblesse, il cherche encore
                            target = random.choice(self.player1_units)
                    #niveau sup où il garde en mémoire un target pour toute la partie, cette fois en estimant le meilleur enemy dans la liste des joueurs?
                    #ou alors algo d'optimisation. Minimisation entre le chemin le plus court vers l'ennemi et rester hors de portée d'une attaque directe si enemy ne peut pas attaquer dans le meme tour 
                    #ou alors algo pour prendre en compte la proba de se faire tuer par un target spécifique au prochain tour, enemy fuit l'adversaire si c'est le cas
                    #vu qu'on a déjà un projet en optimisation, on ne va pas creuser plus loin :)
                    #par ailleurs toutes les fonctions qui ont été créées (je pense notamment pour le calcul des dégats, pourraient être étudiés graphiquement avec matplotlib, j'essairai de plot au moins 1 si j'ai le temps ( pour certains, ça ferait une fonction 2 entrées 1 sortie, avec des isovaleurs représentables; par exemple Unit().ponderation))
                    #on pourrait alors ajuster les valeurs de stats d'attaque et de défense plus précisément en connaissant la forme de Unit().pondération 
                
                enemy.current_move = 0
                essai = 0 #essai = 0 si le move est successful, si le move rate :  essai = 1. 0 et 1 sont aussi des bools  reconnus
                
                while enemy.current_move < enemy.nombre_deplacements:
                    
                    if essai : #tentatives suivante si le essai de else n'a pas fonctionné
                        if abs(enemy.x - target.x) <= 1 and abs(enemy.y - target.y) <= 1:
                            break #si l'ennemi est portée, plus besoin de se déplacer
                        else:
                            #for _ in range(LEVEL):
                            dx, dy =0, 0
                            while abs(dx+ dy)!=1:
                                dx = random.randint(-1, 1)
                                dy = random.randint(-1, 1)
                            print('boop')
                            essai = enemy.move(dx, dy, self.enemy_units, self.player1_units) #mouvement aléatoire pour essayer de se débloquer
                            if essai :
                                break #si rien ne marche on ne bloque pas la partie
                                print('bip')
                
                    else:   # l'algo appliquera ce else en premier      
                    
                        
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
                
            running = self.test_fin()
            if not running:
                break             
                            
                
    

    def flip_display(self, selected_unit=False):
        """
        #Affiche le jeu.
        """

        # Affiche la grille
        self.screen.fill(BLACK)
        for x in range(box_width+ DECALAGE*2, GRID_WIDTH+box_width+DECALAGE, CELL_SIZE):
            for y in range(DECALAGE, GRID_HEIGHT+DECALAGE, CELL_SIZE):
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, WHITE, rect, 1)

       
        units = self.player1_units + self.enemy_units
        # Affiche les unités
        for unit in units:
            unit.draw(self.screen, units)
            
        #CURSEUR DE sélection
        if selected_unit != False:
            pygame.draw.rect(self.screen, GREEN, (selected_unit.x * CELL_SIZE  + X_DEC, selected_unit.y * CELL_SIZE + Y_DEC, CELL_SIZE, CELL_SIZE), 3)
            
            self.draw_info_box(self.screen, selected_unit, box_rect)
            #print('boop')
        
            

        # Rafraîchit l'écran
        pygame.display.flip()
        
    def test_fin(self):
        if len(self.player1_units) == 0 or len(self.enemy_units) == 0:
            return False
        else:
            return True
        
        
    def toggle_inspect(self, selected_unit):
        pygame.display.flip() 
        # Initialize movement deltas
        dx, dy = 0, 0
    
        # Important: this loop handles Pygame events
        while True:  # Keep this loop running until the inspection is exited
        
            # Affiche la grille
            self.screen.fill(BLACK)
            for x in range(box_width+ DECALAGE*2, GRID_WIDTH+box_width+DECALAGE, CELL_SIZE):
                for y in range(DECALAGE, GRID_HEIGHT+DECALAGE, CELL_SIZE):
                    rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(self.screen, WHITE, rect, 1)
            
        
            #self.flip_display(selected_unit)
            for event in pygame.event.get():
                # Handle quitting the game
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
    
                
                units = self.player1_units + self.enemy_units
                # Affiche les unités
                for unit in units:
                    unit.draw(self.screen, units)
                
    
                # Handle keyboard events
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        return  # Exit the inspection mode
                    

                   
                   
                    
                    pygame.display.flip()
                    
                    # Movement controls
                    if event.key == pygame.K_LEFT:
                        dx -= 1
                    elif event.key == pygame.K_RIGHT:
                        dx += 1
                    elif event.key == pygame.K_UP:
                        dy -= 1
                    elif event.key == pygame.K_DOWN:
                        dy += 1
    
            # Calculate the new position
            new_x = selected_unit.x + dx
            new_y = selected_unit.y + dy

            # Ensure the new position is within bounds (optional)
            if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:  # Replace with your grid dimensions
                # Clear the previous selection (optional)
                self.screen.fill((0, 0, 0))  # Clear the screen or redraw the background

                # Draw the selection rectangle
                pygame.draw.rect(self.screen, BLUE, (new_x * CELL_SIZE + X_DEC, new_y * CELL_SIZE + Y_DEC, CELL_SIZE, CELL_SIZE), 3)

                # Check for units at the new position
                for unit in self.player1_units + self.enemy_units:
                    if unit.x == new_x and unit.y == new_y:
                        self.draw_info_box(self.screen, unit, box_rect)
                        unit.draw(self.screen, self.player1_units + self.enemy_units)
                        
            
    
            # Update the display
            pygame.display.flip()  # Refresh the screen to show changes


    
    def draw_info_box(self, screen, unit, box_rect):
        # Draw the box
        
        # Determine the color based on the unit's team
        color = BLUE if unit.team == 'player1' else RED
        color = int(color[0]/1.5), int(color[1]/1.5), int(color[2]/1.5)
        
        # Draw the box rectangle
        box = pygame.draw.rect(screen, color, box_rect)
        
        adjusted_box_rect = box_rect.move(CELL_SIZE + X_DEC, CELL_SIZE + Y_DEC)

            # Check if the unit has an icon and draw it
        if unit.perso.icon is not None:
            icon_scaled = pygame.transform.scale(unit.perso.icon, (CELL_SIZE*2, CELL_SIZE*2))
            screen.blit(icon_scaled, (box_rect.x + 10, box_rect.y + 10))  # Position the icon inside the box
    
        # Prepare the text to display
        health_text = f"PdV: {unit.health}/{unit.maxhealth}"
        attack_text = f"Attack: {unit.attack_power}"
        defense_text = f"Defense: {unit.defense_power}"
        agility_text = f'Agility: {unit.agility_power}'
        speed_text = f'Speed: {unit.speed}'
        nature_text =f'Nature: {unit.perso.de_nature}'
        type_text ='perso de type: {unit.perso.de_type}'
        
        
        # Render the text surfaces
        health_surface = font.render(health_text, True, BLACK)
        attack_surface = font.render(attack_text, True, BLACK)
        defense_surface = font.render(defense_text, True, BLACK)
        agility_surface = font.render(agility_text, True, BLACK)
        speed_surface = font.render(speed_text, True, BLACK)
        nature_surface = font.render(type_text, True, BLACK)
        type_surface = font.render(type_text, True, BLACK)
        
        
        
        # Draw the text on the box
        screen.blit(health_surface, (box_rect.x + 10, box_rect.y + 10 + CELL_SIZE*2))
        screen.blit(attack_surface, (box_rect.x + 10, box_rect.y + 10 + CELL_SIZE*3))  # Below the icon
        screen.blit(defense_surface, (box_rect.x + 10, box_rect.y + 10 + CELL_SIZE *4))  # Below the attack text
        screen.blit(agility_surface, (box_rect.x + 10, box_rect.y + 10 + CELL_SIZE *5)) 
        screen.blit(speed_surface, (box_rect.x + 10, box_rect.y + 10 + CELL_SIZE *6)) 
        screen.blit(nature_surface, (box_rect.x + 10, box_rect.y + 10 + CELL_SIZE *8)) 
        screen.blit(type_surface, (box_rect.x + 10, box_rect.y + 10 + CELL_SIZE *9))

def main():
    
    #menu type console ui pour paramétrer le combat
    ui=Ui()
    player1_units, enemy_units = ui.run_ui()
    print('chargement du jeu...')
    time.sleep(1)



    # Instanciation de la fenêtre
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mon jeu de stratégie")

    # Instanciation du jeu
    game = Game(screen, player1_units, enemy_units)


    running = True    
    
    while running:
        game.handle_player_turn(game)
        running = game.test_fin()
        if not running:
            break
        game.handle_enemy_turn()
        running = game.test_fin()
        if not running:
            break
        #if len(game.player1_units) == 0 or len(game.enemy_units) == 0: 
        #    running = False
            
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