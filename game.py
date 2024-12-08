import pygame
import random
import sys
import time
from unit import *
from personnages import *
from ui import *
from abilities import *
from interface import Interface

LEVEL = 3 #doit etre > 1 ordre de grandeur des facultés débloquées : 1-3, mettre > 3 fera réfléchir l'IA plus longtemps encore tho

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

    def __init__(self, screen, player_units, enemy_units):
        """
        Construit le jeu avec la surface de la fenêtre.

        Paramètres
        ----------
        screen : pygame.Surface
            La surface de la fenêtre du jeu.
        """
        self.screen = screen
        self.interface = Interface(self.screen, self)
        #self.player_units = [Unit(0, 0, 100, 10, 'player', 0, interface = self.interface),     # Position (x = 0, y = 0), PdV intial = 100, puissance d'attaque = 10
        #                     Unit(1, 0, 100, 10, 'player', 1, interface = self.interface)]     # Position (x = 1, y = 0), PdV intial = 100, puissance d'attaque = 10
        #self.enemy_units = [Unit(6, 6, 100, 10, 'enemy', 0, interface = self.interface),       # Position (x = 6, y = 6), PdV intial = 100, puissance d'attaque = 8
        #                    Unit(7, 6, 100, 10, 'enemy', 1, interface = self.interface)]       # Position (x = 7, y = 6), PdV intial = 100, puissance d'attaque = 8
        self.player_units = player_units
        self.enemy_units = enemy_units 
        startposP1 = [(0,0), (1,0), (1,1), (0,1)]
        startposE = [(GRID_SIZE-1,GRID_SIZE-1), (GRID_SIZE-2,GRID_SIZE-1), (GRID_SIZE-2,GRID_SIZE-2), (GRID_SIZE-2,GRID_SIZE-1)]
        random.shuffle(startposP1)
        random.shuffle(startposE)

        self.player_row = 5
        self.player_col = 5
        self.messages = []
        
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

    def flip_display(self):
        """
        Met à jour l'affichage en utilisant l'interface graphique.
        """
        # Affichage du jeu
        self.interface.draw_interface(self.screen, self.player_row, self.player_col)

        # Affichage des unités (alliées et ennemies)
        for unit in self.player_units + self.enemy_units:
            self.interface.draw_unit(self.screen, unit)

        competences_disponibles = [c for c in self.competences if c.nom not in self.competences_utilisees]
        self.interface.afficher_interface(competences_disponibles, self.touches_competences, self.messages)
        pygame.display.flip() # Mise à jour de l'écran    

    def handle_player_turn(self):
        """Tour du joueur"""        
        for selected_unit in self.player_units:
            has_acted = False # Indicateur pour savoir si l'unité a agi ou non pendant ce tour
            for effet in selected_unit.effects[:]: # Gestion de la compétence "Poison" qui s'étend sur 2 tours
                if effet["effet"] == "poison":
                    selected_unit.attack(dommage=effet["dommages"]) # Dégâts infligés = -15 PdV
                effet["duree"] -= 1 # Réduit la durée de l'effet
                if effet["duree"] <= 0:
                    self.interface.ajouter_message(f"{selected_unit.team} unité à ({selected_unit.x}, {selected_unit.y}) n'est plus affectée par {effet['effet']}.")
                    selected_unit.effects.remove(effet) # Suppression de l'effet, une fois sa durée écoulée
            selected_unit.is_selected = True
            self.flip_display() # Mise à jour de l'affichage

            # Étape 1 : Déplacement de l'unité
            self.interface.ajouter_message(f"Déplacez l'unité : ({selected_unit.x}, {selected_unit.y})")
            max_deplacements = selected_unit.nombre_deplacements
            while max_deplacements > 0:
                self.flip_display() # Mise à jour de l'affichage
                for event in pygame.event.get(): # Gestion des évènements
                    if event.type == pygame.QUIT: # Dans le cas où l'utilisateur ferme la fenêtre du jeu
                        pygame.quit() # Fermeture de Pygame proprement
                        exit() # Arrêt complet du programme
                    if event.type == pygame.KEYDOWN: # Gestions de touches du clavier
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
                        
                        if dx != 0 or dy != 0: # Dans le cas où l'utilisateur tente de se déplacer
                            moved = selected_unit.move(dx, dy, self.player_units, self.enemy_units) # Si le déplacement aboutit
                            if moved:
                                max_deplacements -= 1
                                self.interface.ajouter_message(f"L'unité a été déplacée en ({selected_unit.x}, {selected_unit.y}). Déplacements restants : {max_deplacements}")
                            else:
                                self.interface.ajouter_message("Déplacement invalide. Prenez une autre direction.")
                        break

            # Étape 2 : Transition vers le choix attaque/compétence
            if max_deplacements == 0: # Dans le cas où le déplacement a été effectué
                self.interface.ajouter_message("Veuillez choisir entre attaque directe et compétence.")
                self.flip_display() # Mise à jour de l'affichage

            # Étape 3 : Choix entre l'utilisation d'une compétence ou l'attaque directe
            while not has_acted: # Tant que l'unité n'a pas agi, on répète la boucle pour permettre la sélection d'une compétence
                for event in pygame.event.get(): # Gestion des évènements
                    if event.type == pygame.QUIT: # Dans le cas où l'utilisateur ferme la fenêtre du jeu
                        pygame.quit() # Fermeture de Pygame proprement
                        exit() # Arrêt complet du programme
                    if event.type == pygame.KEYDOWN: # Gestion des touches du clavier
                        if event.key == pygame.K_SPACE: # Touche "Espace" implique le choix d'une attaque directe
                            cible = next((enemy for enemy in self.enemy_units if abs(enemy.x - selected_unit.x) + abs(enemy.y - selected_unit.y) == 1), None)
                            if cible:
                                selected_unit.attack(cible)
                                self.interface.ajouter_message(f"L'unité {selected_unit.perso.nom} attaque l'ennemi à ({cible.x}, {cible.y}).")
                                if cible.health <= 0:
                                    self.enemy_units.remove(cible)
                            else:
                                self.interface.ajouter_message("L'attaque a échoué. Aucun ennemi à votre portée.")
                            has_acted = True
                        else: # Dans le cas du choix d'une compétence
                            competence = Competence.selectionner_competence(
                                self.interface, self.screen, self.competences, self.touches_competences, self.competences_utilisees
                            )
                            if competence:
                                cible = Competence.selectionner_cible(selected_unit, self, competence)
                                if cible:
                                    Competence.utiliser_competence(selected_unit, cible, competence, self, self.interface)
                                    self.competences_utilisees.add(competence.nom)
                                    if len(self.competences_utilisees) == len(self.competences):
                                        self.interface.ajouter_message("Toutes les compétences ont été utilisées. Recharge des compétences...")
                                        self.competences_utilisees.clear()
                                has_acted = True
                self.flip_display() # Mise à jour de l'affichage
            selected_unit.is_selected = False
            self.player_units = [unit for unit in self.player_units if unit.health > 0]
            self.enemy_units = [unit for unit in self.enemy_units if unit.health > 0]
            if not self.player_units:
                self.interface.ajouter_message("Défaite ! Toutes vos unités ont été éliminées.")
                pygame.quit()
                exit()
            elif not self.enemy_units:
                self.interface.ajouter_message("Victoire ! Tous les ennemis ont été éliminés.")
                pygame.quit()
                exit()

    def handle_enemy_turn(self):
        """IA pour les ennemis."""
        for enemy in self.enemy_units:
            for effet in enemy.effects[:]:
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
            
            if len(self.enemy_units) != 0 and len(self.player_units) != 0:
            # Déplacement aléatoire différencié selon le niveau de l'IA (normalement, l'intelligence de l'ia augmente de façon exponnentielle jusqu'à probablement atteindre un plafond, il faudrait étudier la fonction)
                target = random.choice(self.player_units)
                for _ in range(LEVEL): #plus le niveau de l'IA sera grand, plus il aura le temps de réfléchir
                    if LEVEL > 1:
                        if target.comparateur_faiblesse_resistance(enemy)[1]: #si target a une résistance, il cherche encore
                           target = random.choice(self.player_units)
                    if LEVEL > 2: #si niveau superieur à 2
                        if not target.comparateur_faiblesse_resistance(enemy)[0]: #si target n'a pas de faiblesse, il cherche encore
                            target = random.choice(self.player_units)
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
                            for _ in range(LEVEL):
                                dx, dy =0, 0
                                while abs(dx+ dy)!=1:
                                    dx = random.randint(-1, 1)
                                    dy = random.randint(-1, 1)
                                essai = enemy.move(dx, dy, self.enemy_units, self.player_units) #mouvement aléatoire pour essayer de se débloquer
                                if essai :
                                    break #si rien ne marche on ne bloque pas la partie
                
                    else:   # l'algo appliquera ce else en premier      
                    
                        #on input l'ess
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
                        essai = enemy.move(dx, dy, self.enemy_units, self.player_units)
                        self.flip_display()
                        time.sleep(0.3)
                        #print(enemy.current_move)
                    
                enemy.current_move = 0
            self.interface.ajouter_message(f"L'unité a été déplacée à ({enemy.x}, {enemy.y}).")

            # Vérifie si l'ennemi est désarmé (ne peut pas attaquer)
            if any(effet["effet"] == "désarmé" for effet in enemy.effects):
                self.interface.ajouter_message(f"{enemy.team} unité à ({enemy.x}, {enemy.y}) est désarmée.")
                continue # Passe au prochain ennemi
            # Attaque si possible
            if abs(enemy.x - target.x) <= 1 and abs(enemy.y - target.y) <= 1:
                enemy.attack(target)
                if target.health <= 0:
                    self.player_units.remove(target)
        self.enemy_units = [enemy for enemy in self.enemy_units if enemy.health > 0] # Mise à jour de la liste des ennemis pour exclure ceux qui sont morts
        if not self.player_units: # Si la liste des unités alliées (player_units) est vide
            self.interface.ajouter_message("Défaite ! Toutes vos unités ont été éliminées.")
            pygame.quit() # Fermeture de Pygame proprement
            exit() # Arrêt complet du programme # On vérifie si le jeu est terminé après que l'unité ait agi
        elif not self.enemy_units: # Si la liste des unités ennemies (enemy_units) est vide
            self.interface.ajouter_message("Victoire ! Tous les ennemis ont été éliminés.")
            pygame.quit() # Fermeture de Pygame proprement
            exit() # Arrêt complet du programme # On s'assure que la condition de fin de jeu n'est pas remplie (victoire ou défaite)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#

def main():
    ui = Ui()
    player_units, enemy_units = ui.run_ui()
    print('chargement du jeu...')
    time.sleep(1)
    # Initialisation de Pygame
    pygame.init()
    # Instanciation de la fenêtre
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mon jeu de stratégie")
    # Instanciation du jeu
    game = Game(screen, player_units, enemy_units)
    # Boucle principale du jeu
    while True:
        for event in pygame.event.get(): # Gestion des évènements
            if event.type == pygame.QUIT: # Dans le cas où l'utilisateur ferme la fenêtre du jeu
                pygame.quit() # Fermeture de Pygame proprement
                exit() # Arrêt complet du programme

        game.handle_player_turn()
        game.handle_enemy_turn()

if __name__ == "__main__":
    main()