import pygame
import random
import sys
import time
from ui import *
from abilities import *

LEVEL = 3 #doit etre > 1 ordre de grandeur des facultés débloquées : 1-3, mettre > 3 fera réfléchir l'IA plus longtemps encore tho

class Game: # Classe pour représenter le jeu
    def __init__(self, screen, player_units, enemy_units):
        self.screen = screen # Écran sur lequel le jeu sera affiché
        self.player_units = player_units # Liste des unités contrôlées par le joueur
        self.enemy_units = enemy_units # Liste des unités contrôlées par "l'ordinateur"
        self.messages = [] # Liste des messages à afficher dans l'interface (actions, compétences, etc.)
        # Initialisation des compétences (chacune étant une instance de classe)
        self.competences = [Poison(), PluieDeProjectiles(), Missile(), Drain(), Soin(), Bouclier(), Paralysie(), Desarmement(), Vortex(), Teleportation()]
        self.competences_utilisees = set() # Suivi des compétences utilisées (utilisation d'un set, car plus rapide pour la recherche d'éléments)
        self.interface = Interface(self.screen, self) # Instance de la classe Interface pour les interactions

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#

    def flip_display(self): # Mise à jour de l'affichage en utilisant l'interface graphique
        self.screen.blit(self.interface.background, (0, 0)) # Arrière-plan

        for unit in self.player_units + self.enemy_units: # Unités (alliées et ennemies)
            unit.draw_unit(self.screen)

        self.interface.draw_foreground() # Objets au premier plan (arbre, sapin, tente, etc.)
        self.screen.blit(self.interface.foreground_surface, (0, 0))
        self.interface.draw_grid() # Grille semi-transparente (pour délimiter les cellules)
        self.screen.blit(self.interface.grid_surface, (0, 0))
        
        selected_unit = next((unit for unit in self.player_units + self.enemy_units if unit.is_selected), None)
        image_path = selected_unit.image_path if selected_unit else None

        # Afficher l'interface pour l'unité sélectionnée
        self.interface.afficher_interface([], self.messages, image_path)
        pygame.display.flip() # Mise à jour de l'écran    

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#

    def handle_player_turn(self):
        """Tour du joueur"""
        for selected_unit in self.player_units:
            has_acted = False # Indique si l'utilisateur a agi pendant ce tour
            selected_unit.is_selected = True # Indique si l'utilisateur est sélectionnée
            self.flip_display() # Mise à jour de l'affichage

            # Étape 1 : Déplacement de l'unité
            max_deplacements = selected_unit.nombre_deplacements # Déplacements totaux de l'unité (calculés en fonction de sa vitesse)
            self.interface.ajouter_message(f"À toi de jouer, {selected_unit.perso.nom} ! Déplacements totaux : {max_deplacements}")
            while max_deplacements > 0: # Tant que l'unité n'a pas fini de se déplacer
                self.flip_display() # Mise à jour de l'affichage
                for event in pygame.event.get(): # Parcours des événements capturés par pygame (clavier, souris, fermeture de fenêtre, etc.)
                    if event.type == pygame.QUIT: # Dans le cas où l'utilisateur ferme la fenêtre du jeu
                        pygame.quit() # Fermeture de Pygame proprement
                        exit() # Arrêt complet du programme
                    if event.type == pygame.KEYDOWN:
                        dx, dy = 0, 0 # Initialisation des décalages dx et dy à 0
                        if event.key == pygame.K_LEFT:
                            dx = -1 # Déplacement d'une case vers la gauche (colonne précédente)
                        elif event.key == pygame.K_RIGHT:
                            dx = 1 # Déplacement d'une case vers la droite (colonne suivante)
                        elif event.key == pygame.K_UP:
                            dy = -1 # Déplacement d'une case vers le haut (ligne précédente)
                        elif event.key == pygame.K_DOWN:
                            dy = 1 # Déplacement d'une case vers le bas (ligne suivante)

                        if dx != 0 or dy != 0: # Dans le cas où un déplacement est demandé
                            new_colonne = selected_unit.x + dx # Calcul de la nouvelle colonne après que le déplacement ait été effectué
                            new_ligne = selected_unit.y + dy # Calcul de la nouvelle ligne après que le déplacement ait été effectué
                            # On s'assure de rester dans les limites de la grille et d'accéder à une case dite "passable"
                            if 0 <= new_ligne < GRID_SIZE and 0 <= new_colonne < GRID_SIZE and self.interface.passable(new_ligne, new_colonne):
                                moved = selected_unit.move(dx, dy, self.player_units, self.enemy_units) # Déplacement de l'unité
                                if moved: # Dans le cas où l'unité a bougé
                                    max_deplacements -= 1 # Réduction du nombre de déplacements restants
                                    self.interface.ajouter_message(f"Déplacements restants : {max_deplacements}")
                                else:
                                    self.interface.ajouter_message("Déplacement invalide. Prenez une autre direction.")
                            else:
                                self.interface.ajouter_message("Zone bloquée. Prenez une autre direction.")
                        break

            # Étape 2 : Transition vers le choix attaque/compétence
            if max_deplacements == 0: # Dans le cas où l'utilisateur a épuisé tous ses déplacements
                self.interface.ajouter_message("Souhaitez-vous attaquer directement (touche espace) ou utiliser une compétence (touche c) ?")
                self.flip_display() # Mise à jour de l'affichage

            # Étape 3 : Choix entre attaque directe ou compétence
            while not has_acted: # Tant que l'utilisateur n'a pas agi
                self.flip_display() # Mise à jour de l'affichage
                for event in pygame.event.get(): # Parcours des événements capturés par pygame (clavier, souris, fermeture de fenêtre, etc.)
                    if event.type == pygame.QUIT: # Dans le cas où l'utilisateur ferme la fenêtre du jeu
                        pygame.quit() # Fermeture de Pygame proprement
                        exit() # Arrêt complet du programme
                    if event.type == pygame.KEYDOWN: # Dans le cas où une touche du clavier a été enfoncée
                        if event.key == pygame.K_SPACE: # S'il s'agit de la touche "Espace" (choix de l'attaque directe)
                            self.interface.ajouter_message("Vous avez choisi d'attaquer directement. Veuillez sélectionner une cible.")
                            self.flip_display() # Mise à jour de l'affichage

                            # Sélection de la cible
                            cible_x, cible_y = selected_unit.x, selected_unit.y # Initialisation des coordonnées de la cible (sur la position de l'utilisateur)
                            selecting_target = True # Indique si la cible a été sélectionné
                            while selecting_target: # Boucle qui tourne tant que l'utilisateur n'a pas validé la sélection de sa cible
                                self.flip_display() # Mise à jour de l'affichage
                                rect = pygame.Rect(cible_x * CELL_SIZE, cible_y * CELL_SIZE, CELL_SIZE, CELL_SIZE) # Curseur de sélection
                                pygame.draw.rect(self.screen, (255, 255, 0), rect, 3) # Rectangle de couleur jaune (255, 255, 0) qui correspond au curseur de sélection
                                pygame.display.update() # Affichage des modifications à l'écran

                                for target_event in pygame.event.get(): # Parcours des événements capturés par pygame (clavier, souris, fermeture de fenêtre, etc.)
                                    if target_event.type == pygame.QUIT: # Dans le cas où l'utilisateur ferme la fenêtre du jeu
                                        pygame.quit() # Fermeture de Pygame proprement
                                        exit() # Arrêt complet du programme
                                    if target_event.type == pygame.KEYDOWN: # Dans le cas où une touche du clavier a été enfoncée
                                        if target_event.key == pygame.K_LEFT: # Déplacement du curseur vers la gauche (décrémentation de cible_x)
                                            cible_x = max(0, cible_x - 1) # On utilise max(0, cible_x - 1) pour rester dans les limites de la grille
                                        elif target_event.key == pygame.K_RIGHT: # Déplacement du curseur vers la gauche (incrémentation de cible_x)
                                            cible_x = min(GRID_SIZE - 1, cible_x + 1) # On utilise min(GRID_SIZE - 1, cible_x + 1) pour rester dans les limites de la grille
                                        elif target_event.key == pygame.K_UP: # Déplacement du curseur vers le haut (décrémentation de cible_y)
                                            cible_y = max(0, cible_y - 1) # On utilise max(0, cible_y - 1) pour rester dans les limites de la grille
                                        elif target_event.key == pygame.K_DOWN: # Déplacement du curseur vers le bas (incrémentation de cible_y)
                                            cible_y = min(GRID_SIZE - 1, cible_y + 1) # On utilise min(GRID_SIZE - 1, cible_y + 1) pour rester dans les limites de la grille
                                        elif target_event.key == pygame.K_RETURN: # Dans le cas où l'utilisateur presse la touche "Entrée"
                                            selecting_target = False # Validation de la cible, arrêt de la boucle de sélection

                            # On retourne l'ennemi situé aux coordonnées (cible_x, cible_y) (None s'il n'y en a pas)
                            cible = next((enemy for enemy in self.enemy_units if enemy.x == cible_x and enemy.y == cible_y), None)
                            if cible: # Dans le cas où une cible ennemie valide a été trouvée
                                if abs(selected_unit.x - cible_x) + abs(selected_unit.y - cible_y) == 1: # Si elle est à portée (à 1 case de distance de l'utilisateur)
                                    selected_unit.attack(cible, 30) # Dégâts bruts = 30 avant l'ajustement (en fonction de l'attaque/défense/agilité des partis impliqués)
                                    self.interface.ajouter_message(f"{selected_unit.perso.nom} attaque {cible.perso.nom} ({cible.HPloss(30, selected_unit)} PdV).")
                                    if cible.health <= 0: # Dans le cas où la cible n'a plus de PdV après l'attaque
                                        self.enemy_units.remove(cible) # On la supprime des unités ennemies
                                    has_acted = True # Indique que l'utilisateur a agi
                                else: # Si la cible n'est pas à portée
                                    self.interface.ajouter_message("La cible n'est pas à votre portée.")
                                    has_acted = True # Indique que l'utilisateur a agi
                            else: # Si aucune cible n'a été trouvée aux coordonnées spécifiées
                                self.interface.ajouter_message("Aucune cible sélectionnée.")
                                has_acted = True # Indique que l'utilisateur a agi

                        # Gestion de la sélection d'une compétence
                        elif event.key == pygame.K_c: # S'il s'agit de la touche "C" (choix d'une compétence)
                            competence_choisie = Competence.selectionner_competence(self, selected_unit)
                            if competence_choisie:
                                cible = Competence.selectionner_cible(selected_unit, self, competence_choisie)
                                if cible:
                                    Competence.utiliser_competence(selected_unit, cible, competence_choisie, self, self.interface)
                                    selected_unit.competences_utilisees.add(competence_choisie.nom)
                            has_acted = True # Indique que l'utilisateur a agi
                selected_unit.is_selected = False

                # Nettoyage des unités mortes:
                self.player_units = [unit for unit in self.player_units if unit.health > 0]
                self.enemy_units = [unit for unit in self.enemy_units if unit.health > 0]

                # Vérification des conditions de victoire/défaite:
                if not self.player_units: # S'il ne reste plus d'unités alliées vivantes
                    self.interface.ajouter_message("Défaite ! Toutes vos unités ont été éliminées.")
                    pygame.quit() # Fermeture de Pygame proprement
                    exit() # Arrêt complet du programme
                elif not self.enemy_units: # S'il ne reste plus d'unités ennemies vivantes
                    self.interface.ajouter_message("Victoire ! Tous les ennemis ont été éliminés.")
                    pygame.quit() # Fermeture de Pygame proprement
                    exit() # Arrêt complet du programme

