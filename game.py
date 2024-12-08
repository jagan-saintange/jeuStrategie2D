import pygame
import random
import sys
import time

from unit import *
from personnages import *
from ui import *
from interface import Interface
from abilities import *

LEVEL = 3 #doit etre >1 ordre de grandeur des facultés débloquées : 1-3, mettre >3 fera réfléchir l'IA plus longtemps encore tho

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
        self.interface = Interface(self.screen, self)
        for i in self.player1_units+self.enemy_units:
            i.interface = self.interface
        ############################################
        
        self.player_row = 5
        self.player_col = 5
        self.messages = []
        
        startposP1 = [(0,0), (1,0), (1,1), (0,1)]
        startposE = [(GRID_SIZE-1,GRID_SIZE-1), (GRID_SIZE-2,GRID_SIZE-1), (GRID_SIZE-2,GRID_SIZE-2), (GRID_SIZE-2,GRID_SIZE-1)]
        random.shuffle(startposP1)
        random.shuffle(startposE)


# Initialisation des compétences
        self.competences = [Poison(),
                            PluieDeProjectiles(),
                            Missile(),
                            Drain(),
                            Soin(),
                            Bouclier(),
                            Paralysie(),
                            Desarmement(), 
                            Vortex(),   
                            Teleportation()]
        # Attribution de chaque compétence à une touche du clavier (A, Z, E, R, T, Y, U, I, O, P)
        self.touches_competences = {"Poison": pygame.K_a,
                                    "Pluie de projectiles": pygame.K_z,
                                    "Missile": pygame.K_e,
                                    "Drain": pygame.K_r,
                                    "Soin": pygame.K_t,
                                    "Bouclier": pygame.K_y,
                                    "Paralysie": pygame.K_u,
                                    "Désarmement": pygame.K_i,
                                    "Vortex": pygame.K_o,
                                    "Téléportation": pygame.K_p}

        self.competences_utilisees = set() # Suivi des compétences utilisées

#----------------------------------------

    def handle_player_turn(self):
        """
        #Tour du joueur
        """
        if len(self.enemy_units)!=0 and len(self.player1_units)!=0: #ce if ne marche pas comme souhaité
            for selected_unit in self.player1_units:
                if selected_unit.team == 'player1':
                    self.interface.ajouter_message("Tour du joueur 1 --------------------------")
                elif selected_unit.team == 'enemy':
                    self.interface.ajouter_message("Tour du joueur 2 --------------------------")
                
                has_acted = False # Indicateur pour savoir si l'unité a agi ou non pendant ce tour
                for effet in selected_unit.effects[:]: # Gestion de "Poison" qui s'étend sur 2 tours
                    if effet["effet"] == "poison":
                        selected_unit.attack(dommage = effet["dommages"]) # Dégats infligés = -15 PdV
                    effet["duree"] -= 1 # Réduit la durée de l'effet
                    if effet["duree"] <= 0:
                        self.interface.ajouter_message(f"{selected_unit.team} unité à ({selected_unit.x}, {selected_unit.y}) n'est plus affectée par {effet['effet']}.")
                        selected_unit.effects.remove(effet) # Suppression de l'effet, une fois sa durée écoulée
                selected_unit.is_selected = True
                self.flip_display()
                
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
                                immobilise = False
                                for effet in selected_unit.effects[:]:
                                    if effet["effet"] == "immobilisé":
                                        immobilise = True
                                if immobilise: # Si l'effet "immobilisé" est actif
                                    self.interface.ajouter_message(f"{self.team} unité à ({self.x}, {self.y}) est paralysée et ne peut pas se déplacer.")
                                else:
                                    selected_unit.move(dx, dy, self.player1_units, self.enemy_units)
                                    self.interface.ajouter_message(f"L'unité a été déplacée en ({selected_unit.x}, {selected_unit.y}).\nIl vous reste {selected_unit.nombre_deplacements - selected_unit.current_move} déplacements, pour cette unité")
                                    print(f'il vous reste {selected_unit.nombre_deplacements - selected_unit.current_move} déplacements, pour cette unité')
                                
                                self.flip_display(selected_unit)
                                
                                
                                
                            # Attaque (touche espace) met fin au tour
                            self.interface.ajouter_message(f"Appuyez sur espace pour une attaque directe. Sinon appuyez sur entrer puis choisissez une compétence")
                            for event in pygame.event.get():
                                if event.key == pygame.K_SPACE:
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
                                            
                                elif event.key == pygame.K_KP_ENTER:
                                        # Étape 2 : Sélection et utilisation d'une compétence
                                    self.interface.ajouter_message(f"Sélectionnez une compétence pour l'unité : ({selected_unit.x}, {selected_unit.y})")
                                    while not has_acted: # Tant que l'unité n'a pas agi, on répète la boucle pour permettre la sélection et l'utilisation d'une compétence
                                        competence = self.selectionner_competence() # Appel de la fonction de sélection pour que le joueur choisisse une compétence disponible
                                        if competence: # Dans le cas où une compétence a été sélectionnée
                                            cible = self.selectionner_cible(selected_unit, competence) # Appel de la fonction de sélection pour que le joueur choisisse une cible qui subira la compétence
                                            if cible: # Dans le cas où une cible valide (unité ennemie) a été sélectionnée
                                                self.utiliser_competence(selected_unit, cible, competence, self.interface) # Utilisation de la compétence sélectionnée sur la cible choisie
                                                self.competences_utilisees.add(competence.nom) # Ajout du nom de la compétence utilisée à l'ensemble des compétences déjà utilisées
                                                if len(self.competences_utilisees) == len(self.competences): # On vérifie si toutes les compétences disponibles ont été utilisées
                                                    self.interface.ajouter_message("Toutes les compétences ont été utilisées. Recharge des compétences...")
                                                    self.competences_utilisees.clear() # Vide l'ensemble des compétences utilisées pour les rendre toutes disponibles à nouveau (nouveau cycle)

                                has_acted = True
                                selected_unit.is_selected = False
                                self.flip_display(selected_unit)
                running = self.test_fin()
                if not running:
                    break
                                
                            

    def handle_enemy_turn(self):
        """
        #IA pour les ennemis.
        """
        
        print(len(self.enemy_units), len(self.player1_units))
        for enemy in self.enemy_units:
            
            
            if effet["effet"] == "poison":
                enemy.attack(dommage = effet["dommages"])  # Applique les dégâts du poison
            effet["duree"] -= 1  # Réduit la durée de l'effet
            if effet["duree"] <= 0:
                self.interface.ajouter_message(f"{enemy.team} unité à ({enemy.x}, {enemy.y}) n'est plus affectée par {effet['effet']}.")
                enemy.effects.remove(effet)  # Supprime l'effet expiré
                
            # Vérifie si l'ennemi est immobilisé (paralysie)
            if any(effet["effet"] == "immobilisé" for effet in enemy.effects):
                self.interface.ajouter_message(f"{enemy.team} unité à ({enemy.x}, {enemy.y}) est paralysée et ne peut pas agir ce tour.")
                continue # Passe au prochain ennemi

            
            
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
                self.interface.ajouter_message(f"L'unité a été déplacée à ({enemy.x}, {enemy.y}).")
                # Vérifie si l'ennemi est désarmé (ne peut pas attaquer)
                if any(effet["effet"] == "désarmé" for effet in enemy.effects):
                    self.interface.ajouter_message(f"{enemy.team} unité à ({enemy.x}, {enemy.y}) est désarmée.")
                    continue # Passe au prochain ennemi
                
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

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#
# FONCTIONS RELATIVES AUX COMPÉTENCES:

    # Fonction permettant à l'utilisateur de sélectionner une compétence parmi celles qu'il n'a pas encore utilité
    def selectionner_competence(self):
        # Sélection des compétences parmi celles qui n'ont pas encore été utilisées dans ce cycle (un cycle dure 5 tours)
        competences_disponibles = [c for c in self.competences if c.nom not in self.competences_utilisees]
        self.interface.afficher_competences(self.screen, competences_disponibles) # Méthode qui met à jour l'affichage des compétences
        while True: # Boucle principale permettant de gérer la sélection du joueur
            for event in pygame.event.get(): # On parcourt les événements en attente
                if event.type == pygame.QUIT: # Dans le cas où l'utilisateur ferme la fenêtre du jeu
                    pygame.quit() # Fermeture de Pygame proprement
                    exit() # Arrêt complet du programme
                elif event.type == pygame.KEYDOWN: # Dans le cas où l'utilisateur presse une touche
                    competence = None # Variable dans laquelle on stockera la compétence sélectionnée parmi celles qui sont disponibles
                    for c in competences_disponibles: # On parcourt les compétences disponibles (celles affichées à l'écran)
                        if event.key == self.touches_competences.get(c.nom): # On s'assure que la touche pressée correspond à celle associée à la compétence
                            competence = c # Si une correspondance est vérifiée, alors cette compétence est attribuée à la variable "competence"
                            break # Aussitôt qu'une compétence valide a été trouvée, on sort de la boucle
                    if competence: # Dans le cas où une compétence valide est sélectionnée
                        return competence # Retourne la compétence sélectionnée pour qu'elle puisse être utilisée

    # Fonction permettant à l'utilisateur d'utiliser une compétence sur une cible (ou une position s'il s'agit des compétences Vortex et Téléportation)
    def utiliser_competence(self, utilisateur, cible, competence, interface):
        if competence and utilisateur and cible: # Dans le cas où la compétence peut être utilisée
            competence.utiliser(utilisateur, cible, self, self.interface) # On l'utilise
            if isinstance(cible, Unit) and cible.team == "enemy" and cible.health <= 0: # Dans le cas où la cible est une unité ennemie ET qu'elle n'a plus de PdV
                if cible in self.enemy_units:
                    self.enemy_units.remove(cible) # Suppression de la cible de la liste des ennemis
        else: # Dans le cas où la cible est une unité alliée
            self.interface.ajouter_message("Impossible d'utiliser la compétence. Vérifiez l'utilisateur, la cible et la compétence.")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#