#-----------------------------------------------------------------------------------------------------------------------------------------------------------#

    def handle_enemy_turn(self):
        """IA pour les ennemis."""
        for enemy in self.enemy_units:
            for effet in enemy.effects[:]:
                if effet["effet"] == "poison":
                    enemy.attack(dommage = effet["dommages"]) # Applique les dégâts du poison
                effet["duree"] -= 1 # Réduit la durée de l'effet
                if effet["duree"] <= 0:
                    self.interface.ajouter_message(f"{enemy.perso.nom} n'est plus affecté par {effet['effet']}.")
                    enemy.effects.remove(effet) # Supprime l'effet expiré
            # Vérifie si l'ennemi est immobilisé (paralysie)
            if any(effet["effet"] == "immobilisé" for effet in enemy.effects):
                self.interface.ajouter_message(f"{enemy.perso.nom} est paralysé. L'unité ne peut donc pas se déplacer durant ce tour.")
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
            self.interface.ajouter_message(f"{enemy.perso.nom} s'est déplacé en ({enemy.x}, {enemy.y}).")

            # Gestion des attaques:
            if abs(enemy.x - target.x) <= 1 and abs(enemy.y - target.y) <= 1:
                if any(effet["effet"] == "désarmé" for effet in enemy.effects): # Dans le cas où l'ennemi est désarmé
                    self.interface.ajouter_message(f"{enemy.perso.nom} est désarmé.")
                    continue # Passe au prochain ennemi
                elif any(effet["effet"] == "bouclier" for effet in target.effects): # Dans le cas où la cible est protégé par un bouclier
                    self.interface.ajouter_message(f"{enemy.perso.nom} tente d'attaquer {target.perso.nom}.")
                    self.interface.ajouter_message(f"{target.perso.nom} est protégé(e) par un bouclier ! Aucun dégât subi.")
                else:
                    enemy.attack(target, 30)
                    self.interface.ajouter_message(f"{enemy.perso.nom} attaque {target.perso.nom} ({target.HPloss(30, enemy)} PdV).")            
                if target.health <= 0:
                    self.player_units.remove(target)
        self.enemy_units = [enemy for enemy in self.enemy_units if enemy.health > 0] # Mise à jour de la liste des ennemis pour exclure ceux qui sont morts
        # On s'assure que la condition de fin de jeu n'est pas remplie (victoire ou défaite)
        if not self.player_units: # Si la liste des unités alliées (player_units) est vide
            self.interface.ajouter_message("Défaite ! Toutes vos unités ont été éliminées.")
            pygame.quit() # Fermeture de Pygame proprement
            exit() # Arrêt complet du programme
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