# FONCTION RELATIVE AU CURSEUR (SÉLÉCTION DE CIBLE ET/OU DE CASE):

    def selectionner_cible(self, utilisateur, competence = None):
        curseur_x, curseur_y = utilisateur.x, utilisateur.y # Coordonnées du curseur initialisées avec les coordonnées actuelles de l'utilisateur
        if competence:
            if competence.nom in ["Soin", "Bouclier", "Téléportation"]: # S'il s'agit des compétences "Bouclier", "Soin" ou "Téléportation", pas de sélection extérieure
                return utilisateur
            elif competence.nom == "Missile": # Sélection d'une ligne de 5 cases (horizontale ou verticale) pour la compétence "Missile"
                direction = None # Variable dans laquelle on stocke la direction choisie par l'utilisateur
                curseur_positions = [] # Liste contenant les coordonnées (x, y) des 5 cases du curseur
                while True: # Boucle qui reste active jusqu'à ce que l'utilisateur choisisse une direction
                    self.flip_display() # Mise à jour de l'affichage
                    if direction: # Dans le cas où une direction (haut, bas, gauche, droite) a été choisie
                        for x, y in curseur_positions:
                            pygame.draw.rect(self.screen, (255, 0, 0), (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2) # Dessin du curseur (en rouge) qui représente la zone d'effet
                    else: # Dans le cas où aucune direction n'a été choisie
                        pygame.draw.rect(self.screen, GREEN, (curseur_x * CELL_SIZE, curseur_y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2) # Dessin d'un curseur (en vert) autour de l'utilisateur
                    pygame.display.flip() # Mise à jour de l'affichaget
                    for event in pygame.event.get(): # Gestion des évènements
                        if event.type == pygame.QUIT: # Dans le cas où l'utilisateur ferme la fenêtre du jeu
                            pygame.quit() # Fermeture de Pygame proprement
                            exit() # Arrêt complet du programme
                        elif event.type == pygame.KEYDOWN: # Gestion des touches du clavier
                            if event.key == pygame.K_UP: # Si la flèche du haut (touches fléchées) est pressée
                                direction = 'haut'
                            elif event.key == pygame.K_DOWN: # Si la flèche du bas (touches fléchées) est pressée
                                direction = 'bas'
                            elif event.key == pygame.K_LEFT: # Si la flèche gauche (touches fléchées) est pressée
                                direction = 'gauche'
                            elif event.key == pygame.K_RIGHT: # Si la flèche droite (touches fléchées) est pressée
                                direction = 'droite'
                            elif event.key == pygame.K_RETURN and direction: # Validation en pressant "Entrée"
                                return direction
                            
            elif competence.nom == "Pluie de projectiles": # Sélection d'une matrice 3x3 pour la compétence "Pluie de projectiles"
                while True: # Boucle qui reste active jusqu'à ce que l'utilisateur choisisse une case (centre de la matrice)
                    self.flip_display() # Mise à jour de l'affichage
                    for dx in range(-1, 2): # Parcourt les déplacements horizontaux par rapport à la case centrale
                        for dy in range(-1, 2): # Parcourt les déplacements verticaux par rapport à la case centrale
                            if 0 <= curseur_x + dx < GRID_SIZE and 0 <= curseur_y + dy < GRID_SIZE: # On s'assure que la case centrale (calculée en combinant ses coordonnées avec les déplacements dx et dy) ne dépassent pas les bordures de la grille
                                pygame.draw.rect(self.screen, (128, 0, 128), ((curseur_x + dx) * CELL_SIZE, (curseur_y + dy) * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2) # Dessin d'un carré (matrice 3x3) qui représente la zone d'effet
                    pygame.display.flip() # Affichage des évènements à l'écran
                    for event in pygame.event.get(): # Gestion des évènements
                        if event.type == pygame.QUIT: # Dans le cas où l'utilisateur ferme la fenêtre du jeu
                            pygame.quit() # Fermeture de Pygame proprement
                            exit() # Arrêt complet du programme
                        elif event.type == pygame.KEYDOWN: # Gestion des touches du clavier
                            if event.key == pygame.K_LEFT: # Si la flèche gauche (touches fléchées) est pressée, le curseur se déplace à gauche
                                curseur_x = max(0, curseur_x - 1) # Restreint le curseur aux bordures de la grille (axes des abscisses)
                            elif event.key == pygame.K_RIGHT: # Si la flèche droite (touches fléchées) est pressée, le curseur se déplace à droite
                                curseur_x = min(GRID_SIZE - 1, curseur_x + 1) # Restreint le curseur aux bordures de la grille (axes des abscisses)
                            elif event.key == pygame.K_UP: # Si la flèche du haut (touches fléchées) est pressée, le curseur se déplace en haut
                                curseur_y = max(0, curseur_y - 1) # Restreint le curseur aux bordures de la grille (axes des ordonnées)
                            elif event.key == pygame.K_DOWN: # Si la flèche du bas (touches fléchées) est pressée, le curseur se déplace en bas
                                curseur_y = min(GRID_SIZE - 1, curseur_y + 1) # Restreint le curseur aux bordures de la grille (axes des ordonnées)
                            elif event.key == pygame.K_RETURN: # Validation en pressant "Entrée"
                                return Unit(curseur_x, curseur_y, 0, 0, 'neutral', None, interface = self.interface) # Dans le cas où aucune unité ennemie n'est trouvée, on retourne une position vide comme cible "neutre"

            while True: # Cas général (compétences sans zone d'effet)
                self.flip_display() # Mise à jour de l'affichage
                pygame.draw.rect(self.screen, GREEN, (curseur_x * CELL_SIZE, curseur_y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2) # Dessin du curseur habituel (en vert)
                pygame.display.flip() # Affichage des évènements à l'écran
                for event in pygame.event.get(): # Gestion des évènements
                    if event.type == pygame.QUIT: # Dans le cas où l'utilisateur ferme la fenêtre du jeu
                        pygame.quit() # Fermeture de Pygame proprement
                        exit() # Arrêt complet du programme
                    elif event.type == pygame.KEYDOWN: # Gestion des touches du clavier
                        if event.key == pygame.K_LEFT: # Si la flèche gauche (touches fléchées) est pressée, le curseur se déplace à gauche
                            curseur_x = max(0, curseur_x - 1) # Restreint le curseur aux bordures de la grille (axes des abscisses)
                        elif event.key == pygame.K_RIGHT: # Si la flèche droite (touches fléchées) est pressée, le curseur se déplace à droite
                            curseur_x = min(GRID_SIZE - 1, curseur_x + 1) # Restreint le curseur aux bordures de la grille (axes des abscisses)
                        elif event.key == pygame.K_UP: # Si la flèche du haut (touches fléchées) est pressée, le curseur se déplace en haut
                            curseur_y = max(0, curseur_y - 1) # Restreint le curseur aux bordures de la grille (axes des ordonnées)
                        elif event.key == pygame.K_DOWN: # Si la flèche du bas (touches fléchées) est pressée, le curseur se déplace en bas
                            curseur_y = min(GRID_SIZE - 1, curseur_y + 1) # Restreint le curseur aux bordures de la grille (axes des ordonnées)
                        elif event.key == pygame.K_RETURN: # Valide en pressant "Entrée"
                            for unit in self.enemy_units: # Parcourt les unités ennemies
                                if unit.x == curseur_x and unit.y == curseur_y: # Dans le cas où le curseur désigne une unité ennemie
                                    return unit # Retourne l'unité ennemie comme cible valide
                            return Unit(curseur_x, curseur_y, 0, 0, 'neutral', None, interface = self.interface)
                        elif event.key == pygame.K_ESCAPE: # Dans le cas où la touche "Échap" est pressée
                            return None

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
                

        # Affichage du jeu
        self.interface.draw_interface(self.screen, self.player_row, self.player_col)

        # Affichage des unités (alliées et ennemies)
        for unit in self.player1_units + self.enemy_units:
            self.interface.draw_unit(self.screen, unit)

        competences_disponibles = [c for c in self.competences if c.nom not in self.competences_utilisees]
        self.interface.afficher_interface(competences_disponibles, self.touches_competences, self.messages)
        pygame.display.flip() # Mise à jour de l'écran
        
            
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